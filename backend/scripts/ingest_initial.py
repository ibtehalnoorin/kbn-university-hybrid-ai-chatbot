import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app import create_app
from app.extensions import get_db
from app.models.knowledge_source import KnowledgeSource
from app.models.ingestion_job import IngestionJob
from app.services.rag.embeddings import EmbeddingService
from app.services.ingestion.ingestion_service import IngestionService

def run_initial():
    app = create_app()
    with app.app_context():
        session = get_db()
        source = session.query(KnowledgeSource).filter_by(base_url="https://www.kbn.university/").first()
        if not source:
            source = KnowledgeSource(
                base_url="https://www.kbn.university/",
                name="KBN University Official Website",
                description="Official web portal of Khaja Bandanawaz University, Kalaburagi."
            )
            session.add(source)
            session.commit()

        print(f"Starting initial crawl for: {source.base_url} (limit: 15 key pages)...")
        job = IngestionJob(source_id=source.id, status="pending")
        session.add(job)
        session.commit()

        emb_service = EmbeddingService(
            base_url=app.config["OLLAMA_BASE_URL"],
            model=app.config["OLLAMA_EMBEDDING_MODEL"],
            dimension=app.config["VECTOR_DIMENSION"]
        )
        service = IngestionService(session, emb_service)
        service.run_ingestion_sync(
            job_id=job.id,
            source_id=source.id,
            max_depth=1,
            max_pages=15,
            crawl_delay=0.3
        )

        job = session.query(IngestionJob).get(job.id)
        print(f"Ingestion finished with status: {job.status}")
        print(f"Pages Discovered: {job.pages_discovered}, Processed: {job.pages_processed}, Failed: {job.pages_failed}")
        if job.error_message:
            print(f"Error: {job.error_message}")

if __name__ == "__main__":
    run_initial()
