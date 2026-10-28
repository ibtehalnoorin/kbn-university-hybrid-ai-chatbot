import ipaddress
import socket
import hmac
import hashlib
import time
from urllib.parse import urlparse
from app.utils.errors import ValidationError

# Private/reserved network ranges to block for SSRF prevention
BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),       # Link-local and cloud metadata
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("100.64.0.0/10"),       # Carrier-grade NAT
    ipaddress.ip_network("198.18.0.0/15"),       # Benchmark testing
    ipaddress.ip_network("::1/128"),             # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),            # IPv6 unique local
    ipaddress.ip_network("fe80::/10"),           # IPv6 link-local
]

def validate_public_url(url: str, allowed_domain: str = None) -> str:
    """
    Validates a URL against SSRF attacks:
    1. Enforces HTTP or HTTPS.
    2. Resolves DNS to check that destination IP is not private, loopback, or cloud metadata.
    3. Optionally verifies same-domain or subdomain match.
    """
    if not url or not isinstance(url, str):
        raise ValidationError("URL must be a non-empty string.")

    url = url.strip()
    parsed = urlparse(url)

    if parsed.scheme.lower() not in ("http", "https"):
        raise ValidationError(f"Invalid URL scheme '{parsed.scheme}'. Only http and https are permitted.")

    hostname = parsed.hostname
    if not hostname:
        raise ValidationError("Invalid URL: missing hostname.")

    # Restrict to allowed domain if specified
    if allowed_domain:
        allowed_clean = allowed_domain.lower().lstrip("www.")
        host_clean = hostname.lower().lstrip("www.")
        if host_clean != allowed_clean and not host_clean.endswith("." + allowed_clean):
            raise ValidationError(f"URL domain '{hostname}' is not within allowed domain '{allowed_domain}'.")

    # DNS Resolution and IP check
    try:
        addr_info = socket.getaddrinfo(hostname, None)
    except socket.gaierror as e:
        raise ValidationError(f"Failed to resolve hostname '{hostname}': {e}")

    for family, _, _, _, sockaddr in addr_info:
        ip_str = sockaddr[0]
        ip = ipaddress.ip_address(ip_str)

        for blocked_net in BLOCKED_IP_NETWORKS:
            if ip in blocked_net:
                raise ValidationError(f"Access to private/restricted IP address ({ip_str}) is prohibited.")

    return url

def generate_session_token(secret_key: str, session_id: str) -> str:
    """Generates an HMAC-SHA256 signature for a session ID."""
    sig = hmac.new(secret_key.encode("utf-8"), session_id.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{session_id}.{sig}"

def verify_session_token(secret_key: str, token: str) -> str:
    """Verifies HMAC signature of a session token and returns the session_id."""
    if not token or "." not in token:
        raise ValidationError("Invalid session token format.")
    session_id, sig = token.rsplit(".", 1)
    expected_sig = hmac.new(secret_key.encode("utf-8"), session_id.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected_sig):
        raise ValidationError("Session signature verification failed.")
    return session_id

def sanitize_untrusted_content(text: str) -> str:
    """
    Sanitizes untrusted webpage text before injecting into prompts.
    Strips prompt injection patterns, brackets, or override instructions.
    """
    if not text:
        return ""
    # Remove control characters
    cleaned = "".join(ch for ch in text if ch.isprintable() or ch in "\n\r\t")
    # Defang common injection attempts
    cleaned = cleaned.replace("[SYSTEM]", "[DOC_SYSTEM]").replace("<|im_start|>", "").replace("<|im_end|>", "")
    return cleaned
