"""Problem and test case schemas."""

from uuid import UUID

from pydantic import BaseModel, field_serializer, field_validator


class TestCaseCreate(BaseModel):
    input_data: str | None = None
    expected_output: str
    is_sample: bool = False
    order_index: int = 0


class ProblemCreate(BaseModel):
    """Input cho POST /api/admin/problems. time_limit (ms), memory_limit (MB)."""

    title: str
    description: str
    input_format: str = ""
    output_format: str = ""
    constraints: str = ""
    time_limit: int  # ms
    memory_limit: int  # MB
    max_score: int

    @field_validator("time_limit", "memory_limit")
    @classmethod
    def positive_limit(cls, v: int) -> int:
        if v is not None and v <= 0:
            raise ValueError("phải lớn hơn 0")
        return v


class ProblemUpdate(BaseModel):
    """Input cho PUT /api/admin/problems/{id}. Chỉ các trường được phép sửa."""

    description: str | None = None
    input_format: str | None = None
    output_format: str | None = None
    constraints: str | None = None
    time_limit: int | None = None  # ms
    memory_limit: int | None = None  # MB
    max_score: int | None = None

    @field_validator("time_limit", "memory_limit", "max_score")
    @classmethod
    def positive_if_present(cls, v: int | None) -> int | None:
        if v is not None and v <= 0:
            raise ValueError("phải lớn hơn 0")
        return v


class ProblemResponse(BaseModel):
    id: UUID
    title: str
    slug: str
    description: str
    input_format: str | None
    output_format: str | None
    constraints: str | None
    time_limit_ms: int
    memory_limit_mb: int
    max_score: int
    status: str
    created_by: UUID | None
    language_allowed: str = "python"

    @field_serializer("status")
    def serialize_status(self, v):
        return v.value if hasattr(v, "value") else v

    class Config:
        from_attributes = True
