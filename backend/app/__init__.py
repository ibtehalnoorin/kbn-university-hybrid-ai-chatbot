from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.extensions import init_db, db_session
from app.utils.logging_config import setup_logging
from app.utils.errors import register_error_handlers
from app.api import chat_bp, conversations_bp, knowledge_bp, memories_bp, health_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Logging
    setup_logging(app)

    # Database
    init_db(app)

    # CORS
    CORS(app, origins=app.config["CORS_ORIGINS"], expose_headers=["X-Session-Id"])

    # Error handling
    register_error_handlers(app)

    # Blueprints
    app.register_blueprint(chat_bp)
    app.register_blueprint(conversations_bp)
    app.register_blueprint(knowledge_bp)
    app.register_blueprint(memories_bp)
    app.register_blueprint(health_bp)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if db_session:
            db_session.remove()

    return app
