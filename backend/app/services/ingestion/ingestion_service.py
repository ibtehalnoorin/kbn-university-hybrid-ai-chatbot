import threading
import datetime
import logging
from sqlalchemy.orm import Session
from app.extensions import get_db
from app.models.knowledge_source import KnowledgeSource
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.ingestion_job import IngestionJob
from app.services.ingestion.crawler import Crawler
from app.services.ingestion.content_cleaner import ContentCleaner
from app.services.rag.chunker import RecursiveChunker
from app.services.rag.embeddings import EmbeddingService

logger = logging.getLogger(__name__)

class IngestionService:
    def __init__(self, session: Session, embedding_service: EmbeddingService):
        self.session = session
        self.embedding_service = embedding_service
        self.chunker = RecursiveChunker()

    def run_ingestion_sync(
        self,
        job_id: int,
        source_id: int,
        max_depth: int = 2,
        max_pages: int = 30,
        crawl_delay: float = 0.5
    ) -> None:
        """Runs the ingestion job synchronously."""
        job = self.session.query(IngestionJob).get(job_id)
        source = self.session.query(KnowledgeSource).get(source_id)

        if not job or not source:
            logger.error(f"Cannot run ingestion: Job {job_id} or Source {source_id} not found.")
            return

        job.status = "running"
        job.started_at = datetime.datetime.utcnow()
        self.session.commit()

        discovered_count = 0
        processed_count = 0
        failed_count = 0

        try:
            crawler = Crawler(
                base_url=source.base_url,
                max_depth=max_depth,
                max_pages=max_pages,
                crawl_delay=crawl_delay
            )

            for url, html_content, error in crawler.crawl():
                discovered_count += 1
                job.pages_discovered = discovered_count
                self.session.commit()

                if error or not html_content:
                    failed_count += 1
                    job.pages_failed = failed_count
                    self.session.commit()
                    continue

                # Clean content
                cleaned = ContentCleaner.clean_html(html_content)
                text_content = cleaned["cleaned_text"]
                content_hash = cleaned["content_hash"]
                title = cleaned["title"]

                if not text_content or len(text_content) < 50:
                    # Skip empty/stub pages
                    continue

                # Check if document already exists
                existing_doc = self.session.query(Document).filter_by(url=url).first()

                if existing_doc:
                    if existing_doc.content_hash == content_hash:
                        # Unchanged document
                        processed_count += 1
                        job.pages_processed = processed_count
                        self.session.commit()
                        continue
                    else:
                        # Document changed, remove old chunks
                        self.session.query(DocumentChunk).filter_by(document_id=existing_doc.id).delete()
                        existing_doc.content = text_content
                        existing_doc.content_hash = content_hash
                        existing_doc.title = title
                        existing_doc.updated_at = datetime.datetime.utcnow()
                        doc = existing_doc
                else:
                    doc = Document(
                        source_id=source.id,
                        url=url,
                        title=title,
                        content=text_content,
                        content_hash=content_hash
                    )
                    self.session.add(doc)
                    self.session.flush()

                # Chunk document
                chunks_data = self.chunker.chunk_text(text_content)
                for c in chunks_data:
                    emb = self.embedding_service.get_embedding(c["content"])
                    chunk = DocumentChunk(
                        document_id=doc.id,
                        chunk_index=c["chunk_index"],
                        content=c["content"],
                        char_count=c["char_count"],
                        embedding=emb
                    )
                    self.session.add(chunk)

                processed_count += 1
                job.pages_processed = processed_count
                self.session.commit()

            # Job finished
            job.status = "completed"
            job.completed_at = datetime.datetime.utcnow()
            source.total_pages = self.session.query(Document).filter_by(source_id=source.id).count()
            source.last_crawled_at = datetime.datetime.utcnow()
            self.session.commit()

        except Exception as e:
            logger.exception(f"Ingestion job {job_id} encountered fatal error: {e}")
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.datetime.utcnow()
            self.session.commit()

    @staticmethod
    def start_background_ingestion(
        app,
        job_id: int,
        source_id: int,
        max_depth: int = 2,
        max_pages: int = 30,
        crawl_delay: float = 0.5
    ):
        """Spawns background thread with its own scoped DB session to execute ingestion."""
        def worker():
            with app.app_context():
                session = get_db()
                try:
                    emb_service = EmbeddingService(
                        base_url=app.config["OLLAMA_BASE_URL"],
                        model=app.config["OLLAMA_EMBEDDING_MODEL"],
                        dimension=app.config["VECTOR_DIMENSION"]
                    )
                    ingest_service = IngestionService(session, emb_service)
                    ingest_service.run_ingestion_sync(
                        job_id=job_id,
                        source_id=source_id,
                        max_depth=max_depth,
                        max_pages=max_pages,
                        crawl_delay=crawl_delay
                    )
                finally:
                    session.remove()

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return thread
