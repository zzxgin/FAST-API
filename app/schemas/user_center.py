"""User center Pydantic schemas for API validation.

Defines schemas for user profile, task records, and statistics.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel,EmailStr
from app.models.user import UserRole
from app.models.task import TaskStatus
from app.models.assignment import AssignmentStatus
from app.models.reward import RewardStatus


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile."""
    email: Optional[EmailStr] = None
    # TODO: Add more profile fields as needed (avatar, bio, etc.)


class UserProfileResponse(BaseModel):
    """Schema for user profile response."""
    id: int
    username: str
    email: Optional[EmailStr]=None
    role: UserRole
    created_at: datetime
    updated_at: datetime
    # TODO: Add reputation, level, avatar, etc. when implemented

    class Config:
        orm_mode = True


class UserTaskRecord(BaseModel):
    """Schema for user's task record."""
    task_id: int
    task_title: str
    task_status: TaskStatus
    assignment_id: Optional[int]
    assignment_status: Optional[AssignmentStatus]
    reward_amount: float
    submit_time: Optional[datetime]
    review_time: Optional[datetime]
    created_at: datetime

    class Config:
        orm_mode = True


class UserPublishedTask(BaseModel):
    """Schema for user's published tasks."""
    task_id: int
    title: str
    status: TaskStatus
    reward_amount: float
    total_assignments: int
    pending_reviews: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserRewardRecord(BaseModel):
    """Schema for user's reward record."""
    reward_id: int
    assignment_id: int
    task_title: str
    amount: float
    status: RewardStatus  # pending, issued, failed
    issued_time: Optional[datetime]
    created_at: datetime

    class Config:
        orm_mode = True


class UserStatistics(BaseModel):
    """Schema for user statistics."""
    total_tasks_taken: int
    total_tasks_completed: int
    total_tasks_published: int
    total_rewards_earned: float
    total_rewards_pending: float
    success_rate: float  # Task completion success rate
    average_rating: Optional[float]  # TODO: Add after rating system is implemented


class UserTaskStats(BaseModel):
    """Schema for detailed task statistics."""
    # Task assignment statistics
    taken_tasks: int
    completed_tasks: int
    pending_tasks: int
    rejected_tasks: int

    # Published task statistics
    published_tasks: int
    published_completed: int
    published_in_progress: int

    # Reward statistics
    total_earned: float
    total_pending: float
    monthly_earned: float
    monthly_completed: int