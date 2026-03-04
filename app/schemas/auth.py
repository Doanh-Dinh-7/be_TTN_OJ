"""Auth request/response schemas."""
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str = Field(..., min_length=8, description="Ít nhất 8 ký tự")


class VerifyEmailRequest(BaseModel):
    token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    verified: bool
    role_id: UUID

    class Config:
        from_attributes = True
