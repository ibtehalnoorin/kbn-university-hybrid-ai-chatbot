from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

Base = declarative_base()
engine = None
db_session = None

def init_db(app):
    global engine, db_session
    engine = create_engine(
        app.config["SQLALCHEMY_DATABASE_URI"],
        **app.config.get("SQLALCHEMY_ENGINE_OPTIONS", {})
    )
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    Base.query = db_session.query_property()
    
    # Enable pgvector extension if postgresql
    if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgresql"):
        try:
            with engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
        except Exception as e:
            app.logger.warning(f"Could not enable pgvector extension automatically: {e}")
            
    # Create all tables if they do not exist
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    return db_session

def get_db():
    return db_session
