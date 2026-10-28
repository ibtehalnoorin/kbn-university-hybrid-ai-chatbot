from typing import List, Dict, Any

class CitationBuilder:
    @staticmethod
    def build_citations(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicates retrieved chunks by URL and creates structured source citations.
        """
        if not chunks:
            return []

        seen_urls = set()
        citations = []

        for c in chunks:
            url = c.get("url")
            if not url or url in seen_urls:
                continue

            seen_urls.add(url)
            content = c.get("content", "").strip()
            # Clean snippet for UI preview
            snippet = content[:180] + ("..." if len(content) > 180 else "")

            citations.append({
                "title": c.get("title") or "KBN University Official Page",
                "url": url,
                "snippet": snippet,
                "similarity": c.get("similarity", 0.0)
            })

        return citations
