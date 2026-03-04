"""Auth business logic: register, login, verify email. No DB in controller."""

from app import db
from app.repositories.user_repository import UserRepository
from app.services.email_service import send_verification_email
from app.utils.auth import (
    check_password,
    create_refresh_token_for_user,
    create_token,
    create_verify_email_token,
    decode_verify_email_token,
    hash_password,
)


class AuthService:
    @staticmethod
    def register(email: str, password: str, username: str) -> tuple[dict, str | None]:
        if UserRepository.get_by_email(email):
            return {}, "Email already registered"
        if UserRepository.get_by_username(username):
            return {}, "Username already taken"
        password_hash = hash_password(password)
        role_name = "user"
        user = UserRepository.create(email, password_hash, username, role_name)
        db.session.commit()
        verify_token = create_verify_email_token(user.id)
        send_verification_email(email, username, verify_token)
        return {"message": "Đăng ký thành công. Vui lòng xác thực email."}, None

    @staticmethod
    def login(username: str, password: str) -> tuple[dict | None, str | None]:
        user = UserRepository.get_by_username(username)
        if not user or not check_password(password, user.password_hash):
            return None, "Invalid username or password"
        if not user.verified:
            return None, "Email chưa được xác thực. Vui lòng kiểm tra hộp thư."
        if user.banned:
            return None, "Account is banned"
        role = user.role
        access_token = create_token(user.id, role.name)
        refresh_token = create_refresh_token_for_user(user.id)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": str(user.id),
        }, None

    @staticmethod
    def refresh(user_id_str: str) -> tuple[dict | None, str | None]:
        """Tạo access token mới từ refresh token (identity = user_id)."""
        from uuid import UUID

        try:
            user_id = UUID(user_id_str)
        except ValueError:
            return None, "Invalid token"
        user = UserRepository.get_by_id(user_id)
        if not user or user.banned:
            return None, "User not found or banned"
        role = user.role
        access_token = create_token(user.id, role.name)
        return {"access_token": access_token, "token_type": "bearer", "user_id": str(user.id)}, None

    @staticmethod
    def verify_email(token: str) -> tuple[dict, str | None]:
        user_id = decode_verify_email_token(token)
        if not user_id:
            return {}, "Token không hợp lệ hoặc đã hết hạn"
        if not UserRepository.set_verified(user_id):
            return {}, "User không tồn tại"
        db.session.commit()
        return {"message": "Email đã được xác thực. Bạn có thể đăng nhập."}, None
