"""
TaskAssignment Pydantic schemas for API validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.assignment import AssignmentStatus

class AssignmentBase(BaseModel):
    task_id: int
    submit_content: Optional[str] = None

class AssignmentCreate(AssignmentBase):
    pass

class AssignmentUpdate(BaseModel):
    submit_content: Optional[str] = None
    status: Optional[AssignmentStatus] = None
    review_time: Optional[datetime] = None

class AssignmentRead(AssignmentBase):
    id: int
    user_id: int
    status: AssignmentStatus
    submit_time: Optional[datetime]
    review_time: Optional[datetime]

    class Config:
        orm_mode = True
