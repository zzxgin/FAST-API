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
# from app.models.assignment import TaskAssignment # Avoid circular import if any, but here it seems safe or use string

class ReviewResult(enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    appealing = "appealing"
class ReviewType(enum.Enum):
    """审核类型枚举"""
    acceptance_review = "acceptance_review"  
    submission_review = "submission_review"  
    appeal_review = "appeal_review"  
class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("task_assignments.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    review_result = Column(Enum(ReviewResult), default=ReviewResult.pending)
    review_type = Column(Enum(ReviewType), nullable=False)
    review_comment = Column(Text)
    review_time = Column(DateTime, default=datetime.utcnow)
    reviewer = relationship("User")
    assignment = relationship("TaskAssignment")

    @property
    def task_title(self):
        return self.assignment.task.title if self.assignment and self.assignment.task else None

    @property
    def submitter_username(self):
        return self.assignment.user.username if self.assignment and self.assignment.user else None
