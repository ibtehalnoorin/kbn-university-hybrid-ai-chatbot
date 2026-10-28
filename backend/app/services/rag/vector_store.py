import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.document_chunk import DocumentChunk
from app.models.document import Document

class VectorStore:
    def __init__(self, session: Session):
        self.session = session

    def search_similar(
        self,
        query_vector: List[float],
        top_k: int = 5,
        threshold: float = 0.45
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top_k document chunks most similar to query_vector.
        Utilizes pgvector cosine distance on PostgreSQL, or NumPy cosine similarity on SQLite.
        """
        if not query_vector:
            return []

        bind = self.session.get_bind()
        is_postgres = bind and bind.dialect.name == "postgresql"

        if is_postgres:
            try:
                # pgvector cosine distance: embedding <=> query_vector
                # similarity = 1 - cosine_distance
                q_vec_str = "[" + ",".join(str(float(x)) for x in query_vector) + "]"
                sql = text("""
                    SELECT c.id, c.document_id, c.content, c.chunk_index,
                           d.url, d.title,
                           1 - (c.embedding <=> :qvec) AS similarity
                    FROM document_chunks c
                    JOIN documents d ON c.document_id = d.id
                    WHERE c.embedding IS NOT NULL
                    ORDER BY c.embedding <=> :qvec ASC
                    LIMIT :top_k
                """)
                res = self.session.execute(sql, {"qvec": q_vec_str, "top_k": top_k * 2}).fetchall()
                results = []
                for row in res:
                    sim = float(row.similarity) if row.similarity is not None else 0.0
                    if sim >= threshold:
                        results.append({
                            "chunk_id": row.id,
                            "document_id": row.document_id,
                            "content": row.content,
                            "chunk_index": row.chunk_index,
                            "url": row.url,
                            "title": row.title or "KBN University Official Page",
                            "similarity": round(sim, 4),
                        })
                    if len(results) >= top_k:
                        break
                return results
            except Exception as e:
                # If pgvector query fails (e.g. extension syntax issue), fall through to python similarity
                pass

        # Python / NumPy Cosine Similarity fallback for SQLite or local dev
        chunks = self.session.query(DocumentChunk).join(Document).all()
        if not chunks:
            return []

        q_vec = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            return []

        scored_chunks = []
        for c in chunks:
            emb = c.embedding
            if not emb or not isinstance(emb, (list, tuple)):
                continue
            c_vec = np.array(emb, dtype=np.float32)
            c_norm = np.linalg.norm(c_vec)
            if c_norm == 0:
                continue

            sim = float(np.dot(q_vec, c_vec) / (q_norm * c_norm))
            if sim >= threshold:
                doc = c.document
                scored_chunks.append({
                    "chunk_id": c.id,
                    "document_id": c.document_id,
                    "content": c.content,
                    "chunk_index": c.chunk_index,
                    "url": doc.url if doc else "https://www.kbn.university/",
                    "title": (doc.title if doc and doc.title else "KBN University Official Page"),
                    "similarity": round(sim, 4),
                })

        # Sort by similarity descending
        scored_chunks.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_chunks[:top_k]
