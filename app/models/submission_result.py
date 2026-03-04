"""SubmissionResult: per-test-case result. Used for score calculation."""

from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import relationship

from app import db
from app.models.base import BaseModel
from app.models.submission import SubmissionStatus


class SubmissionResult(BaseModel):
    __tablename__ = "submission_results"

    submission_id = Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("submissions.id", ondelete="CASCADE"),
        nullable=False,
    )
    test_case_id = Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("test_cases.id", ondelete="CASCADE"),
        nullable=False,
    )
    order_index = Column(Integer, nullable=False)
    status = Column(db.Enum(SubmissionStatus), nullable=False)
    score = Column(Integer, default=0, nullable=False)
    output = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    time_ms = Column(Integer, nullable=True)
    memory_mb = Column(db.Float, nullable=True)

    submission = relationship("Submission", back_populates="results")
