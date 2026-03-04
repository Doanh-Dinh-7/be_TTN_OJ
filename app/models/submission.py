"""Submission model. Never delete submission history."""

import enum

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app import db
from app.models.base import BaseModel


class SubmissionStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    RUNTIME_ERROR = "runtime_error"
    COMPILATION_ERROR = "compilation_error"


class Submission(BaseModel):
    __tablename__ = "submissions"

    user_id = Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    contest_id = Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("contests.id", ondelete="CASCADE"),
        nullable=False,
    )
    problem_id = Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("problems.id", ondelete="CASCADE"),
        nullable=False,
    )
    code = Column(Text, nullable=False)
    language = Column(String(32), nullable=False)
    status = Column(db.Enum(SubmissionStatus), default=SubmissionStatus.PENDING, nullable=False)
    score = Column(Integer, default=0, nullable=False)

    user = relationship("User", backref="submissions")
    contest = relationship("Contest", backref="submissions")
    problem = relationship("Problem", backref="submissions")
    results = relationship(
        "SubmissionResult", back_populates="submission", order_by="SubmissionResult.order_index"
    )
