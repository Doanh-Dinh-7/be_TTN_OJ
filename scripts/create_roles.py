"""Create default roles (admin, user). Run once after db upgrade."""
import sys
sys.path.insert(0, ".")
from app import create_app, db
from app.models import Role

app = create_app()
with app.app_context():
    for name in ("admin", "user"):
        if not db.session.query(Role).filter(Role.name == name).first():
            db.session.add(Role(name=name))
    db.session.commit()
    print("Roles created.")
