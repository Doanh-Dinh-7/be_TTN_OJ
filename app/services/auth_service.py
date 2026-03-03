"""Auth business logic: register, login. No DB in controller."""
from app.repositories.user_repository import UserRepository
from app.utils.auth import hash_password, check_password, create_token


class AuthService:
    @staticmethod
    def register(email: str, password: str, username: str) -> tuple[dict, str | None]:
        if UserRepository.get_by_email(email):
            return {}, "Email already registered"
        password_hash = hash_password(password)
        role_name = "user"
        user = UserRepository.create(email, password_hash, username, role_name)
        token = create_token(user.id, role_name)
        return {"access_token": token, "token_type": "bearer", "user_id": str(user.id)}, None

    @staticmethod
    def login(email: str, password: str) -> tuple[dict | None, str | None]:
        user = UserRepository.get_by_email(email)
        if not user or not check_password(password, user.password_hash):
            return None, "Invalid email or password"
        if user.banned:
            return None, "Account is banned"
        role = user.role
        token = create_token(user.id, role.name)
        return {"access_token": token, "token_type": "bearer", "user_id": str(user.id)}, None
