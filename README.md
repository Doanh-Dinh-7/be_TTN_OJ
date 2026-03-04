# TTN OJ Backend

Flask REST API. Clean Architecture: Controller → Service → Repository → Models.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt --no-cache-dir
cp .example.env .env     # edit .env với secrets
```

## Database (PostgreSQL / Neon)

- **Neon**: Vào [Dashboard](https://neon.tech) → Project → **Connection string** → copy URI (dạng `postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require`). Dán vào `.env`: `DATABASE_URL=<chuỗi vừa copy>`. Ứng dụng tự thêm `sslmode=require` nếu URI chưa có (kết nối cloud).
- **PostgreSQL local**: `DATABASE_URL=postgresql://user:pass@localhost:5432/ttn_oj`

Migrations:

```bash
flask db init
flask db migrate -m "Initial"
flask db upgrade
```

Tạo roles: `python scripts/create_roles.py`  
Tạo tài khoản ADMIN (email: admin@ttnoj.local, password: 12341234): `python scripts/create_admin.py`

## Run

- API: `python run.py` (or `flask run`)
- Celery worker (judge): `celery -A app.celery_app:celery_app worker -l info`

Requires Redis and PostgreSQL (see docker-compose in project root).

## Check trước khi push (giống CI)

Chạy trong thư mục gốc repo backend (đã activate venv nếu dùng):

```bash
# 1. Lint (Ruff)
pip install ruff
ruff check .
ruff format --check .

# 2. Cài đặt + kiểm tra app load được (không cần DB/Redis thật)
pip install -r requirements.txt
set SECRET_KEY=ci-secret-key-min-32-chars-long
set JWT_SECRET_KEY=ci-jwt-secret-key-min-32-chars
set DATABASE_URL=postgresql://u:p@localhost/dummy?sslmode=require
set REDIS_URL=redis://localhost:6379/0
set CELERY_BROKER_URL=redis://localhost:6379/0
set CELERY_RESULT_BACKEND=redis://localhost:6379/0
python -c "from app import create_app; create_app()"
```

- **Linux/macOS:** thay `set VAR=value` bằng `export VAR=value`.
- **PowerShell:** dùng `$env:SECRET_KEY = "ci-secret-key-min-32-chars-long"` (và tương tự các biến khác).

Nếu tất cả lệnh trên chạy xong không lỗi thì CI trên GitHub thường cũng pass.

## Deploy (backend + frontend là hai repo riêng)

Xem [DEPLOY.md](DEPLOY.md) để deploy Backend lên Render + Judge lên Fly.io (Neon, Render Redis / Upstash).
