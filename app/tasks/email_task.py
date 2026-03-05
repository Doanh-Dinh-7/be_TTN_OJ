"""
Task gửi email xác thực qua Celery. Chạy trong worker, không block request API.
Tránh timeout trên Render khi SMTP chậm.
"""

from app.celery_app import celery_app
from app.services.email_service import send_verification_email


@celery_app.task(bind=True)
def send_verification_email_task(self, to_email: str, full_name: str, verify_token: str):
    """Gửi email xác thực (chạy trong Celery worker)."""
    send_verification_email(to_email, full_name, verify_token)
