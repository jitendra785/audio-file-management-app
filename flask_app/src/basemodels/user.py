from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserResponse(BaseModel):
    """User response model"""
    id: int
    username: str
    email: str
    role: str
    full_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserCreateRequest(BaseModel):
    """User creation request model"""
    username: str = Field(..., min_length=3, max_length=80)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, max_length=120)
    role: str = Field(default="USER", pattern="^(ADMIN|USER)$")


class UserUpdateRequest(BaseModel):
    """User update request model"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=120)
    role: Optional[str] = Field(None, pattern="^(ADMIN|USER)$")
    password: Optional[str] = Field(None, min_length=8)
