"""Admin-level CRUD operations: user/task management, risk control, statistics"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.user import User, UserRole
from app.models.task import Task, TaskStatus
from app.models.assignment import TaskAssignment, AssignmentStatus
from app.models.reward import Reward, RewardStatus
from app.schemas.admin import SiteStatistics


def list_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    print(f"Listing users with skip={skip} and limit={limit}")
    return db.query(User).offset(skip).limit(limit).all()


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, user_id: int, role: Optional[UserRole] = None, is_active: Optional[bool] = None):
    user = get_user(db, user_id)
    if not user:
        return None
    if role is not None:
        user.role = role
    if is_active is not None:
        user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user


def list_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Task).offset(skip).limit(limit).all()


def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()


def update_task_status(db: Session, task_id: int, status: TaskStatus):
    task = get_task(db, task_id)
    if not task:
        return None
    task.status = status
    db.commit()
    db.refresh(task)
    return task


def flag_task(db: Session, task_id: int, flagged: bool = True):
    # Simple placeholder: set status to closed when flagged
    task = get_task(db, task_id)
    if not task:
        return None
    if flagged:
        task.status = TaskStatus.closed
    db.commit()
    db.refresh(task)
    return task


def get_site_statistics(db: Session) -> SiteStatistics:
    total_users = db.query(func.count(User.id)).scalar() or 0
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
    total_tasks = db.query(func.count(Task.id)).scalar() or 0
    open_tasks = db.query(func.count(Task.id)).filter(Task.status == TaskStatus.open).scalar() or 0
    in_progress_tasks = db.query(func.count(Task.id)).filter(Task.status == TaskStatus.in_progress).scalar() or 0
    total_assignments = db.query(func.count(TaskAssignment.id)).scalar() or 0
    pending_reviews = db.query(func.count(TaskAssignment.id)).filter(TaskAssignment.status == AssignmentStatus.pending_review).scalar() or 0
    total_rewards_issued = db.query(func.coalesce(func.sum(Reward.amount), 0.0)).filter(Reward.status == RewardStatus.issued).scalar() or 0.0

    return SiteStatistics(
        total_users=int(total_users),
        active_users=int(active_users),
        total_tasks=int(total_tasks),
        open_tasks=int(open_tasks),
        in_progress_tasks=int(in_progress_tasks),
        total_assignments=int(total_assignments),
        pending_reviews=int(pending_reviews),
        total_rewards_issued=float(total_rewards_issued)
    )
