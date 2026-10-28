from flask import Blueprint, jsonify, current_app
from sqlalchemy import text
from app.extensions import get_db
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.knowledge_source import KnowledgeSource
from app.services.llm.ollama_provider import OllamaProvider

health_bp = Blueprint("health", __name__, url_prefix="/api")

@health_bp.route("/health", methods=["GET"])
def health():
    db_status = "unknown"
    db_type = "unknown"
    doc_count = 0
    chunk_count = 0
    source_count = 0

    session = get_db()
    try:
        bind = session.get_bind()
        db_type = bind.dialect.name if bind else "unknown"
        session.execute(text("SELECT 1"))
        db_status = "connected"
        doc_count = session.query(Document).count()
        chunk_count = session.query(DocumentChunk).count()
        source_count = session.query(KnowledgeSource).count()
    except Exception as e:
        db_status = f"disconnected ({str(e)})"

    return jsonify({
        "status": "online" if db_status == "connected" else "degraded",
        "database": {
            "status": db_status,
            "engine": db_type,
            "indexed_sources": source_count,
            "indexed_documents": doc_count,
            "indexed_chunks": chunk_count,
        },
        "version": "1.0.0"
    }), 200

@health_bp.route("/llm/status", methods=["GET"])
def llm_status():
    provider = OllamaProvider(
        base_url=current_app.config["OLLAMA_BASE_URL"],
        default_model=current_app.config["OLLAMA_MODEL"]
    )
    is_online = provider.is_available()
    configured_model = current_app.config["OLLAMA_MODEL"]
    configured_embedding_model = current_app.config["OLLAMA_EMBEDDING_MODEL"]

    installed_models = []
    model_ready = False
    embedding_ready = False

    if is_online:
        installed_models = provider.list_models()
        model_ready = provider.check_model_availability(configured_model)
        embedding_ready = provider.check_model_availability(configured_embedding_model)

    return jsonify({
        "provider": "ollama",
        "base_url": current_app.config["OLLAMA_BASE_URL"],
        "is_reachable": is_online,
        "configured_model": configured_model,
        "model_available": model_ready,
        "configured_embedding_model": configured_embedding_model,
        "embedding_model_available": embedding_ready,
        "vector_dimension": current_app.config["VECTOR_DIMENSION"],
        "installed_models": installed_models
    }), 200

@health_bp.route("/models", methods=["GET"])
def list_models():
    provider = OllamaProvider(base_url=current_app.config["OLLAMA_BASE_URL"])
    models = provider.list_models()
    return jsonify({"models": models, "count": len(models)}), 200
