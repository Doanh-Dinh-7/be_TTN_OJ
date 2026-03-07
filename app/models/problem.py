"""Problem model. Must have test cases and max_score before contest assign."""

import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ProblemStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"


class Problem(BaseModel):
    __tablename__ = "problems"

    title = Column(String(255), nullable=False, unique=True)
    slug = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    input_format = Column(Text, nullable=True)
    output_format = Column(Text, nullable=True)
    constraints = Column(Text, nullable=True)
    time_limit_ms = Column(Integer, nullable=False)  # time_limit (ms)
    memory_limit_mb = Column(Integer, nullable=False)  # memory_limit (MB)
    max_score = Column(Integer, nullable=False)
    created_by = Column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    status = Column(
        Enum(ProblemStatus),
        nullable=False,
        default=ProblemStatus.DRAFT,
    )
    language_allowed = Column(String(64), default="python", nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    test_cases = relationship("TestCase", back_populates="problem")
    contest_problems = relationship("ContestProblem", back_populates="problem")
