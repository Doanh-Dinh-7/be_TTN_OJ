"""Admin API: nhóm route theo resource. Chỉ Admin mới được truy cập."""

from app.controllers.admin.problems import admin_problems_bp
from app.controllers.admin.submissions import admin_submissions_bp
from app.controllers.admin.users import admin_users_bp

ADMIN_URL_PREFIX = "/api/admin"

__all__ = [
    "admin_problems_bp",
    "admin_submissions_bp",
    "admin_users_bp",
    "register_admin_blueprints",
]


def register_admin_blueprints(app) -> None:
    """Đăng ký tất cả admin blueprints với prefix /api/admin."""
    app.register_blueprint(admin_submissions_bp, url_prefix=ADMIN_URL_PREFIX)
    app.register_blueprint(admin_problems_bp, url_prefix=ADMIN_URL_PREFIX)
    app.register_blueprint(admin_users_bp, url_prefix=ADMIN_URL_PREFIX)
