import json
import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(32), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    response_type = Column(String(32), default="llm")  # rule, rag, llm, error
    citations = Column(Text, nullable=True)  # JSON-encoded array of {title, url, snippet}
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    def get_citations(self):
        if not self.citations:
            return []
        try:
            return json.loads(self.citations)
        except Exception:
            return []

    def set_citations(self, citations_list):
        if not citations_list:
            self.citations = None
        else:
            self.citations = json.dumps(citations_list)

    def to_dict(self):
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "response_type": self.response_type,
            "citations": self.get_citations(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
