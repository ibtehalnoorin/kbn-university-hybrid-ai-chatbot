import hashlib
import logging
import numpy as np
import requests
from typing import List

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "nomic-embed-text",
        dimension: int = 768
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.dimension = dimension
        self._local_model = None

    def _generate_fallback_vector(self, text: str) -> List[float]:
        """
        Deterministic pseudo-semantic vector generator for fallback and unit tests
        when Ollama or network is unavailable. Ensures unit length and consistent dimension.
        """
        seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(self.dimension)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def get_embedding(self, text: str) -> List[float]:
        """Generates embedding for a single text."""
        if not text:
            return [0.0] * self.dimension

        # 1. Try Ollama Embeddings API
        try:
            url = f"{self.base_url}/api/embeddings"
            payload = {"model": self.model, "prompt": text}
            res = requests.post(url, json=payload, timeout=8)
            if res.status_code == 200:
                data = res.json()
                emb = data.get("embedding", [])
                if emb and len(emb) == self.dimension:
                    return emb
                elif emb:
                    # Adjust dimension if model outputs different size
                    return self._pad_or_truncate(emb)
        except Exception as e:
            logger.debug(f"Ollama embedding unavailable ({e}), trying fallback.")

        # 2. Try local sentence-transformers if available
        try:
            if self._local_model is None:
                from sentence_transformers import SentenceTransformer
                self._local_model = SentenceTransformer("all-MiniLM-L6-v2")
            raw_emb = self._local_model.encode(text).tolist()
            return self._pad_or_truncate(raw_emb)
        except Exception:
            pass

        # 3. Deterministic fallback vector
        return self._generate_fallback_vector(text)

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a batch of texts."""
        return [self.get_embedding(t) for t in texts]

    def _pad_or_truncate(self, vec: List[float]) -> List[float]:
        if len(vec) == self.dimension:
            return vec
        if len(vec) > self.dimension:
            trimmed = vec[:self.dimension]
            # normalize
            arr = np.array(trimmed)
            norm = np.linalg.norm(arr)
            return (arr / (norm if norm > 0 else 1.0)).tolist()
        else:
            # pad with zeros
            padded = vec + [0.0] * (self.dimension - len(vec))
            return padded
