from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


class LoginRequest(BaseModel):
    """Login request model"""
    username: str = Field(..., min_length=3, max_length=80)
    password: str = Field(..., min_length=8)


class SignupRequest(BaseModel):
    """Signup request model"""
    username: str = Field(..., min_length=3, max_length=80)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, max_length=120)

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not v.isalnum() and '_' not in v:
            raise ValueError('Username must be alphanumeric or contain underscores')
        return v


class AuthResponse(BaseModel):
    """Authentication response model"""
    success: bool
    message: str
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None
