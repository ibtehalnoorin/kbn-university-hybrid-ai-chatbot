import json
import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index, TypeDecorator
from sqlalchemy.orm import relationship
from app.extensions import Base

try:
    from pgvector.sqlalchemy import Vector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False

class VectorType(TypeDecorator):
    """
    Transparent vector type that utilizes pgvector.sqlalchemy.Vector on PostgreSQL,
    and falls back to JSON-serialized lists of floats on other databases like SQLite.
    """
    impl = Text
    cache_ok = True

    def __init__(self, dim=768, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dim = dim

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql" and HAS_PGVECTOR:
            return dialect.type_descriptor(Vector(self.dim))
        else:
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql" and HAS_PGVECTOR:
            return value
        # For SQLite / JSON fallback
        if isinstance(value, (list, tuple)):
            return json.dumps(list(value))
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql" and HAS_PGVECTOR:
            if hasattr(value, "tolist"):
                return value.tolist()
            return list(value)
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                return []
        return value

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    char_count = Column(Integer, default=0)
    embedding = Column(VectorType(dim=768), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="chunks")

    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "chunk_index": self.chunk_index,
            "content": self.content,
            "char_count": self.char_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
