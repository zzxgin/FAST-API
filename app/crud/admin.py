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
    """List users with pagination limits.
    
    Args:
        db: Database session
        skip: Records to skip (max: 10000)
        limit: Records to return (max: 1000)
    
    Returns:
        List of User objects
    """
    # Apply upper limits
    skip = min(skip, 10000)
    limit = min(limit, 1000)
    return db.query(User).offset(skip).limit(limit).all()


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, user_id: int, role: Optional[UserRole] = None) -> Optional[User]:
    user = get_user(db, user_id)
    if not user:
        return None
    if role is not None:
        user.role = role
    db.commit()
    db.refresh(user)
    return user


def list_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[Task]:
    """List tasks with pagination limits.
    
    Args:
        db: Database session
        skip: Records to skip (max: 10000)
        limit: Records to return (max: 1000)
    
    Returns:
        List of Task objects
    """
    # Apply upper limits
    skip = min(skip, 10000)
    limit = min(limit, 1000)
    return db.query(Task).offset(skip).limit(limit).all()


def get_task(db: Session, task_id: int) -> Optional[Task]:
    return db.query(Task).filter(Task.id == task_id).first()


def update_task_status(db: Session, task_id: int, status: TaskStatus) -> Optional[Task]:
    task = get_task(db, task_id)
    if not task:
        return None
    task.status = status
    db.commit()
    db.refresh(task)
    return task


def flag_task(db: Session, task_id: int, flagged: bool = True) -> Optional[Task]:
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
    """Get site-wide statistics with optimized aggregation queries.
    
    Uses single queries with conditional aggregation to reduce database round trips.
    """
    # Single query for all user and task counts
    stats_query = db.query(
        func.count(func.distinct(User.id)).label('total_users'),
        func.count(func.distinct(Task.id)).label('total_tasks'),
        func.sum(func.case((Task.status == TaskStatus.open, 1), else_=0)).label('open_tasks'),
        func.sum(func.case((Task.status == TaskStatus.in_progress, 1), else_=0)).label('in_progress_tasks')
    ).select_from(User).outerjoin(Task, Task.publisher_id == User.id).first()
    
    # Single query for assignment statistics
    assignment_stats = db.query(
        func.count(TaskAssignment.id).label('total_assignments'),
        func.sum(func.case((TaskAssignment.status == AssignmentStatus.pending_review, 1), else_=0)).label('pending_reviews')
    ).first()
    
    # Single query for reward statistics
    total_rewards_issued = db.query(
        func.coalesce(func.sum(Reward.amount), 0.0)
    ).filter(Reward.status == RewardStatus.issued).scalar() or 0.0

    return SiteStatistics(
        total_users=int(stats_query.total_users or 0),
        total_tasks=int(stats_query.total_tasks or 0),
        open_tasks=int(stats_query.open_tasks or 0),
        in_progress_tasks=int(stats_query.in_progress_tasks or 0),
        total_assignments=int(assignment_stats.total_assignments or 0),
        pending_reviews=int(assignment_stats.pending_reviews or 0),
        total_rewards_issued=float(total_rewards_issued)
    )
