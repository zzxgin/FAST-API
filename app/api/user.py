"""User API routes for registration, login, and user info.

This module provides endpoints for user registration, authentication,
and user information retrieval. All endpoints follow FastAPI standards.

Note:
All endpoints returning ORM objects must use `UserRead.from_orm(obj)` to ensure compatibility with Pydantic 1.x response_model validation.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserRead, UserLogin
from app.crud.user import create_user, authenticate_user, get_user_by_username
from app.core.security import create_access_token, get_current_user, require_role
from app.core.database import get_db

router = APIRouter(prefix="/api/user", tags=["user"])

@router.post("/register", response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user.

    Args:
        user: UserCreate schema with registration info.
        db: Database session dependency.

    Returns:
        UserRead schema of the created user.

    Raises:
        HTTPException: If username already exists.
    """
    db_user = get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    created = create_user(db, user)
    return UserRead.from_orm(created)

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token.

    Args:
        user: UserLogin schema with login credentials.
        db: Database session dependency.

    Returns:
        dict: JWT access token and token type.

    Raises:
        HTTPException: If credentials are invalid.
    """
    db_user = authenticate_user(db, user.username, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserRead)
def read_me(current_user = Depends(get_current_user)):
    """Get current authenticated user's info.

    Args:
        current_user: User object from JWT token.

    Returns:
        UserRead schema of the current user.
    """
    return UserRead.from_orm(current_user)

@router.get("/info/{username}", response_model=UserRead)
def get_user_info(username: str, db: Session = Depends(get_db)):
    """Get user info by username.

    Args:
        username: Username to query.
        db: Database session dependency.

    Returns:
        UserRead schema of the user.

    Raises:
        HTTPException: If user not found.
    """
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.from_orm(user)
