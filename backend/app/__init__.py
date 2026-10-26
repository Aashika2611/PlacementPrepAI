import os
from flask import Flask, jsonify
from flask_cors import CORS

from config.config import Config
from app.extensions import db, jwt


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config["FRONTEND_ORIGIN"]}})

    # --- Blueprints ---
    from app.routes.auth import auth_bp
    from app.routes.profile import profile_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.applications import applications_bp
    from app.routes.resume import resume_bp
    from app.routes.interview import interview_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(applications_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(interview_bp)

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "ok",
            "ai_enabled": app.config.get("AI_ENABLED", False),
        }), 200

    # --- Error handlers ---
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed."}), 405

    @app.errorhandler(413)
    def too_large(e):
        max_mb = app.config.get("MAX_UPLOAD_MB", 5)
        return jsonify({"error": f"File too large. Maximum upload size is {max_mb}MB."}), 413

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "An unexpected server error occurred."}), 500

    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        return jsonify({"error": "Missing or invalid authentication token."}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return jsonify({"error": "Invalid authentication token."}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Session expired. Please log in again."}), 401

    return app
