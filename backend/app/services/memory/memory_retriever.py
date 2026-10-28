from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.services.memory.short_term import ShortTermMemory
from app.services.memory.summarizer import ConversationSummarizer
from app.services.memory.long_term import LongTermMemory

class MemoryRetriever:
    def __init__(self, session: Session, summarizer_llm=None):
        self.session = session
        self.short_term = ShortTermMemory(session)
        self.summarizer = ConversationSummarizer(session, summarizer_llm)
        self.long_term = LongTermMemory(session)

    def assemble_memory_context(
        self,
        session_id: str,
        conversation_id: int
    ) -> Dict[str, Any]:
        """
        Builds user memory context and conversation summary context.
        """
        # 1. User long-term memories
        memories = self.long_term.get_memories(session_id)
        if memories:
            mem_lines = [f"- {m['key']}: {m['value']}" for m in memories]
            user_memory_context = "USER PREFERENCES & SAVED CONTEXT:\n" + "\n".join(mem_lines)
        else:
            user_memory_context = ""

        # 2. Conversation summary
        summary = self.summarizer.get_summary(conversation_id)
        if summary:
            summary_context = f"PREVIOUS CONVERSATION SUMMARY:\n{summary}"
        else:
            summary_context = ""

        # 3. Recent short-term messages
        recent_messages = self.short_term.get_recent_messages(conversation_id)

        return {
            "user_memory_context": user_memory_context,
            "conversation_summary_context": summary_context,
            "recent_messages": recent_messages,
        }
