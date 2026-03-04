"""JWT and RBAC. Password hashing with bcrypt."""

from datetime import timedelta
from functools import wraps
from uuid import UUID

import bcrypt
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_jwt,
    get_jwt_identity,
    verify_jwt_in_request,
)

from app import db
from app.models import User

# Claim type cho token xác thực email (phân biệt với access token)
VERIFY_EMAIL_CLAIM = "verify_email"


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
    """Create JWT access token (24h) with identity and role."""
    return create_access_token(
        identity=str(user_id),
        additional_claims={"role": role_name},
    )


def create_refresh_token_for_user(user_id: UUID) -> str:
    """Create JWT refresh token (dài hạn, dùng để lấy access token mới)."""
    return create_refresh_token(identity=str(user_id))


def create_verify_email_token(user_id: UUID) -> str:
    """Tạo JWT token cho xác thực email, hết hạn sau 15 phút. Ký bằng JWT secret."""
    return create_access_token(
        identity=str(user_id),
        additional_claims={"type": VERIFY_EMAIL_CLAIM},
        expires_delta=timedelta(minutes=15),
    )


def decode_verify_email_token(token: str) -> UUID | None:
    """Giải mã token xác thực email. Trả về user_id nếu hợp lệ, None nếu hết hạn/sai."""
    try:
        decoded = decode_token(token)
        if decoded.get("type") != VERIFY_EMAIL_CLAIM:
            return None
        return UUID(decoded["sub"])
    except Exception:
        return None


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
