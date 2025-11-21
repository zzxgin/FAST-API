"""
TaskAssignment SQLAlchemy model definition.
"""
from sqlalchemy import Column, Integer, Text, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models import Base
import enum
from datetime import datetime, timezone
from app.models.user import User
from app.models.task import Task

class AssignmentStatus(enum.Enum):
    task_pending = "task_pending"
    user_approved = "user_approved"
    user_rejected = "user_rejected"
    appealing = "appealing"
    task_completed = "task_completed"
    task_reject="task_reject"
    task_progress = "task_progress"

class TaskAssignment(Base):
    __tablename__ = "task_assignments"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    submit_content = Column(Text)
    submit_time = Column(DateTime)
    status = Column(Enum(AssignmentStatus), default=AssignmentStatus.pending_review)
    review_time = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user = relationship("User")
    task = relationship("Task")
