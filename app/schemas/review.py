"""
Review Pydantic schemas for API validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.review import ReviewResult, ReviewType

class ReviewBase(BaseModel):
    assignment_id: int
    review_result: ReviewResult
    review_type: ReviewType
    review_comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    review_result: Optional[ReviewResult] = None
    review_comment: Optional[str] = None

class ReviewRead(ReviewBase):
    id: int
    reviewer_id: int
    review_time: Optional[datetime]

    class Config:
        orm_mode = True
        use_enum_values = True  

