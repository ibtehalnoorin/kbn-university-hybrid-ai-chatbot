import requests
from typing import Optional, Tuple
from app.services.ingestion.url_validator import URLValidator
from app.utils.errors import ValidationError

class Scraper:
    def __init__(self, timeout: int = 15, max_bytes: int = 5 * 1024 * 1024):
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 KBNUniversityBot/1.0"
        }

    def fetch(self, url: str, validator: URLValidator) -> Tuple[Optional[str], Optional[str]]:
        """
        Fetches webpage content with SSRF redirect validation and size limits.
        Returns (html_content, final_url) or (None, error_str).
        """
        current_url = url
        try:
            # Validate starting URL
            current_url = validator.validate(current_url)

            # Check robots.txt permission
            if not validator.can_fetch(current_url):
                return None, f"Crawling prohibited by robots.txt for: {current_url}"

            # Make request with manual redirect following to validate each hop
            session = requests.Session()
            res = session.get(
                current_url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True,
                stream=True
            )

            # Re-validate final destination URL after redirects
            final_url = validator.validate(res.url)

            if res.status_code != 200:
                return None, f"HTTP error {res.status_code} fetching {final_url}"

            content_type = res.headers.get("Content-Type", "")
            if "text/html" not in content_type and "text/plain" not in content_type:
                return None, f"Unsupported Content-Type: {content_type}"

            # Read content with byte limit
            content_chunks = []
            bytes_read = 0
            for chunk in res.iter_content(chunk_size=8192):
                bytes_read += len(chunk)
                if bytes_read > self.max_bytes:
                    return None, f"Content exceeded maximum size limit of {self.max_bytes} bytes."
                content_chunks.append(chunk)

            raw_bytes = b"".join(content_chunks)
            encoding = res.encoding or "utf-8"
            html_text = raw_bytes.decode(encoding, errors="replace")
            return html_text, final_url

        except ValidationError as e:
            return None, f"Security validation error: {str(e)}"
        except requests.exceptions.Timeout:
            return None, f"Request timed out after {self.timeout}s fetching {current_url}"
        except requests.exceptions.RequestException as e:
            return None, f"Network error fetching {current_url}: {str(e)}"
        except Exception as e:
            return None, f"Unexpected error scraping {current_url}: {str(e)}"
