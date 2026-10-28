import pytest
from app.utils.security import validate_public_url
from app.utils.errors import ValidationError
from app.services.ingestion.url_validator import URLValidator
from app.services.ingestion.content_cleaner import ContentCleaner
from app.services.rag.chunker import RecursiveChunker

def test_ssrf_protection_blocks_private_ips():
    blocked_urls = [
        "http://127.0.0.1:8080/admin",
        "http://localhost:5000",
        "http://169.254.169.254/latest/meta-data/",
        "http://10.0.0.1/secrets",
        "http://192.168.1.1/router",
        "http://172.16.0.1/",
        "ftp://example.com/file",
        "javascript:alert(1)"
    ]
    for url in blocked_urls:
        with pytest.raises(ValidationError):
            validate_public_url(url)

def test_url_validator_domain_and_normalization():
    validator = URLValidator(allowed_domain="kbn.university")
    
    # Normalizes trailing slash and fragments
    norm = validator.normalize_url("https://www.kbn.university/about/#history")
    assert norm == "https://www.kbn.university/about"
    
    # Rejects different domain
    with pytest.raises(ValidationError):
        validator.validate("https://evil-hacker-site.com/exploit")

def test_content_cleaner():
    raw_html = """
    <html>
        <head><title>Engineering Faculty | KBN University</title></head>
        <body>
            <header><nav><a href="/">Home</a></nav></header>
            <script>console.log("bad code");</script>
            <main>
                <h1>Faculty of Engineering & Technology</h1>
                <p>Welcome to KBN\u200b University engineering division.\xa0Top facilities.</p>
            </main>
            <footer><p>&copy; 2026 KBN University</p></footer>
        </body>
    </html>
    """
    cleaned = ContentCleaner.clean_html(raw_html)
    assert cleaned["title"] == "Engineering Faculty | KBN University"
    assert "console.log" not in cleaned["cleaned_text"]
    assert "Faculty of Engineering & Technology" in cleaned["cleaned_text"]
    assert "\u200b" not in cleaned["cleaned_text"]  # Zero width space cleaned
    assert len(cleaned["content_hash"]) == 64

def test_recursive_chunker():
    chunker = RecursiveChunker(chunk_size=100, chunk_overlap=20)
    sample_text = (
        "Khaja Bandanawaz University is established under Karnataka Act No. 23 of 2018. "
        "It features multiple faculties offering comprehensive degrees. "
        "The campus is located in Kalaburagi, Karnataka."
    )
    chunks = chunker.chunk_text(sample_text)
    assert len(chunks) >= 2
    for c in chunks:
        assert len(c["content"]) <= 120
        assert "chunk_index" in c
