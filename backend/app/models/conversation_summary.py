import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import Base

class ConversationSummary(Base):
    __tablename__ = "conversation_summaries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    summary = Column(Text, nullable=False)
    last_summarized_message_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="summaries")

    def to_dict(self):
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "summary": self.summary,
            "last_summarized_message_id": self.last_summarized_message_id,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
