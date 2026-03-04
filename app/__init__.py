"""Flask app factory. Clean Architecture: controllers use services, services use repositories."""
import hashlib
import os
from datetime import timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.config import get_config

db = SQLAlchemy()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address)


def _ensure_jwt_key_length(key: str) -> str:
    """Đảm bảo JWT secret >= 32 bytes để tránh InsecureKeyLengthWarning (RFC 7518)."""
    if len(key) >= 32:
        return key
    return hashlib.sha256(key.encode()).hexdigest()


def create_app(config_overrides: dict | None = None) -> Flask:
    """Create and configure Flask app."""
    app = Flask(__name__)
    config = get_config()
    app.config["SECRET_KEY"] = config.secret_key
    app.config["SQLALCHEMY_DATABASE_URI"] = config.database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = _ensure_jwt_key_length(config.jwt_secret_key or "default-change-me")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=config.jwt_access_expires)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(seconds=config.jwt_refresh_expires)
    app.config["JWT_ALGORITHM"] = config.jwt_algorithm
    if config_overrides:
        app.config.update(config_overrides)

    db.init_app(app)
    migrate.init_app(app, db)
    cors_origins_raw = os.getenv("CORS_ORIGINS", "*").strip()
    cors_origins = [o.strip() for o in cors_origins_raw.split(",") if o.strip()]
    CORS(app, supports_credentials=True, origins=cors_origins if cors_origins else "*")
    limiter.init_app(app)

    from app.controllers import register_blueprints
    register_blueprints(app)

    return app
