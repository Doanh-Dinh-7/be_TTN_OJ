"""Submission schemas."""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class SubmissionCreate(BaseModel):
    code: str
    language: str = "python"


class SubmissionResponse(BaseModel):
    id: UUID
    problem_id: UUID
    contest_id: UUID
    status: str
    score: int
    created_at: datetime

    class Config:
        from_attributes = True
