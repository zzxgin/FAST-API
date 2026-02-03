"""
Task SQLAlchemy model definition.
"""
from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from app.models import Base
import enum
from datetime import datetime
from app.models.user import User

class TaskStatus(enum.Enum):
    open = "open"
    in_progress = "in_progress"
    pending_review = "pending_review"
    completed = "completed"
    closed = "closed"

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(128), nullable=False)
    description = Column(Text)
    publisher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.open)
    reward_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    publisher = relationship("User", backref="published_tasks")
