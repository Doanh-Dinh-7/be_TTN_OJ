"""Flask app factory. Clean Architecture: controllers use services, services use repositories."""
import os
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


def create_app(config_overrides: dict | None = None) -> Flask:
    """Create and configure Flask app."""
    app = Flask(__name__)
    config = get_config()
    app.config["SECRET_KEY"] = config.secret_key
    app.config["SQLALCHEMY_DATABASE_URI"] = config.database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = config.jwt_secret_key
    app.config["JWT_ACCESS_EXPIRES"] = config.jwt_access_expires
    app.config["JWT_ALGORITHM"] = config.jwt_algorithm
    if config_overrides:
        app.config.update(config_overrides)

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, supports_credentials=True, origins=os.getenv("CORS_ORIGINS", "*").split(","))
    limiter.init_app(app)

    from app.controllers import register_blueprints
    register_blueprints(app)

    return app
