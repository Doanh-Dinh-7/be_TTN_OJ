"""
Admin user management: list, lock, unlock, change role.
Business rules: no self-demote last admin.
"""

from uuid import UUID

from app import db
from app.repositories.user_repository import UserRepository


class AdminUserService:
    @staticmethod
    def list_users(skip: int = 0, limit: int = 50) -> list[dict]:
        """
        Danh sách user cho Admin.
        Trả về id, email, username, verified, role name, locked (banned).
        """
        users = UserRepository.list_users(skip=skip, limit=limit)
        return [
            {
                "id": str(u.id),
                "email": u.email,
                "username": u.username,
                "verified": u.verified,
                "role": u.role.name,
                "locked": u.banned,
            }
            for u in users
        ]

    @staticmethod
    def lock_user(user_id: UUID) -> tuple[bool, str | None]:
        """Khóa user (banned=True). User không login được. Không xóa submission history."""
        user = UserRepository.get_by_id(user_id)
        if not user:
            return False, "User not found"
        UserRepository.update_banned(user_id, True)
        db.session.commit()
        return True, None

    @staticmethod
    def unlock_user(user_id: UUID) -> tuple[bool, str | None]:
        """Mở khóa user (banned=False)."""
        user = UserRepository.get_by_id(user_id)
        if not user:
            return False, "User not found"
        UserRepository.update_banned(user_id, False)
        db.session.commit()
        return True, None

    @staticmethod
    def set_role(user_id: UUID, role_name: str, current_admin_id: UUID) -> tuple[bool, str | None]:
        """Đổi role user. Có hiệu lực ngay (DB). Không cho self-demote Admin cuối cùng."""
        if role_name not in ("admin", "user"):
            return False, "Invalid role"
        user = UserRepository.get_by_id(user_id)
        if not user:
            return False, "User not found"
        role = UserRepository.get_role_by_name(role_name)
        if not role:
            return False, "Role not found"
        # Demote admin → user: không cho demote admin cuối cùng (kể cả self hay do admin khác)
        if user.role.name == "admin" and role_name == "user":
            admin_count = UserRepository.count_admins()
            if admin_count <= 1:
                return False, "Cannot demote the last admin"
        UserRepository.update_role(user_id, role.id)
        db.session.commit()
        return True, None
