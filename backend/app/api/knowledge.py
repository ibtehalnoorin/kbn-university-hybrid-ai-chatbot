from flask import Blueprint, request, jsonify, current_app
from app.extensions import get_db
from app.models.knowledge_source import KnowledgeSource
from app.models.ingestion_job import IngestionJob
from app.schemas.knowledge_schema import AddKnowledgeSourceRequest
from app.services.ingestion.url_validator import URLValidator
from app.services.ingestion.ingestion_service import IngestionService
from app.utils.errors import NotFoundError, ValidationError
from pydantic import ValidationError as PydanticValidationError

knowledge_bp = Blueprint("knowledge", __name__, url_prefix="/api/knowledge")

@knowledge_bp.route("/sources", methods=["GET"])
def list_sources():
    session = get_db()
    sources = session.query(KnowledgeSource).order_by(KnowledgeSource.id.desc()).all()
    return jsonify({"sources": [s.to_dict() for s in sources], "count": len(sources)}), 200

@knowledge_bp.route("/sources", methods=["POST"])
def add_source():
    body = request.get_json(silent=True) or {}
    try:
        req = AddKnowledgeSourceRequest(**body)
    except PydanticValidationError as e:
        raise ValidationError(f"Invalid input: {e.errors()[0]['msg']}")

    session = get_db()
    validator = URLValidator(allowed_domain="kbn.university")
    normalized_url = validator.validate(req.url)

    # Check if already exists
    existing = session.query(KnowledgeSource).filter_by(base_url=normalized_url).first()
    if existing:
        source = existing
    else:
        source = KnowledgeSource(
            base_url=normalized_url,
            name=req.name or "KBN University Official Site",
            description=req.description or "Primary university knowledge base"
        )
        session.add(source)
        session.commit()

    # Create ingestion job
    job = IngestionJob(source_id=source.id, status="pending")
    session.add(job)
    session.commit()

    # Trigger background ingestion
    IngestionService.start_background_ingestion(
        app=current_app._get_current_object(),
        job_id=job.id,
        source_id=source.id,
        max_depth=current_app.config["CRAWL_MAX_DEPTH"],
        max_pages=current_app.config["CRAWL_MAX_PAGES"],
        crawl_delay=current_app.config["CRAWL_DELAY_SECONDS"]
    )

    return jsonify({
        "source": source.to_dict(),
        "job": job.to_dict(),
        "message": "Knowledge source registered and ingestion started."
    }), 201

@knowledge_bp.route("/sources/<int:source_id>/refresh", methods=["POST"])
def refresh_source(source_id):
    session = get_db()
    source = session.query(KnowledgeSource).get(source_id)
    if not source:
        raise NotFoundError(f"Knowledge source {source_id} not found.")

    # Create new ingestion job
    job = IngestionJob(source_id=source.id, status="pending")
    session.add(job)
    session.commit()

    IngestionService.start_background_ingestion(
        app=current_app._get_current_object(),
        job_id=job.id,
        source_id=source.id,
        max_depth=current_app.config["CRAWL_MAX_DEPTH"],
        max_pages=current_app.config["CRAWL_MAX_PAGES"],
        crawl_delay=current_app.config["CRAWL_DELAY_SECONDS"]
    )

    return jsonify({"job": job.to_dict(), "message": "Reindexing job initiated."}), 200

@knowledge_bp.route("/sources/<int:source_id>", methods=["DELETE"])
def delete_source(source_id):
    session = get_db()
    source = session.query(KnowledgeSource).get(source_id)
    if not source:
        raise NotFoundError(f"Knowledge source {source_id} not found.")

    session.delete(source)
    session.commit()
    return jsonify({"message": f"Source {source_id} and all associated documents deleted."}), 200

@knowledge_bp.route("/jobs", methods=["GET"])
def list_jobs():
    session = get_db()
    jobs = session.query(IngestionJob).order_by(IngestionJob.id.desc()).limit(20).all()
    return jsonify({"jobs": [j.to_dict() for j in jobs]}), 200

@knowledge_bp.route("/jobs/<int:job_id>", methods=["GET"])
def get_job(job_id):
    session = get_db()
    job = session.query(IngestionJob).get(job_id)
    if not job:
        raise NotFoundError(f"Ingestion job {job_id} not found.")
    return jsonify(job.to_dict()), 200
