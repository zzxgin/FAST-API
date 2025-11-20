"""Admin-level CRUD operations: user/task management, risk control, statistics"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.models.user import User, UserRole
from app.models.task import Task, TaskStatus
from app.models.assignment import TaskAssignment, AssignmentStatus
from app.models.reward import Reward, RewardStatus
from app.schemas.admin import SiteStatistics


def list_users(db: Session, skip: int = 0, limit: int = 20) -> List[User]:
    """List users with pagination.
    
    Args:
        db: Database session.
        skip: Records to skip.
        limit: Records to return.
    
    Returns:
        List of User objects.
    """
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
    # 关键修改：用 SQLAlchemy 原生 case 函数（生成 MySQL 兼容的 CASE WHEN 语法）
    # 1. 单查询获取用户和任务统计（修复 case 表达式）
    stats_query = db.query(
        func.count(func.distinct(User.id)).label('total_users'),
        func.count(func.distinct(Task.id)).label('total_tasks'),
        # 修复点1：用 case() 替代 func.case()，参数为 [(条件, 值)]，else_=0 显式指定默认值
        func.sum(
            case(
                [(Task.status == TaskStatus.open.value, 1)],  # 枚举类加 .value 获取字符串（避免隐式转换错误）
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
    
    # 2. 任务分配统计（同样修复 case 表达式）
    assignment_stats = db.query(
        func.count(TaskAssignment.id).label('total_assignments'),
        func.sum(
            case(
                [(TaskAssignment.status == AssignmentStatus.pending_review.value, 1)],
                else_=0
            )
        ).label('pending_reviews')
    ).first()
    
    # 3. 奖励统计（coalesce 用法正确，保留不变）
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
