import sys
import requests
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.config import Config
from app.services.llm.ollama_provider import OllamaProvider

def check_all():
    print("=" * 60)
    print(" KBN UNIVERSITY HYBRID AI CHATBOT - DIAGNOSTIC CHECK")
    print("=" * 60)

    # 1. Check KBN University Website
    print("\n1. Testing KBN University website accessibility...")
    try:
        res = requests.get("https://www.kbn.university/", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if res.status_code == 200:
            print(f"   [SUCCESS] https://www.kbn.university/ reachable (HTTP {res.status_code}, {len(res.content)} bytes)")
        else:
            print(f"   [WARNING] https://www.kbn.university/ returned HTTP {res.status_code}")
    except Exception as e:
        print(f"   [ERROR] Failed to connect to KBN University website: {e}")

    # 2. Check Database
    print("\n2. Testing Database configuration...")
    print(f"   Database URI: {Config.SQLALCHEMY_DATABASE_URI}")
    try:
        from app import create_app
        from app.extensions import get_db
        from sqlalchemy import text
        app = create_app()
        with app.app_context():
            session = get_db()
            session.execute(text("SELECT 1"))
            print("   [SUCCESS] Database connection established and verified.")
    except Exception as e:
        print(f"   [ERROR] Database connection failed: {e}")

    # 3. Check Ollama & Qwen
    print("\n3. Testing Ollama & LLM...")
    ollama = OllamaProvider(base_url=Config.OLLAMA_BASE_URL, default_model=Config.OLLAMA_MODEL)
    if ollama.is_available():
        models = ollama.list_models()
        print(f"   [SUCCESS] Ollama is reachable at {Config.OLLAMA_BASE_URL}")
        print(f"   Installed models: {', '.join(models) if models else 'None'}")
        has_model = ollama.check_model_availability(Config.OLLAMA_MODEL)
        if has_model:
            print(f"   [SUCCESS] Configured model '{Config.OLLAMA_MODEL}' is ready.")
        else:
            print(f"   [NOTICE] Configured model '{Config.OLLAMA_MODEL}' not found. Run: ollama pull {Config.OLLAMA_MODEL}")
    else:
        print(f"   [OFFLINE] Ollama not reachable at {Config.OLLAMA_BASE_URL}")
        print("   -> Start Ollama via: `ollama serve` and pull models:")
        print(f"      ollama pull {Config.OLLAMA_MODEL}")
        print(f"      ollama pull {Config.OLLAMA_EMBEDDING_MODEL}")
        print("   -> Rule-based responses and crawled university RAG retrieval will continue to function.")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_all()
