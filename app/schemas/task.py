"""
Task Pydantic schemas for API validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.task import TaskStatus
from app.schemas.user import UserRead

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    reward_amount: float = Field(gt=0, description="Reward amount must be positive")

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    reward_amount: Optional[float] = Field(None, gt=0, description="Reward amount must be positive")
    status: Optional[TaskStatus] = None

class TaskRead(TaskBase):
    id: int
    publisher_id: int
    status: TaskStatus
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    publisher: Optional[UserRead] = None

    class Config:
        orm_mode = True

