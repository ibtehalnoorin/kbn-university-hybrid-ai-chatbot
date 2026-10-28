import uuid
from flask import request, current_app
from app.utils.security import generate_session_token, verify_session_token

def get_session_id():
    """
    Extracts and verifies guest session ID from request header 'X-Session-Token'
    or 'X-Session-Id'. If token is invalid or missing, generates a new session ID.
    """
    secret = current_app.config.get("SECRET_KEY", "default-dev-secret")
    token = request.headers.get("X-Session-Token") or request.headers.get("X-Session-Id")

    if token:
        try:
            if "." in token:
                return verify_session_token(secret, token)
            # Accept valid alphanumeric, hyphenated session strings
            clean = token.strip()
            if clean and len(clean) <= 128 and all(c.isalnum() or c in "-_" for c in clean):
                return clean
        except Exception:
            pass

    # Generate new random session ID
    return str(uuid.uuid4())
