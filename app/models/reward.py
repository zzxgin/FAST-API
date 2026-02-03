"""
Reward SQLAlchemy model definition.
"""
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.models import Base
from datetime import datetime, timezone
import enum

class RewardStatus(enum.Enum):
    pending = "pending"
    issued = "issued"
    failed = "failed"

class Reward(Base):
    __tablename__ = "rewards"
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("task_assignments.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(Enum(RewardStatus), default=RewardStatus.pending)
    issued_time = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    assignment = relationship("TaskAssignment")

    @property
    def user_name(self):
        return self.assignment.user.username if self.assignment and self.assignment.user else None

    @property
    def task_title(self):
        return self.assignment.task.title if self.assignment and self.assignment.task else None

    @property
    def task_status(self):
        return self.assignment.task.status if self.assignment and self.assignment.task else None
