"""JWT and RBAC. Password hashing with bcrypt."""
import bcrypt
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    get_jwt,
    verify_jwt_in_request,
)
from flask_jwt_extended import JWTManager
from functools import wraps
from uuid import UUID
from app import db
from app.models import User, Role


def init_jwt(app) -> None:
    """Initialize JWT on app."""
    JWTManager(app)

    @app.context_processor
    def _():
        return {}


def hash_password(password: str) -> str:
    """Hash password with bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, password_hash: str) -> bool:
    """Verify password against bcrypt hash."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_token(user_id: UUID, role_name: str) -> str:
    """Create JWT access token with identity and role."""
    return create_access_token(
        identity=str(user_id),
        additional_claims={"role": role_name},
    )


def get_current_user_id() -> UUID:
    """Current user UUID from JWT."""
    return UUID(get_jwt_identity())


def get_current_user() -> User | None:
    """Load current user from DB."""
    uid = get_jwt_identity()
    if not uid:
        return None
    return db.session.get(User, UUID(uid))


def require_role(*allowed_roles: str):
    """Decorator: require JWT and one of allowed roles (RBAC)."""
    def wrapper(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get("role")
            if role not in allowed_roles:
                return {"message": "Forbidden"}, 403
            return fn(*args, **kwargs)
        return inner
    return wrapper


def admin_required(fn):
    """Require Admin role."""
    return require_role("admin")(fn)


def user_required(fn):
    """Require User (contestant) or Admin."""
    return require_role("admin", "user")(fn)
