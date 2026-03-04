# Hướng dẫn deploy TTN OJ Backend (repo riêng)

Backend và Frontend là **hai repo Git riêng**. Repo này chỉ chứa backend; deploy lên **Render** (Web Service) và **Fly.io** (Judge Worker).

Stack:
- **Backend API:** Render Web Service
- **Judge Worker:** Fly.io (Celery + Docker-in-Docker)
- **DB:** Neon (đã có)
- **Queue:** Render Redis (Backend) + **Upstash** (dùng chung Backend + Judge, vì Render Redis internal không ra internet)

---

## 1. Render Redis (Queue)

1. [Render Dashboard](https://dashboard.render.com) → **New** → **Redis**
2. Tên: `ttn-oj-redis`, Region gần Neon, Plan **Free**
3. **Create Redis** → copy **Internal Redis URL** (chỉ dùng được từ các service trên Render)

**Lưu ý:** Judge chạy trên Fly.io nên **không** dùng được Render Internal Redis. Dùng **Upstash** (public URL) cho cả Backend và Judge:
- [Upstash Console](https://console.upstash.com) → Create Database → copy `REDIS_URL`
- Trên Render (Backend) và Fly (Judge) đều set cùng `REDIS_URL` = URL Upstash

---

## 2. Backend – Render Web Service

1. Render → **New** → **Web Service**
2. Kết nối **repo backend** (repo Git chứa code này), nhánh chính
3. **Root Directory:** để trống (repo root = app)
4. **Build Command:** `pip install -r requirements.txt`
5. **Start Command:** `gunicorn -w 2 -b 0.0.0.0:$PORT run:app`
6. **Environment** (thêm trong Dashboard):
   - `DATABASE_URL` — Neon connection string
   - `REDIS_URL` / `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` — Upstash Redis URL (cùng một URL)
   - `SECRET_KEY`, `JWT_SECRET_KEY` — random ≥ 32 ký tự (cùng giá trị dùng cho Fly Judge)
   - `CORS_ORIGINS` — URL Frontend Vercel, ví dụ: `https://ttn-oj.vercel.app` (nhiều origin cách nhau bằng dấu phẩy)
   - `FRONTEND_URL` — URL Vercel chính
7. **Create Web Service** → sau khi deploy, copy URL Backend (vd: `https://ttn-oj-backend.onrender.com`)

**Migrations (Neon):** Chạy một lần từ máy local:
```bash
set DATABASE_URL=<Neon connection string>
flask db upgrade
```

---

## 3. Judge Worker – Fly.io

1. Cài [flyctl](https://fly.io/docs/hands-on/install-flyctl/) → `fly auth login`
2. Trong **repo backend** (root repo):
   ```bash
   cp fly.toml.example fly.toml
   # Sửa app = "ttn-oj-judge" nếu cần
   fly launch
   ```
   - Chọn app name, region; **không** tạo Postgres/Redis trên Fly
3. **Secrets / Environment:**
   ```bash
   fly secrets set DATABASE_URL="<Neon URI>"
   fly secrets set REDIS_URL="<Upstash Redis URL>"
   fly secrets set CELERY_BROKER_URL="<cùng Upstash URL>"
   fly secrets set CELERY_RESULT_BACKEND="<cùng Upstash URL>"
   fly secrets set SECRET_KEY="<cùng với Render Backend>"
   fly secrets set JWT_SECRET_KEY="<cùng với Render Backend>"
   ```
4. Deploy:
   ```bash
   fly deploy
   ```

Judge dùng Docker-in-Docker (DinD); `fly.toml` nên set `memory = "1gb"` (free tier 256MB thường không đủ).

---

## 4. Repo Frontend (riêng) – Vercel

Repo frontend deploy trên Vercel. Trong project Vercel:
- **Root Directory:** để trống
- **Build:** `npm run build`
- **Environment:** `VITE_API_URL` = URL Backend Render (vd: `https://ttn-oj-backend.onrender.com`)

Sau khi có URL Vercel, quay lại Render Backend → Environment → cập nhật `CORS_ORIGINS` và `FRONTEND_URL`.

---

## Tóm tắt biến môi trường

| Nơi | Biến |
|-----|------|
| **Render (Backend)** | `DATABASE_URL`, `REDIS_URL`, `CELERY_*`, `SECRET_KEY`, `JWT_SECRET_KEY`, `CORS_ORIGINS`, `FRONTEND_URL` |
| **Fly (Judge)** | Cùng trên + dùng **cùng** `REDIS_URL` (Upstash) và cùng `SECRET_KEY`/`JWT_SECRET_KEY` với Backend |
| **Vercel (Frontend repo)** | `VITE_API_URL` = URL Backend Render |
