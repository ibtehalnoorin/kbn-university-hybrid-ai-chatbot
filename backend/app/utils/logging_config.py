import logging
import sys

def setup_logging(app):
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] in %(module)s: %(message)s"
    )
    handler.setFormatter(formatter)
    
    app.logger.setLevel(logging.INFO if not app.debug else logging.DEBUG)
    if not app.logger.handlers:
        app.logger.addHandler(handler)
