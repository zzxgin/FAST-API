"""
Review SQLAlchemy model definition.
"""
from sqlalchemy import Column, Integer, Text, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models import Base
import enum
from datetime import datetime
from app.models.user import User
from app.models.task import Task

class ReviewResult(enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    appealing = "appealing"

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("task_assignments.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    review_result = Column(Enum(ReviewResult), default=ReviewResult.pending)
    review_comment = Column(Text)
    review_time = Column(DateTime, default=datetime.utcnow)
    reviewer = relationship("User")
