"""Base model: UUID PK, UTC timestamps, soft delete support."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app import db


def utc_now() -> datetime:
    """All timestamps in UTC."""
    return datetime.now(timezone.utc)


class BaseModel(db.Model):
    """Abstract base: id (UUID), created_at, updated_at."""

    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
