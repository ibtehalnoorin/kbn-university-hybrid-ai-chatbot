from flask import jsonify

class APIError(Exception):
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["error"] = self.message
        rv["status"] = "error"
        rv["code"] = self.status_code
        return rv

class NotFoundError(APIError):
    def __init__(self, message="Resource not found", payload=None):
        super().__init__(message, status_code=404, payload=payload)

class ValidationError(APIError):
    def __init__(self, message="Invalid request parameters", payload=None):
        super().__init__(message, status_code=422, payload=payload)

class ServiceUnavailableError(APIError):
    def __init__(self, message="External service unavailable", payload=None):
        super().__init__(message, status_code=503, payload=payload)

def register_error_handlers(app):
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(404)
    def handle_404(error):
        return jsonify({"error": "Endpoint not found", "status": "error", "code": 404}), 404

    @app.errorhandler(500)
    def handle_500(error):
        app.logger.error(f"Internal server error: {error}")
        return jsonify({"error": "An internal server error occurred", "status": "error", "code": 500}), 500
