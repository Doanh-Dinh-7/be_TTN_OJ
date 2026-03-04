# TTN OJ Backend

Flask REST API. Clean Architecture: Controller → Service → Repository → Models.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .example.env .env     # edit .env với secrets
```

## Database (PostgreSQL / Supabase)

- **Supabase**: Vào [Dashboard](https://supabase.com/dashboard) → Project → **Settings** → **Database**.
  - Chọn tab **Connection pooling** (hoặc **URI**).
  - Chọn **Transaction** mode → copy **Connection string** (dạng `postgresql://postgres.[ref]:[password]@aws-0-xx.pooler.supabase.com:6543/postgres`).
  - Dán vào `.env`: `DATABASE_URL=<chuỗi vừa copy>`. Ứng dụng tự thêm `sslmode=require` nếu cần.
  - **Không dùng** "Direct connection" (host `db.xxx.supabase.co`) khi gặp lỗi DNS (xem Troubleshooting).
- **PostgreSQL local**: `DATABASE_URL=postgresql://user:pass@localhost:5432/ttn_oj`

### Troubleshooting: "could not translate host name ... to address: Name or service not known"

Lỗi do DNS không phân giải được host Supabase (thường gặp với **Direct** `db.xxx.supabase.co`). Cách xử lý:

1. Dùng **Connection pooler** thay vì Direct: Dashboard → **Settings** → **Database** → **Connection pooling** → **Transaction** → copy URI (host sẽ là `...pooler.supabase.com`, port **6543**). Cập nhật `DATABASE_URL` trong `.env` bằng URI này.
2. Kiểm tra mạng: có internet, thử tắt VPN/proxy nếu đang dùng.
3. Thử DNS khác (ví dụ Google DNS 8.8.8.8) nếu mạng công ty chặn.

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
