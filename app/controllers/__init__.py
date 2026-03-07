"""Controllers: API layer only. Delegate to services."""

from app.controllers.admin import register_admin_blueprints
from app.controllers.auth_controller import auth_bp
from app.controllers.contest_controller import contest_bp
from app.controllers.submission_controller import submission_bp


def register_blueprints(app) -> None:
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(contest_bp, url_prefix="/api/contests")
    app.register_blueprint(submission_bp, url_prefix="/api/submissions")
    register_admin_blueprints(app)
    from app.utils.auth import init_jwt

    init_jwt(app)
