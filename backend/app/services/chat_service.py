import json
import datetime
from typing import Generator, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.conversation import Conversation
from app.models.message import Message
from app.services.hybrid_router import HybridRouter
from app.services.conversation_service import ConversationService
from app.services.memory.summarizer import ConversationSummarizer
from app.utils.errors import ServiceUnavailableError

class ChatService:
    def __init__(self, session: Session, router: HybridRouter):
        self.session = session
        self.router = router
        self.conv_service = ConversationService(session)

    def process_message(
        self,
        message: str,
        session_id: str,
        conversation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Processes a chat message synchronously."""
        # Ensure conversation exists
        if conversation_id is None:
            conv = Conversation(session_id=session_id, title=message[:40] + ("..." if len(message) > 40 else ""))
            self.session.add(conv)
            self.session.commit()
            conversation_id = conv.id
        else:
            conv = self.conv_service.get_conversation(conversation_id, session_id)

        # Save user message
        user_msg = Message(
            conversation_id=conversation_id,
            role="user",
            content=message.strip(),
            response_type="user"
        )
        self.session.add(user_msg)
        self.session.commit()

        # Route query
        routed = self.router.route_and_prepare(message, session_id, conversation_id)
        citations = routed.get("citations", [])
        route_type = routed["route"]

        if routed["direct_response"] is not None:
            reply_text = routed["direct_response"]
        else:
            # Generate via LLM
            messages_for_llm = routed["messages_for_llm"]
            try:
                reply_text = self.router.llm_provider.generate(messages_for_llm)
            except ServiceUnavailableError as e:
                reply_text = (
                    "⚠️ Notice: The local LLM (Ollama) is currently unreachable or offline. "
                    "However, rule-based FAQs and indexed university pages are operational. "
                    "Please verify that Ollama is started with `ollama serve` and the model is downloaded."
                )
                route_type = "error"

        # Save assistant message
        asst_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=reply_text,
            response_type=route_type
        )
        asst_msg.set_citations(citations)
        self.session.add(asst_msg)

        # Update conversation timestamp
        conv.updated_at = datetime.datetime.utcnow()
        self.session.commit()

        # Check summarizer
        try:
            summarizer = ConversationSummarizer(self.session, self.router.llm_provider)
            summarizer.maybe_update_summary(conversation_id)
        except Exception:
            pass

        return {
            "conversation_id": conversation_id,
            "message": asst_msg.to_dict(),
            "response_type": route_type,
            "citations": citations
        }

    def process_message_stream(
        self,
        message: str,
        session_id: str,
        conversation_id: Optional[int] = None
    ) -> Generator[str, None, None]:
        """Processes a chat message and yields Server-Sent Events (SSE)."""
        if conversation_id is None:
            conv = Conversation(session_id=session_id, title=message[:40] + ("..." if len(message) > 40 else ""))
            self.session.add(conv)
            self.session.commit()
            conversation_id = conv.id
        else:
            conv = self.conv_service.get_conversation(conversation_id, session_id)

        user_msg = Message(
            conversation_id=conversation_id,
            role="user",
            content=message.strip(),
            response_type="user"
        )
        self.session.add(user_msg)
        self.session.commit()

        # Send conversation ID header event
        yield f"data: {json.dumps({'type': 'init', 'conversation_id': conversation_id})}\n\n"

        routed = self.router.route_and_prepare(message, session_id, conversation_id)
        citations = routed.get("citations", [])
        route_type = routed["route"]

        full_content = ""

        if routed["direct_response"] is not None:
            # Direct response chunk
            full_content = routed["direct_response"]
            yield f"data: {json.dumps({'type': 'chunk', 'content': full_content})}\n\n"
        else:
            messages_for_llm = routed["messages_for_llm"]
            try:
                for chunk in self.router.llm_provider.generate_stream(messages_for_llm):
                    full_content += chunk
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
            except ServiceUnavailableError as e:
                err_text = (
                    "\n\n⚠️ Notice: Local LLM service is offline or unreachable. "
                    "Rule matching and indexed university knowledge are active."
                )
                full_content += err_text
                yield f"data: {json.dumps({'type': 'chunk', 'content': err_text})}\n\n"
                route_type = "error"

        # Save assistant message
        asst_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=full_content,
            response_type=route_type
        )
        asst_msg.set_citations(citations)
        self.session.add(asst_msg)
        conv.updated_at = datetime.datetime.utcnow()
        self.session.commit()

        # Send completion event with citations and message object
        done_payload = {
            "type": "done",
            "message": asst_msg.to_dict(),
            "citations": citations,
            "response_type": route_type
        }
        yield f"data: {json.dumps(done_payload)}\n\n"
