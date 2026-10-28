from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.services.rag.embeddings import EmbeddingService
from app.services.rag.vector_store import VectorStore
from app.utils.security import sanitize_untrusted_content

class Retriever:
    def __init__(self, session: Session, embedding_service: EmbeddingService):
        self.session = session
        self.embedding_service = embedding_service
        self.vector_store = VectorStore(session)

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.45
    ) -> Tuple[List[Dict[str, Any]], str]:
        """
        Retrieves relevant document chunks and assembles formatted context text.
        Returns (chunks, formatted_context_str).
        """
        if not query or not query.strip():
            return [], ""

        # Generate query vector
        query_vec = self.embedding_service.get_embedding(query)

        # Retrieve top chunks
        chunks = self.vector_store.search_similar(query_vec, top_k=top_k, threshold=threshold)

        if not chunks:
            return [], ""

        # Format context passages securely
        passage_blocks = []
        for i, c in enumerate(chunks, 1):
            sanitized_text = sanitize_untrusted_content(c["content"])
            block = (
                f"[Source {i}: {c['title']} | URL: {c['url']}]\n"
                f"{sanitized_text}"
            )
            passage_blocks.append(block)

        context_str = "\n\n".join(passage_blocks)
        return chunks, context_str
