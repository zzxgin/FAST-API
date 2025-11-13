"""User center Pydantic schemas for API validation.

Defines schemas for user profile, task records, and statistics.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.models.user import UserRole
from app.models.task import TaskStatus
from app.models.assignment import AssignmentStatus


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile."""
    email: Optional[str] = None
    # TODO: Add more profile fields as needed (avatar, bio, etc.)


class UserProfileResponse(BaseModel):
    """Schema for user profile response."""
    id: int
    username: str
    email: Optional[str]
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
    status: str  # pending, issued, failed
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
    success_rate: float  # 完成任务成功率
    average_rating: Optional[float]  # TODO: 等评分系统实现后添加


class UserTaskStats(BaseModel):
    """Schema for detailed task statistics."""
    # 接取任务统计
    taken_tasks: int
    completed_tasks: int
    pending_tasks: int
    rejected_tasks: int

    # 发布任务统计
    published_tasks: int
    published_completed: int
    published_in_progress: int

    # 奖励统计
    total_earned: float
    total_pending: float
    monthly_earned: float
    monthly_completed: int