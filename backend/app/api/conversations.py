from flask import Blueprint, request, jsonify
from app.extensions import get_db
from app.services.conversation_service import ConversationService
from app.schemas.chat_schema import ConversationUpdateRequest
from app.api.session_helper import get_session_id
from app.utils.errors import ValidationError
from pydantic import ValidationError as PydanticValidationError

conversations_bp = Blueprint("conversations", __name__, url_prefix="/api/conversations")

@conversations_bp.route("", methods=["GET"])
def list_conversations():
    session_id = get_session_id()
    svc = ConversationService(get_db())
    convs = svc.list_conversations(session_id)
    return jsonify({"conversations": convs, "count": len(convs)}), 200

@conversations_bp.route("", methods=["POST"])
def create_conversation():
    session_id = get_session_id()
    body = request.get_json(silent=True) or {}
    title = body.get("title", "New Conversation")
    svc = ConversationService(get_db())
    conv = svc.create_conversation(session_id, title)
    return jsonify(conv), 201

@conversations_bp.route("/<int:conv_id>/messages", methods=["GET"])
def get_messages(conv_id):
    session_id = get_session_id()
    svc = ConversationService(get_db())
    messages = svc.get_messages(conv_id, session_id)
    return jsonify({"messages": messages, "count": len(messages)}), 200

@conversations_bp.route("/<int:conv_id>", methods=["PATCH"])
def update_conversation(conv_id):
    session_id = get_session_id()
    body = request.get_json(silent=True) or {}
    try:
        req = ConversationUpdateRequest(**body)
    except PydanticValidationError as e:
        raise ValidationError(f"Invalid title: {e.errors()[0]['msg']}")

    svc = ConversationService(get_db())
    updated = svc.update_conversation(conv_id, session_id, req.title)
    return jsonify(updated), 200

@conversations_bp.route("/<int:conv_id>", methods=["DELETE"])
def delete_conversation(conv_id):
    session_id = get_session_id()
    svc = ConversationService(get_db())
    svc.delete_conversation(conv_id, session_id)
    return jsonify({"message": f"Conversation {conv_id} deleted successfully."}), 200

@conversations_bp.route("/<int:conv_id>/messages", methods=["DELETE"])
def clear_messages(conv_id):
    session_id = get_session_id()
    svc = ConversationService(get_db())
    svc.clear_messages(conv_id, session_id)
    return jsonify({"message": f"All messages in conversation {conv_id} cleared."}), 200
