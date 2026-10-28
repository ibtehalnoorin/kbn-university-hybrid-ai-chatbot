from flask import Blueprint, request, jsonify
from app.extensions import get_db
from app.services.memory.long_term import LongTermMemory
from app.schemas.memory_schema import MemoryCreateRequest, MemoryUpdateRequest, MemoryToggleRequest
from app.api.session_helper import get_session_id
from app.utils.errors import NotFoundError, ValidationError
from pydantic import ValidationError as PydanticValidationError

memories_bp = Blueprint("memories", __name__, url_prefix="/api/memories")

@memories_bp.route("", methods=["GET"])
def get_memories():
    session_id = get_session_id()
    svc = LongTermMemory(get_db())
    memories = svc.get_memories(session_id)
    return jsonify({
        "memories": memories,
        "count": len(memories),
        "enabled": svc.is_enabled(session_id)
    }), 200

@memories_bp.route("", methods=["POST"])
def add_memory():
    session_id = get_session_id()
    body = request.get_json(silent=True) or {}
    try:
        req = MemoryCreateRequest(**body)
    except PydanticValidationError as e:
        raise ValidationError(f"Invalid input: {e.errors()[0]['msg']}")

    svc = LongTermMemory(get_db())
    created = svc.add_or_update_memory(
        session_id=session_id,
        key=req.key,
        value=req.value,
        category=req.category or "preference"
    )
    if not created:
        return jsonify({"message": "Memory was filtered due to privacy restrictions or memory being disabled."}), 400
    return jsonify(created), 201

@memories_bp.route("/<int:memory_id>", methods=["PATCH"])
def update_memory(memory_id):
    session_id = get_session_id()
    body = request.get_json(silent=True) or {}
    try:
        req = MemoryUpdateRequest(**body)
    except PydanticValidationError as e:
        raise ValidationError(f"Invalid input: {e.errors()[0]['msg']}")

    session = get_db()
    from app.models.memory import Memory
    mem = session.query(Memory).filter_by(id=memory_id, session_id=session_id).first()
    if not mem:
        raise NotFoundError(f"Memory {memory_id} not found.")

    if req.key:
        mem.key = req.key.strip()
    if req.value:
        mem.value = req.value.strip()
    if req.category:
        mem.category = req.category.strip()

    session.commit()
    return jsonify(mem.to_dict()), 200

@memories_bp.route("/<int:memory_id>", methods=["DELETE"])
def delete_memory(memory_id):
    session_id = get_session_id()
    svc = LongTermMemory(get_db())
    success = svc.delete_memory(memory_id, session_id)
    if not success:
        raise NotFoundError(f"Memory {memory_id} not found.")
    return jsonify({"message": f"Memory {memory_id} deleted."}), 200

@memories_bp.route("", methods=["DELETE"])
def clear_all_memories():
    session_id = get_session_id()
    svc = LongTermMemory(get_db())
    count = svc.clear_all(session_id)
    return jsonify({"message": f"Cleared {count} saved memories."}), 200

@memories_bp.route("/settings", methods=["GET"])
def get_settings():
    session_id = get_session_id()
    svc = LongTermMemory(get_db())
    return jsonify({"long_term_memory_enabled": svc.is_enabled(session_id)}), 200

@memories_bp.route("/settings", methods=["POST"])
def toggle_settings():
    session_id = get_session_id()
    body = request.get_json(silent=True) or {}
    try:
        req = MemoryToggleRequest(**body)
    except PydanticValidationError as e:
        raise ValidationError(f"Invalid input: {e.errors()[0]['msg']}")

    svc = LongTermMemory(get_db())
    enabled = svc.toggle_memory(session_id, req.enabled)
    return jsonify({"long_term_memory_enabled": enabled}), 200
