import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app import create_app
from app.extensions import get_db
from app.models.knowledge_source import KnowledgeSource

def initialize():
    app = create_app()
    with app.app_context():
        session = get_db()
        print("Initializing database tables...")
        # Check if default source exists
        kbn_url = "https://www.kbn.university/"
        existing = session.query(KnowledgeSource).filter_by(base_url=kbn_url).first()
        if not existing:
            source = KnowledgeSource(
                base_url=kbn_url,
                name="KBN University Official Website",
                description="Official web portal of Khaja Bandanawaz University, Kalaburagi."
            )
            session.add(source)
            session.commit()
            print(f"Registered initial knowledge source: {kbn_url}")
        else:
            print(f"Knowledge source already registered: {kbn_url}")
        print("Database initialization complete.")

if __name__ == "__main__":
    initialize()
