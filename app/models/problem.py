"""Problem model. Must have test cases and max_score before contest assign."""

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Problem(BaseModel):
    __tablename__ = "problems"

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    max_score = Column(Integer, nullable=False)
    time_limit_ms = Column(Integer, nullable=False)
    memory_limit_mb = Column(Integer, nullable=False)
    language_allowed = Column(String(64), default="python", nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    test_cases = relationship("TestCase", back_populates="problem")
    contest_problems = relationship("ContestProblem", back_populates="problem")
