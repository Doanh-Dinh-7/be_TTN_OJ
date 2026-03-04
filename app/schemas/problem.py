"""Problem and test case schemas."""

from uuid import UUID

from pydantic import BaseModel


class TestCaseCreate(BaseModel):
    input_data: str | None = None
    expected_output: str
    is_sample: bool = False
    order_index: int = 0


class ProblemCreate(BaseModel):
    title: str
    description: str
    max_score: int
    time_limit_ms: int
    memory_limit_mb: int
    language_allowed: str = "python"
    test_cases: list[TestCaseCreate]


class ProblemResponse(BaseModel):
    id: UUID
    title: str
    description: str
    max_score: int
    time_limit_ms: int
    memory_limit_mb: int
    language_allowed: str

    class Config:
        from_attributes = True
