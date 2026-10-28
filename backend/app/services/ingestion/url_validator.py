import urllib.robotparser
from urllib.parse import urlparse, urlunparse
from app.utils.security import validate_public_url
from app.utils.errors import ValidationError

class URLValidator:
    def __init__(self, allowed_domain: str = "kbn.university"):
        self.allowed_domain = allowed_domain.lower().lstrip("www.")
        self.robot_parsers = {}

    def normalize_url(self, url: str) -> str:
        """Strips fragments, normalizes scheme and trailing slashes."""
        if not url:
            raise ValidationError("URL cannot be empty.")
        parsed = urlparse(url.strip())
        # Strip fragment
        path = parsed.path
        if not path:
            path = "/"
        elif path != "/" and path.endswith("/"):
            path = path[:-1]

        # Rebuild without fragment
        normalized = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            path,
            parsed.params,
            parsed.query,
            ""
        ))
        return normalized

    def validate(self, url: str) -> str:
        """Validates scheme, SSRF restrictions, and domain match."""
        norm_url = self.normalize_url(url)
        # Check SSRF and domain
        validate_public_url(norm_url, allowed_domain=self.allowed_domain)
        return norm_url

    def can_fetch(self, url: str, user_agent: str = "*") -> bool:
        """Checks robots.txt for whether URL is permitted."""
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"

        if base not in self.robot_parsers:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"{base}/robots.txt")
            try:
                rp.read()
                self.robot_parsers[base] = rp
            except Exception:
                # If robots.txt cannot be fetched or read, default to allow
                self.robot_parsers[base] = None

        rp = self.robot_parsers.get(base)
        if rp is None:
            return True
        return rp.can_fetch(user_agent, url)
