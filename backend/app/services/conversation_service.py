import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.conversation import Conversation
from app.models.message import Message
from app.utils.errors import NotFoundError

class ConversationService:
    def __init__(self, session: Session):
        self.session = session

    def list_conversations(self, session_id: str) -> List[Dict[str, Any]]:
        convs = (
            self.session.query(Conversation)
            .filter_by(session_id=session_id)
            .order_by(Conversation.updated_at.desc())
            .all()
        )
        return [c.to_dict() for c in convs]

    def create_conversation(self, session_id: str, title: str = "New Conversation") -> Dict[str, Any]:
        conv = Conversation(session_id=session_id, title=title)
        self.session.add(conv)
        self.session.commit()
        return conv.to_dict()

    def get_conversation(self, conversation_id: int, session_id: str) -> Conversation:
        conv = (
            self.session.query(Conversation)
            .filter_by(id=conversation_id, session_id=session_id)
            .first()
        )
        if not conv:
            raise NotFoundError(f"Conversation {conversation_id} not found.")
        return conv

    def update_conversation(self, conversation_id: int, session_id: str, title: str) -> Dict[str, Any]:
        conv = self.get_conversation(conversation_id, session_id)
        conv.title = title.strip()
        conv.updated_at = datetime.datetime.utcnow()
        self.session.commit()
        return conv.to_dict()

    def delete_conversation(self, conversation_id: int, session_id: str) -> bool:
        conv = self.get_conversation(conversation_id, session_id)
        self.session.delete(conv)
        self.session.commit()
        return True

    def get_messages(self, conversation_id: int, session_id: str) -> List[Dict[str, Any]]:
        conv = self.get_conversation(conversation_id, session_id)
        messages = (
            self.session.query(Message)
            .filter_by(conversation_id=conv.id)
            .order_by(Message.id.asc())
            .all()
        )
        return [m.to_dict() for m in messages]

    def clear_messages(self, conversation_id: int, session_id: str) -> bool:
        conv = self.get_conversation(conversation_id, session_id)
        self.session.query(Message).filter_by(conversation_id=conv.id).delete()
        self.session.commit()
        return True
