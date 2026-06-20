"""Flask application factory (BSc-scope build)."""
from __future__ import annotations

import logging

from flask import Flask, jsonify

from app.config import CONFIG_MAP, get_config
from app.extensions import bcrypt, cors, db, jwt, limiter, migrate


def create_app(config_object=None) -> Flask:
    app = Flask(__name__)
    if isinstance(config_object, str):
        config_object = CONFIG_MAP.get(config_object.lower(), get_config())
    app.config.from_object(config_object or get_config())

    logging.basicConfig(level=app.config.get("LOG_LEVEL", "INFO"))

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["ALLOWED_ORIGINS"]}},
        supports_credentials=False,
        methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    limiter.init_app(app)

    # Import models so SQLAlchemy registers them.
    from app import models  # noqa: F401

    # Auto-create tables in dev (sqlite). Prod uses alembic migrations.
    if app.config.get("DEBUG") and not app.config.get("TESTING"):
        db_uri = str(app.config.get("SQLALCHEMY_DATABASE_URI", ""))
        if db_uri.startswith("sqlite"):
            with app.app_context():
                db.create_all()

    # JWT blocklist
    from app.utils.security import is_token_revoked

    @jwt.token_in_blocklist_loader
    def _check_token_revoked(_jwt_header, jwt_payload):
        return is_token_revoked(jwt_payload["jti"])

    @jwt.revoked_token_loader
    def _revoked_token_response(_jwt_header, _jwt_payload):
        return jsonify({"error": "token_revoked"}), 401

    @jwt.expired_token_loader
    def _expired_token_response(_jwt_header, _jwt_payload):
        return jsonify({"error": "token_expired"}), 401

    @jwt.invalid_token_loader
    def _invalid_token_response(reason):
        return jsonify({"error": "invalid_token", "reason": reason}), 422

    @jwt.unauthorized_loader
    def _missing_token_response(reason):
        return jsonify({"error": "authorization_required", "reason": reason}), 401

    # Register blueprints
    from app.api import (
        admin, auth, evaluation, health, manager, notifications, scores, training,
    )

    for module in (auth, training, scores, manager, admin, health, notifications, evaluation):
        if hasattr(module, "bp"):
            app.register_blueprint(module.bp)

    # Background scheduler  initialised but only auto-starts when ENABLE_SCHEDULER=true.
    if not app.config.get("TESTING"):
        from app.services.scheduler import init_scheduler
        init_scheduler(app)

    @app.get("/")
    def index():
        return jsonify({"app": app.config.get("APP_NAME", "AHRIP"), "status": "ok"})

    from werkzeug.exceptions import HTTPException

    @app.errorhandler(HTTPException)
    def _json_http_error(err: HTTPException):
        return jsonify({
            "error": err.name.lower().replace(" ", "_"),
            "message": err.description,
            "status": err.code,
        }), err.code

    @app.errorhandler(Exception)
    def _json_server_error(err: Exception):  # noqa: BLE001
        app.logger.exception("Unhandled error: %s", err)
        return jsonify({"error": "internal_error", "status": 500}), 500

    return app
