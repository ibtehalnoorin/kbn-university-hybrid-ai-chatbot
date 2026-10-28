import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.extensions import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("knowledge_sources.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(String(1024), nullable=False, unique=True, index=True)
    title = Column(String(512), nullable=True)
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    source = relationship("KnowledgeSource", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "source_id": self.source_id,
            "url": self.url,
            "title": self.title,
            "content_length": len(self.content) if self.content else 0,
            "content_hash": self.content_hash,
            "chunk_count": len(self.chunks) if self.chunks else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
