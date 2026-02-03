"""
Reward Pydantic schemas for API validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.reward import RewardStatus
from app.models.task import TaskStatus

class RewardBase(BaseModel):
    assignment_id: int
    amount: float = Field(..., ge=0)

class RewardCreate(RewardBase):
    pass

class RewardUpdate(BaseModel):
    status: Optional[RewardStatus] = None
    issued_time: Optional[datetime] = None

class RewardRead(RewardBase):
    id: int
    status: RewardStatus
    issued_time: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    user_name: Optional[str] = None
    task_title: Optional[str] = None
    task_status: Optional[TaskStatus] = None

    class Config:
        orm_mode = True

class RewardStats(BaseModel):
    pending_amount: float
    issued_amount: float
    failed_amount: float
    total_amount: float
