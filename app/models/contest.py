"""Contest model. Configuration cannot change after start."""

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Contest(BaseModel):
    __tablename__ = "contests"

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    is_public = Column(Boolean, default=True, nullable=False)
    leaderboard_hidden = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    problems = relationship("ContestProblem", back_populates="contest")
