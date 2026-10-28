import re
import hashlib
from typing import Dict, Any
from bs4 import BeautifulSoup

class ContentCleaner:
    @staticmethod
    def clean_html(html_content: str) -> Dict[str, Any]:
        """
        Parses raw HTML, removes boilerplate tags (scripts, styles, nav, footer),
        extracts page title, normalizes whitespace and unicode, and computes content hash.
        """
        if not html_content:
            return {"title": "", "cleaned_text": "", "content_hash": ""}

        soup = BeautifulSoup(html_content, "html.parser")

        # Extract title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif soup.find("h1"):
            title = soup.find("h1").get_text(strip=True)

        # Decompose non-content and layout tags
        for element in soup(["script", "style", "nav", "footer", "header", "noscript", "svg", "form"]):
            element.decompose()

        # Remove common boilerplate classes
        for el in soup.find_all(class_=re.compile(r"(cookie|banner|modal|popup|sidebar|menu|social)", re.I)):
            el.decompose()

        # Extract text while preserving paragraph and heading breaks
        for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]):
            h.insert_before("\n\n")
            h.insert_after("\n")

        raw_text = soup.get_text(separator=" ")

        # Normalize unicode: zero-width spaces (\u200b), non-breaking spaces (\xa0)
        cleaned_text = raw_text.replace("\u200b", "").replace("\xa0", " ").replace("\ufeff", "")
        # Normalize excessive whitespace while preserving single paragraph breaks
        cleaned_text = re.sub(r"[ \t]+", " ", cleaned_text)
        cleaned_text = re.sub(r"\n\s*\n\s*\n+", "\n\n", cleaned_text).strip()

        # Compute SHA-256 hash
        content_hash = hashlib.sha256(cleaned_text.encode("utf-8")).hexdigest()

        return {
            "title": title or "KBN University Official Page",
            "cleaned_text": cleaned_text,
            "content_hash": content_hash
        }
