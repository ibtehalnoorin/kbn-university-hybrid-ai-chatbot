import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.extensions import Base

class KnowledgeSource(Base):
    __tablename__ = "knowledge_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    base_url = Column(String(512), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    total_pages = Column(Integer, default=0)
    last_crawled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    documents = relationship("Document", back_populates="source", cascade="all, delete-orphan")
    jobs = relationship("IngestionJob", back_populates="source", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "base_url": self.base_url,
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "total_pages": self.total_pages,
            "last_crawled_at": self.last_crawled_at.isoformat() if self.last_crawled_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
