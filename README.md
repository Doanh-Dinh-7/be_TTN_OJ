# TTN OJ Backend

Flask REST API. Clean Architecture: Controller → Service → Repository → Models.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env     # edit .env with secrets
```

## Database

PostgreSQL. Migrations:

```bash
flask db init
flask db migrate -m "Initial"
flask db upgrade
```

Create roles (admin, user) and optionally an admin user via DB or script.

## Run

- API: `python run.py` (or `flask run`)
- Celery worker (judge): `celery -A app.celery_app:celery_app worker -l info`

Requires Redis and PostgreSQL (see docker-compose in project root).
