"""Pydantic schemas for admin APIs: user/task management, risk control, statistics"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.models.user import UserRole
from app.models.task import TaskStatus


class AdminUserItem(BaseModel):
    id: int
    username: str
    email: Optional[str]
    role: UserRole
    is_active: bool
    created_at: Optional[datetime]

    class Config:
        orm_mode = True


class AdminUserUpdate(BaseModel):
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class AdminTaskItem(BaseModel):
    id: int
    title: str
    description: Optional[str]
    publisher_id: int
    status: TaskStatus
    reward_amount: float
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class AdminTaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None


class SiteStatistics(BaseModel):
    total_users: int
    active_users: int
    total_tasks: int
    open_tasks: int
    in_progress_tasks: int
    total_assignments: int
    pending_reviews: int
    total_rewards_issued: float
