import re
from typing import List, Dict, Any

class RecursiveChunker:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 120):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Splits clean text into overlapping chunks, attempting to split at paragraphs,
        sentences, or natural punctuation boundaries.
        """
        if not text:
            return []

        text = text.strip()
        if len(text) <= self.chunk_size:
            return [{"chunk_index": 0, "content": text, "char_count": len(text)}]

        # Split points in priority order: paragraphs, sentence ends, whitespace
        chunks = []
        start = 0
        text_len = len(text)
        chunk_idx = 0

        while start < text_len:
            end = min(start + self.chunk_size, text_len)

            if end < text_len:
                # Look for paragraph break
                para_break = text.rfind("\n\n", start, end)
                if para_break != -1 and para_break > start + (self.chunk_size // 3):
                    end = para_break + 2
                else:
                    # Look for sentence boundary (.!?)
                    match = re.search(r"[\.!?]\s+", text[start + (self.chunk_size // 2):end])
                    if match:
                        end = start + (self.chunk_size // 2) + match.end()
                    else:
                        # Look for space
                        space_break = text.rfind(" ", start, end)
                        if space_break != -1 and space_break > start + (self.chunk_size // 3):
                            end = space_break + 1

            chunk_content = text[start:end].strip()
            if chunk_content:
                chunks.append({
                    "chunk_index": chunk_idx,
                    "content": chunk_content,
                    "char_count": len(chunk_content)
                })
                chunk_idx += 1

            if end >= text_len:
                break

            # Calculate next start with overlap
            start = max(start + 1, end - self.chunk_overlap)

        return chunks
