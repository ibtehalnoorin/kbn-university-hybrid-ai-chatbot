from flask import Blueprint, request, jsonify, Response, stream_with_context, current_app
from app.extensions import get_db
from app.schemas.chat_schema import ChatMessageRequest
from app.services.rules.rule_engine import RuleEngine
from app.services.rag.embeddings import EmbeddingService
from app.services.rag.retriever import Retriever
from app.services.llm.ollama_provider import OllamaProvider
from app.services.hybrid_router import HybridRouter
from app.services.chat_service import ChatService
from app.api.session_helper import get_session_id
from app.utils.errors import ValidationError
from pydantic import ValidationError as PydanticValidationError

chat_bp = Blueprint("chat", __name__, url_prefix="/api")

def get_chat_service():
    session = get_db()
    rule_engine = RuleEngine()
    emb_service = EmbeddingService(
        base_url=current_app.config["OLLAMA_BASE_URL"],
        model=current_app.config["OLLAMA_EMBEDDING_MODEL"],
        dimension=current_app.config["VECTOR_DIMENSION"]
    )
    retriever = Retriever(session, emb_service)
    llm_provider = OllamaProvider(
        base_url=current_app.config["OLLAMA_BASE_URL"],
        default_model=current_app.config["OLLAMA_MODEL"]
    )
    router = HybridRouter(
        session=session,
        rule_engine=rule_engine,
        retriever=retriever,
        llm_provider=llm_provider,
        similarity_threshold=current_app.config["SIMILARITY_THRESHOLD"],
        top_k=current_app.config["TOP_K"]
    )
    return ChatService(session, router)

@chat_bp.route("/chat", methods=["POST"])
def chat():
    body = request.get_json(silent=True) or {}
    try:
        req = ChatMessageRequest(**body)
    except PydanticValidationError as e:
        raise ValidationError(f"Invalid request body: {e.errors()[0]['msg']}")

    session_id = get_session_id()
    chat_svc = get_chat_service()

    if req.stream:
        def generate():
            for chunk in chat_svc.process_message_stream(
                message=req.message,
                session_id=session_id,
                conversation_id=req.conversation_id
            ):
                yield chunk

        resp = Response(stream_with_context(generate()), mimetype="text/event-stream")
        resp.headers["Cache-Control"] = "no-cache"
        resp.headers["X-Accel-Buffering"] = "no"
        resp.headers["X-Session-Id"] = session_id
        return resp

    result = chat_svc.process_message(
        message=req.message,
        session_id=session_id,
        conversation_id=req.conversation_id
    )
    response = jsonify(result)
    response.headers["X-Session-Id"] = session_id
    return response, 200
