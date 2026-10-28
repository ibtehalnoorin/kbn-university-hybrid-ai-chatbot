import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import Base

class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("knowledge_sources.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="pending", index=True)  # pending, running, completed, failed
    pages_discovered = Column(Integer, default=0)
    pages_processed = Column(Integer, default=0)
    pages_failed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    source = relationship("KnowledgeSource", back_populates="jobs")

    def to_dict(self):
        return {
            "id": self.id,
            "source_id": self.source_id,
            "source_url": self.source.base_url if self.source else None,
            "status": self.status,
            "pages_discovered": self.pages_discovered,
            "pages_processed": self.pages_processed,
            "pages_failed": self.pages_failed,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
