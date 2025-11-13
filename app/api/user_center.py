"""User center API endpoints.

Provides endpoints for user profile management, task records, and statistics.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user_center import (
    UserProfileUpdate,
    UserProfileResponse,
    UserTaskRecord,
    UserPublishedTask,
    UserRewardRecord,
    UserStatistics,
    UserTaskStats
)
from app.crud import user_center as crud_user_center

router = APIRouter()


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile.

    Returns:
        User profile information
    """
    user = crud_user_center.get_user_profile(db, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile.

    Args:
        profile_update: Profile update data

    Returns:
        Updated user profile
    """
    user = crud_user_center.update_user_profile(db, current_user.id, profile_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/tasks", response_model=List[UserTaskRecord])
async def get_user_tasks(
    status: Optional[str] = Query(None, description="Filter by assignment status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's task records.

    Args:
        status: Optional assignment status filter
        skip: Pagination offset
        limit: Pagination limit

    Returns:
        List of user's task records
    """
    return crud_user_center.get_user_task_records(
        db, current_user.id, status=status, skip=skip, limit=limit
    )


@router.get("/published-tasks", response_model=List[UserPublishedTask])
async def get_user_published_tasks(
    status: Optional[str] = Query(None, description="Filter by task status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's published tasks.

    Args:
        status: Optional task status filter
        skip: Pagination offset
        limit: Pagination limit

    Returns:
        List of user's published tasks
    """
    return crud_user_center.get_user_published_tasks(
        db, current_user.id, status=status, skip=skip, limit=limit
    )


@router.get("/rewards", response_model=List[UserRewardRecord])
async def get_user_rewards(
    status: Optional[str] = Query(None, description="Filter by reward status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's reward records.

    Args:
        status: Optional reward status filter
        skip: Pagination offset
        limit: Pagination limit

    Returns:
        List of user's reward records
    """
    return crud_user_center.get_user_rewards(
        db, current_user.id, status=status, skip=skip, limit=limit
    )


@router.get("/statistics", response_model=UserStatistics)
async def get_user_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user statistics.

    Returns:
        User statistics overview
    """
    return crud_user_center.get_user_statistics(db, current_user.id)


@router.get("/task-stats", response_model=UserTaskStats)
async def get_user_task_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed user task statistics.

    Returns:
        Detailed task statistics
    """
    return crud_user_center.get_user_task_stats(db, current_user.id)