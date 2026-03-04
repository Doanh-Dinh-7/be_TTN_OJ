"""Contest schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ContestCreate(BaseModel):
    name: str
    description: str | None = None
    start_time: datetime
    end_time: datetime
    is_public: bool = True
    leaderboard_hidden: bool = False


class ContestResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    start_time: datetime
    end_time: datetime
    is_public: bool
    leaderboard_hidden: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ContestListResponse(BaseModel):
    id: UUID
    name: str
    start_time: datetime
    end_time: datetime
    is_public: bool

    class Config:
        from_attributes = True
