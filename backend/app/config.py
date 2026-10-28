import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory for backend
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = FLASK_ENV == "development"
    SECRET_KEY = os.getenv("SECRET_KEY", "kbn-insecure-secret-key-change-me")
    
    # Database
    db_env = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'kbn_chatbot.db'}")
    if db_env.startswith("sqlite:///") and not db_env.startswith("sqlite:////") and ":memory:" not in db_env:
        rel_path = db_env.replace("sqlite:///", "", 1)
        if not os.path.isabs(rel_path):
            DATABASE_URL = f"sqlite:///{BASE_DIR / rel_path}"
        else:
            DATABASE_URL = db_env
    else:
        DATABASE_URL = db_env

    # Handle postgres:// vs postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
    elif DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
    } if not DATABASE_URL.startswith("sqlite") else {}
    
    # LLM & Embedding Settings
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    VECTOR_DIMENSION = int(os.getenv("VECTOR_DIMENSION", "768"))
    
    # RAG Settings
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))
    TOP_K = int(os.getenv("TOP_K", "5"))
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.45"))
    
    # Ingestion & Crawler Settings
    CRAWL_MAX_DEPTH = int(os.getenv("CRAWL_MAX_DEPTH", "2"))
    CRAWL_MAX_PAGES = int(os.getenv("CRAWL_MAX_PAGES", "30"))
    CRAWL_DELAY_SECONDS = float(os.getenv("CRAWL_DELAY_SECONDS", "0.5"))
    REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "15"))
    
    # Security & CORS
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
    CORS_ORIGINS = [FRONTEND_URL, "http://127.0.0.1:5173", "http://localhost:5000"]
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
