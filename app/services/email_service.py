"""Gửi email xác thực. Dùng smtplib (stdlib)."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import get_config


def send_verification_email(to_email: str, full_name: str, verify_token: str) -> bool:
    """
    Gửi email chứa link xác thực (token có expiry 15 phút).
    Link: {frontend_url}/verify-email?token={verify_token}
    Trả về True nếu gửi thành công, False nếu không cấu hình mail (dev: log link ra console).
    """
    config = get_config()
    link = f"{config.frontend_url.rstrip('/')}/verify-email?token={verify_token}"

    subject = "Xác thực email - TTN OJ"
    body = f"""Xin chào {full_name},

Bạn đã đăng ký tài khoản tại TTN OJ.
Vui lòng xác thực email bằng link sau (hết hạn 15 phút):

{link}

Nếu bạn không đăng ký, hãy bỏ qua email này.

TechTonic Online Judge
"""
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = config.mail_default_sender
    msg["To"] = to_email
    msg.attach(MIMEText(body, "plain", "utf-8"))

    if not config.mail_username or not config.mail_password:
        # Dev: không cấu hình SMTP thì chỉ in link ra console
        print(f"[DEV] Verification link for {to_email}: {link}")
        return True

    try:
        with smtplib.SMTP(config.mail_server, config.mail_port) as server:
            if config.mail_use_tls:
                server.starttls()
            server.login(config.mail_username, config.mail_password)
            server.send_message(msg)
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"[Email] Gửi thất bại (xác thực SMTP lỗi): {e}")
        print(
            "[Email] Gmail: dùng App Password thay vì mật khẩu đăng nhập: https://support.google.com/accounts/answer/185833"
        )
        return False
    except Exception as e:
        print(f"[Email] Failed to send verification to {to_email}: {e}")
        return False
