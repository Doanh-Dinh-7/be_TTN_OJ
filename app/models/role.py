"""Role model for RBAC."""

from sqlalchemy import Column, String

from app.models.base import BaseModel


class Role(BaseModel):
    __tablename__ = "roles"

    name = Column(String(64), unique=True, nullable=False)
