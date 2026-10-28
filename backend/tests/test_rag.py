import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.extensions import Base
from app.models.knowledge_source import KnowledgeSource
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.rag.embeddings import EmbeddingService
from app.services.rag.vector_store import VectorStore
from app.services.rag.retriever import Retriever
from app.services.rag.citations import CitationBuilder

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_embedding_service():
    service = EmbeddingService(dimension=768)
    vec = service.get_embedding("KBN University Engineering Faculty")
    assert len(vec) == 768
    assert isinstance(vec[0], float)

def test_vector_store_and_retriever(db_session):
    emb_service = EmbeddingService(dimension=768)
    store = VectorStore(db_session)
    retriever = Retriever(db_session, emb_service)

    # Seed knowledge source and document
    source = KnowledgeSource(base_url="https://www.kbn.university/", name="KBN Portal")
    db_session.add(source)
    db_session.commit()

    doc = Document(
        source_id=source.id,
        url="https://www.kbn.university/engineering",
        title="Faculty of Engineering",
        content="The Faculty of Engineering offers B.Tech programs in Computer Science.",
        content_hash="mockhash123"
    )
    db_session.add(doc)
    db_session.commit()

    # Create chunk with matching embedding
    text = "The Faculty of Engineering offers B.Tech programs in Computer Science."
    emb = emb_service.get_embedding(text)
    chunk = DocumentChunk(
        document_id=doc.id,
        chunk_index=0,
        content=text,
        char_count=len(text),
        embedding=emb
    )
    db_session.add(chunk)
    db_session.commit()

    # Search with matching query
    results, context_str = retriever.retrieve("The Faculty of Engineering offers B.Tech programs in Computer Science.", top_k=3, threshold=0.3)
    assert len(results) > 0
    assert "Faculty of Engineering" in context_str
    assert "https://www.kbn.university/engineering" in context_str

    # Test Citation Builder
    citations = CitationBuilder.build_citations(results)
    assert len(citations) == 1
    assert citations[0]["url"] == "https://www.kbn.university/engineering"
    assert citations[0]["title"] == "Faculty of Engineering"
