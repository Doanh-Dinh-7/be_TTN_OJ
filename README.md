# TTN OJ Backend

Flask REST API. Clean Architecture: Controller → Service → Repository → Models.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
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
