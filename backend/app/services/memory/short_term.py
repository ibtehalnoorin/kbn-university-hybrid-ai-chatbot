from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.message import Message

class ShortTermMemory:
    def __init__(self, session: Session, window_size: int = 6):
        self.session = session
        self.window_size = window_size

    def get_recent_messages(self, conversation_id: int) -> List[Dict[str, str]]:
        """
        Retrieves the last N messages from the active conversation formatted for LLM.
        """
        if not conversation_id:
            return []

        messages = (
            self.session.query(Message)
            .filter_by(conversation_id=conversation_id)
            .order_by(Message.id.desc())
            .limit(self.window_size)
            .all()
        )

        # Reverse to chronological order
        messages.reverse()

        formatted = []
        for m in messages:
            if m.role in ("user", "assistant", "system"):
                formatted.append({
                    "role": m.role,
                    "content": m.content
                })

        return formatted
