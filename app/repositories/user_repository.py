"""User repository: DB access only."""
from uuid import UUID
from app import db
from app.models import User, Role


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
            verified=False,
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
