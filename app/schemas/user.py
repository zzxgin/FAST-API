"""User Pydantic schemas for API validation.

Defines schemas for user creation, reading, updating, and login.
"""
from datetime import datetime
from app.models.user import UserRole
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    """Base user schema with common fields."""
    username: str
    email: Optional[EmailStr] = None
    role: UserRole = UserRole.user

class UserCreate(UserBase):
    """Schema for user registration."""
    password: str

class UserRead(UserBase):
    id: int
    role: UserRole
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str
