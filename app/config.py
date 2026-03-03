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

    # JWT
    jwt_secret_key: str = ""
    jwt_access_expires: int = 3600
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
        database_url=database_url,
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        celery_broker_url=os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0")),
        celery_result_backend=os.getenv("CELERY_RESULT_BACKEND", os.getenv("REDIS_URL", "redis://localhost:6379/0")),
    )
