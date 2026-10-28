import time
from typing import Generator, Set, Tuple
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from app.services.ingestion.url_validator import URLValidator
from app.services.ingestion.scraper import Scraper

IGNORED_EXTENSIONS = (
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp",
    ".mp4", ".mp3", ".avi", ".zip", ".tar", ".gz", ".rar",
    ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"
)

class Crawler:
    def __init__(
        self,
        base_url: str,
        max_depth: int = 2,
        max_pages: int = 30,
        crawl_delay: float = 0.5
    ):
        self.base_url = base_url
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.crawl_delay = crawl_delay
        self.validator = URLValidator(allowed_domain="kbn.university")
        self.scraper = Scraper()

    def crawl(self) -> Generator[Tuple[str, str, str], None, None]:
        """
        Crawls the domain within max_depth and max_pages.
        Yields (url, html_content, error_or_none) for each visited page.
        """
        # Queue: list of (url, current_depth)
        normalized_start = self.validator.normalize_url(self.base_url)
        queue = [(normalized_start, 0)]
        visited: Set[str] = set()

        pages_crawled = 0

        while queue and pages_crawled < self.max_pages:
            current_url, depth = queue.pop(0)

            if current_url in visited:
                continue
            visited.add(current_url)

            # Polite crawl delay
            if pages_crawled > 0 and self.crawl_delay > 0:
                time.sleep(self.crawl_delay)

            # Fetch page
            html_content, fetch_res = self.scraper.fetch(current_url, self.validator)

            if not html_content:
                yield current_url, "", fetch_res
                continue

            pages_crawled += 1
            yield current_url, html_content, None

            # If within depth limit, extract internal links
            if depth < self.max_depth:
                soup = BeautifulSoup(html_content, "html.parser")
                for tag in soup.find_all("a", href=True):
                    href = tag["href"].strip()
                    if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
                        continue

                    full_url = urljoin(current_url, href)
                    parsed = urlparse(full_url)

                    # Check extension
                    if any(parsed.path.lower().endswith(ext) for ext in IGNORED_EXTENSIONS):
                        continue

                    try:
                        normalized = self.validator.normalize_url(full_url)
                        # Check same domain
                        if "kbn.university" in parsed.netloc.lower():
                            if normalized not in visited and not any(u == normalized for u, _ in queue):
                                queue.append((normalized, depth + 1))
                    except Exception:
                        continue
