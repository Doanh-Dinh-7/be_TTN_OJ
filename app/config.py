"""Application configuration. All secrets from environment."""
import os
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env vào os.environ (tìm từ thư mục backend) để script và flask CLI dùng đúng DATABASE_URL
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_backend_dir, ".env"))


def _ensure_supabase_ssl(url: str) -> str:
    """Supabase yêu cầu SSL. Thêm sslmode=require nếu chưa có."""
    if "supabase" not in url.lower():
        return url
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    if "sslmode" in query:
        return url
    query["sslmode"] = ["require"]
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


class Config(BaseSettings):
    """App config from env. Never hardcode credentials."""

    # Flask
    secret_key: str = ""
    env: str = "development"
    debug: bool = False

    # Database (PostgreSQL) - dùng Supabase: paste Connection string từ Dashboard
    database_url: str = "postgresql://postgres:postgres@localhost:5432/ttn_oj"

    # JWT (access token 24h, refresh token dài hơn để gia hạn)
    jwt_secret_key: str = ""
    jwt_access_expires: int = 86400  # 24 giờ (giây)
    jwt_refresh_expires: int = 604800  # 7 ngày (giây)
    jwt_algorithm: str = "HS256"

    # Redis & Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # Judge (Docker)
    judge_memory_limit_mb: int = 256
    judge_cpu_period: int = 100000
    judge_cpu_quota: int = 50000
    judge_timeout_seconds: int = 5
    judge_network_disabled: bool = True

    # Rate limit (submission API)
    submission_rate_limit: str = "10 per minute"

    # Mail (xác thực email)
    mail_server: str = "localhost"
    mail_port: int = 587
    mail_use_tls: bool = True
    mail_username: str = ""
    mail_password: str = ""
    mail_default_sender: str = "noreply@ttnoj.local"
    # URL frontend để dựng link xác thực (ví dụ: https://oj.example.com)
    frontend_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


def get_config() -> Config:
    """Load config from environment. Supabase: set DATABASE_URL từ Dashboard."""
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ttn_oj")
    database_url = _ensure_supabase_ssl(database_url)
    return Config(
        secret_key=os.getenv("SECRET_KEY", "dev-secret-change-in-production"),
        jwt_secret_key=os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "jwt-secret")),
        jwt_access_expires=int(os.getenv("JWT_ACCESS_EXPIRES", "86400")),
        jwt_refresh_expires=int(os.getenv("JWT_REFRESH_EXPIRES", "604800")),
        database_url=database_url,
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        celery_broker_url=os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0")),
        celery_result_backend=os.getenv("CELERY_RESULT_BACKEND", os.getenv("REDIS_URL", "redis://localhost:6379/0")),
        mail_server=os.getenv("MAIL_SERVER", "localhost"),
        mail_port=int(os.getenv("MAIL_PORT", "587")),
        mail_use_tls=os.getenv("MAIL_USE_TLS", "true").lower() in ("1", "true", "yes"),
        mail_username=os.getenv("MAIL_USERNAME", ""),
        mail_password=os.getenv("MAIL_PASSWORD", ""),
        mail_default_sender=os.getenv("MAIL_DEFAULT_SENDER", "noreply@ttnoj.local"),
        frontend_url=os.getenv("FRONTEND_URL", "http://localhost:3000"),
    )
