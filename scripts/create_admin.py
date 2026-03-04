"""Tạo tài khoản ADMIN (email: raymondpython07@gmail.com, password: 12341234). Chạy sau create_roles.py."""
import sys

sys.path.insert(0, ".")
from app import create_app, db
from app.models import Role, User
from app.utils.auth import hash_password
from app.repositories.user_repository import UserRepository

ADMIN_EMAIL = "raymondpython07@gmail.com"
ADMIN_USERNAME = "ADMIN"
ADMIN_PASSWORD = "12341234"

app = create_app()
with app.app_context():
    for name in ("admin", "user"):
        if not db.session.query(Role).filter(Role.name == name).first():
            db.session.add(Role(name=name))
    db.session.commit()

    if UserRepository.get_by_email(ADMIN_EMAIL):
        print("Admin user already exists.")
    else:
        password_hash = hash_password(ADMIN_PASSWORD)
        UserRepository.create(
            email=ADMIN_EMAIL,
            password_hash=password_hash,
            username=ADMIN_USERNAME,
            role_name="admin",
        )
        user = UserRepository.get_by_email(ADMIN_EMAIL)
        if user:
            user.verified = True
        db.session.commit()
        print("Admin user created.")
        print(f"  Email: {ADMIN_EMAIL}")
        print(f"  Username: {ADMIN_USERNAME}")
        print(f"  Password: {ADMIN_PASSWORD}")
