"""AuditLog for suspicious activity and admin actions."""

from sqlalchemy import Column, String, Text

from app import db
from app.models.base import BaseModel


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    user_id = Column(db.UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=True)
    action = Column(String(64), nullable=False)
    resource = Column(String(64), nullable=True)
    resource_id = Column(db.UUID(as_uuid=True), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(64), nullable=True)
