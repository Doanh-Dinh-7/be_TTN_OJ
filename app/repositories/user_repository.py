"""User repository: DB access only."""

from uuid import UUID

from sqlalchemy import or_

from app import db
from app.models import Role, User


class UserRepository:
    @staticmethod
    def get_by_id(user_id: UUID) -> User | None:
        return db.session.get(User, user_id)

    @staticmethod
    def get_by_email(email: str) -> User | None:
        return db.session.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_username(username: str) -> User | None:
        return db.session.query(User).filter(User.username == username).first()

    @staticmethod
    def create(email: str, password_hash: str, username: str, role_name: str) -> User:
        role = db.session.query(Role).filter(Role.name == role_name).first()
        if not role:
            raise ValueError(f"Role {role_name} not found")
        user = User(
            email=email,
            password_hash=password_hash,
            username=username,
            role_id=role.id,
            verified=True,  # Note: tạm thời để True để test
        )
        db.session.add(user)
        db.session.flush()
        return user

    @staticmethod
    def set_verified(user_id: UUID) -> bool:
        """Đánh dấu user đã xác thực email. Trả về True nếu cập nhật thành công."""
        user = db.session.get(User, user_id)
        if not user:
            return False
        user.verified = True
        db.session.flush()
        return True

    @staticmethod
    def get_role_by_name(name: str) -> Role | None:
        return db.session.query(Role).filter(Role.name == name).first()

    @staticmethod
    def list_users(skip: int = 0, limit: int = 50) -> list[User]:
        return (
            db.session.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()
        )

    @staticmethod
    def list_users_filtered(
        skip: int = 0,
        limit: int = 50,
        status: str | None = None,
        role: str | None = None,
        verified: bool | None = None,
        keyword: str | None = None,
    ) -> list[User]:
        """Danh sách user có lọc."""
        q = db.session.query(User)
        if status == "locked":
            q = q.filter(User.banned.is_(True))
        elif status == "active":
            q = q.filter(User.banned.is_(False))
        if role and role.strip().lower() in ("admin", "user"):
            q = q.join(Role).filter(Role.name == role.strip().lower())
        if verified is not None:
            q = q.filter(User.verified.is_(verified))
        if keyword and keyword.strip():
            term = f"%{keyword.strip()}%"
            q = q.filter(
                or_(
                    User.username.ilike(term),
                    User.email.ilike(term),
                )
            )
        return q.order_by(User.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_banned(user_id: UUID, banned: bool) -> bool:
        """Set user banned (lock/unlock). Không xóa submission history."""
        user = db.session.get(User, user_id)
        if not user:
            return False
        user.banned = banned
        db.session.flush()
        return True

    @staticmethod
    def update_role(user_id: UUID, role_id: UUID) -> bool:
        """Đổi role user. Có hiệu lực ngay (DB); token cũ cần refresh để lấy role mới."""
        user = db.session.get(User, user_id)
        if not user:
            return False
        user.role_id = role_id
        db.session.flush()
        return True

    @staticmethod
    def count_admins() -> int:
        """Số user có role admin (dùng để chặn self-demote admin cuối cùng)."""
        admin_role = db.session.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            return 0
        return db.session.query(User).filter(User.role_id == admin_role.id).count()
