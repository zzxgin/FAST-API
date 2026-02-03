"""Admin-level CRUD operations: user/task management, risk control, statistics"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.crud.user import pwd_context
from app.models.user import User, UserRole
from app.models.task import Task, TaskStatus
from app.models.assignment import TaskAssignment, AssignmentStatus
from app.models.reward import Reward, RewardStatus
from app.schemas.admin import SiteStatistics


def list_users(db: Session, skip: int = 0, limit: int = 20, username: Optional[str] = None) -> List[User]:
    """List users with pagination.
    
    Args:
        db: Database session.
        skip: Records to skip.
        limit: Records to return.
        username: Optional username filter (fuzzy search).
    
    Returns:
        List of User objects.
    """
    query = db.query(User)
    if username:
        query = query.filter(User.username.ilike(f"%{username}%"))
    return query.offset(skip).limit(limit).all()


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get a user by ID.
    
    Args:
        db: Database session.
        user_id: User ID to query.
    
    Returns:
        User object if found, None otherwise.
    """
    return db.query(User).filter(User.id == user_id).first()


def update_user(
    db: Session,
    user_id: int,
    username: Optional[str] = None,
    email: Optional[str] = None,
    role: Optional[UserRole] = None,
    password: Optional[str] = None
) -> Optional[User]:
    """Update a user's information.
    
    Args:
        db: Database session.
        user_id: User ID to update.
        username: New username (optional).
        email: New email (optional).
        role: New role to assign (optional).
        password: New password to set (optional).
    
    Returns:
        Updated User object if found, None otherwise.
    """
    try:
        user = db.query(User).filter(User.id == user_id).with_for_update().first()
        if not user:
            return None
        
        if username is not None:
            user.username = username
        if email is not None:
            user.email = email
        if role is not None:
            user.role = role
        if password is not None:
            user.password_hash = pwd_context.hash(password)
            
        db.commit()
        db.refresh(user)
        return user
    except Exception:
        db.rollback()
        raise


def list_tasks(db: Session, skip: int = 0, limit: int = 20) -> List[Task]:
    """List tasks with pagination.
    
    Args:
        db: Database session.
        skip: Records to skip.
        limit: Records to return.
    
    Returns:
        List of Task objects.
    """
    return db.query(Task).offset(skip).limit(limit).all()


def get_task(db: Session, task_id: int) -> Optional[Task]:
    """Get a task by ID.
    
    Args:
        db: Database session.
        task_id: Task ID to query.
    
    Returns:
        Task object if found, None otherwise.
    """
    return db.query(Task).filter(Task.id == task_id).first()


def update_task_status(db: Session, task_id: int, status: TaskStatus) -> Optional[Task]:
    """Update a task's status.
    
    Args:
        db: Database session.
        task_id: Task ID to update.
        status: New task status.
    
    Returns:
        Updated Task object if found, None otherwise.
    """
    try:
        task = db.query(Task).filter(Task.id == task_id).with_for_update().first()
        if not task:
            return None
        task.status = status
        db.commit()
        db.refresh(task)
        return task
    except Exception:
        db.rollback()
        raise


def flag_task(db: Session, task_id: int, flagged: bool = True) -> Optional[Task]:
    """Flag a task for risk control review.
    
    Closes the task when flagged for manual review.
    
    Args:
        db: Database session.
        task_id: Task ID to flag.
        flagged: Whether to flag the task (default: True).
    
    Returns:
        Updated Task object if found, None otherwise.
    """
    try:
        task = db.query(Task).filter(Task.id == task_id).with_for_update().first()
        if not task:
            return None
        if flagged:
            task.status = TaskStatus.closed
        db.commit()
        db.refresh(task)
        return task
    except Exception:
        db.rollback()
        raise


def get_site_statistics(db: Session) -> SiteStatistics:
    """Get site-wide statistics with optimized aggregation queries.
    
    Uses single queries with conditional aggregation to reduce database round trips.
    """
    stats_query = db.query(
        func.count(func.distinct(User.id)).label('total_users'),
        func.count(func.distinct(Task.id)).label('total_tasks'),
        func.sum(
            case(
                [(Task.status == TaskStatus.open.value, 1)],  
                else_=0
            )
        ).label('open_tasks'),
        func.sum(
            case(
                [(Task.status == TaskStatus.in_progress.value, 1)],
                else_=0
            )
        ).label('in_progress_tasks')
    ).select_from(User).outerjoin(Task, Task.publisher_id == User.id).first()
    
    assignment_stats = db.query(
        func.count(TaskAssignment.id).label('total_assignments'),
        func.sum(
            case(
                [(TaskAssignment.status == AssignmentStatus.task_pending.value, 1)],
                else_=0
            )
        ).label('pending_reviews')
    ).first()

    total_rewards_issued = db.query(
        func.coalesce(func.sum(Reward.amount), 0.0)
    ).filter(Reward.status == RewardStatus.issued.value).scalar() or 0.0

    return SiteStatistics(
        total_users=int(stats_query.total_users or 0),
        total_tasks=int(stats_query.total_tasks or 0),
        open_tasks=int(stats_query.open_tasks or 0),
        in_progress_tasks=int(stats_query.in_progress_tasks or 0),
        total_assignments=int(assignment_stats.total_assignments or 0),
        pending_reviews=int(assignment_stats.pending_reviews or 0),
        total_rewards_issued=float(total_rewards_issued)
    )
