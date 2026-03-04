"""Highest score per problem per user per contest for leaderboard optimization."""

from sqlalchemy import Column, Integer, UniqueConstraint

from app import db
from app.models.base import BaseModel


class UserContestScore(BaseModel):
    __tablename__ = "user_contest_scores"
    __table_args__ = (
        UniqueConstraint("user_id", "contest_id", "problem_id", name="uq_user_contest_problem"),
    )

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
    best_score = Column(Integer, default=0, nullable=False)
    best_submission_id = Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("submissions.id", ondelete="SET NULL"),
        nullable=True,
    )
