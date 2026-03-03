"""User model. Password hashed with bcrypt."""
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app import db


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(128), nullable=False, index=True)
    verified = Column(Boolean, default=False, nullable=False)
    banned = Column(Boolean, default=False, nullable=False)
    role_id = Column(
        "role_id",
        db.UUID(as_uuid=True),
        db.ForeignKey("roles.id"),
        nullable=False,
    )
    role = relationship("Role", backref="users")
