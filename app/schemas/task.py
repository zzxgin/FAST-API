"""
Task Pydantic schemas for API validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.task import TaskStatus

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    reward_amount: float

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    reward_amount: Optional[float] = None
    status: Optional[TaskStatus] = None

class TaskRead(TaskBase):
    id: int
    publisher_id: int
    status: TaskStatus
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
