"""
Notification Pydantic schemas for API validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class NotificationBase(BaseModel):
    user_id: int
    content: str

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None

class NotificationRead(NotificationBase):
    id: int
    is_read: bool
    created_at: Optional[datetime]

    class Config:
        orm_mode = True
