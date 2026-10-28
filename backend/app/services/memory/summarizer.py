import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.models.message import Message
from app.models.conversation_summary import ConversationSummary
from app.services.llm.base_provider import BaseLLMProvider

logger = logging.getLogger(__name__)

class ConversationSummarizer:
    def __init__(self, session: Session, llm_provider: Optional[BaseLLMProvider] = None, threshold: int = 8):
        self.session = session
        self.llm_provider = llm_provider
        self.threshold = threshold

    def get_summary(self, conversation_id: int) -> Optional[str]:
        """Retrieves active conversation summary if one exists."""
        rec = self.session.query(ConversationSummary).filter_by(conversation_id=conversation_id).first()
        return rec.summary if rec else None

    def maybe_update_summary(self, conversation_id: int) -> Optional[str]:
        """
        If total messages exceed the threshold, summarizes older messages and persists
        the summary in the database.
        """
        total_msgs = self.session.query(Message).filter_by(conversation_id=conversation_id).count()
        if total_msgs < self.threshold:
            return None

        summary_rec = self.session.query(ConversationSummary).filter_by(conversation_id=conversation_id).first()
        last_id = summary_rec.last_summarized_message_id if summary_rec else 0

        # Fetch messages that are older than the most recent 4 messages, and not yet summarized
        all_msgs = (
            self.session.query(Message)
            .filter_by(conversation_id=conversation_id)
            .order_by(Message.id.asc())
            .all()
        )

        unsummarized = [m for m in all_msgs[:-4] if m.id > last_id]
        if len(unsummarized) < 4:
            return summary_rec.summary if summary_rec else None

        # Build transcript to summarize
        transcript = "\n".join([f"{m.role.capitalize()}: {m.content}" for m in unsummarized])
        prev_summary = summary_rec.summary if summary_rec else "None"

        prompt = (
            f"You are a conversation summarizer. Provide a concise summary (2-4 sentences) capturing key facts, "
            f"user inquiries, and student context from this ongoing university helpdesk dialogue.\n\n"
            f"Previous Summary: {prev_summary}\n\n"
            f"New Messages to incorporate:\n{transcript}\n\n"
            f"Updated Concise Summary:"
        )

        new_summary = None
        if self.llm_provider and self.llm_provider.is_available():
            try:
                new_summary = self.llm_provider.generate(
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    max_tokens=256
                )
            except Exception as e:
                logger.warning(f"Could not generate LLM summary: {e}")

        # Deterministic extractive fallback if LLM is unavailable
        if not new_summary:
            topics = [m.content[:60] for m in unsummarized if m.role == "user"]
            new_summary = f"User inquired about: {'; '.join(topics[:3])}."

        latest_id = unsummarized[-1].id

        if summary_rec:
            summary_rec.summary = new_summary
            summary_rec.last_summarized_message_id = latest_id
        else:
            summary_rec = ConversationSummary(
                conversation_id=conversation_id,
                summary=new_summary,
                last_summarized_message_id=latest_id
            )
            self.session.add(summary_rec)

        self.session.commit()
        return new_summary
