"""TestCase model. Problem must have test cases before contest assign."""

from sqlalchemy import Boolean, Column, Text
from sqlalchemy.orm import relationship

from app import db
from app.models.base import BaseModel


class TestCase(BaseModel):
    __tablename__ = "test_cases"

    problem_id = Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("problems.id", ondelete="CASCADE"),
        nullable=False,
    )
    input_data = Column(Text, nullable=True)
    expected_output = Column(Text, nullable=False)
    input_path = Column(Text, nullable=True)
    output_path = Column(Text, nullable=True)
    is_sample = Column(Boolean, default=False, nullable=False)
    order_index = Column(db.Integer, default=0, nullable=False)

    problem = relationship("Problem", back_populates="test_cases")
