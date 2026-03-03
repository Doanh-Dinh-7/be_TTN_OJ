"""ContestProblem: problem assigned to contest (order, max_score)."""
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app import db


class ContestProblem(BaseModel):
    __tablename__ = "contest_problems"

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
    order_index = Column(Integer, default=0, nullable=False)
    max_score = Column(Integer, nullable=False)

    contest = relationship("Contest", back_populates="problems")
    problem = relationship("Problem", back_populates="contest_problems")
