"""CRUD operations for user center functionality.

Provides functions for user profile management, task records, and statistics.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from datetime import datetime, timedelta

from app.models.user import User
from app.models.task import Task, TaskStatus
from app.models.assignment import TaskAssignment, AssignmentStatus
from app.models.reward import Reward, RewardStatus
from app.schemas.user_center import (
    UserProfileUpdate,
    UserTaskRecord,
    UserPublishedTask,
    UserRewardRecord,
    UserStatistics,
    UserTaskStats
)


def get_user_profile(db: Session, user_id: int) -> Optional[User]:
    """Get user profile by user ID.

    Args:
        db: SQLAlchemy session
        user_id: User ID

    Returns:
        User instance or None
    """
    return db.query(User).filter(User.id == user_id).first()


def update_user_profile(db: Session, user_id: int, profile_update: UserProfileUpdate) -> Optional[User]:
    """Update user profile.

    Args:
        db: SQLAlchemy session
        user_id: User ID
        profile_update: Profile update data

    Returns:
        Updated User instance or None
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    update_data = profile_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


def get_user_task_records(db: Session, user_id: int, status: Optional[str] = None,
                         skip: int = 0, limit: int = 20) -> List[UserTaskRecord]:
    """Get user's task assignment records.

    Args:
        db: SQLAlchemy session
        user_id: User ID
        status: Optional assignment status filter
        skip: Pagination offset
        limit: Pagination limit

    Returns:
        List of task records
    """
    query = db.query(
        Task.id.label('task_id'),
        Task.title.label('task_title'),
        Task.status.label('task_status'),
        TaskAssignment.id.label('assignment_id'),
        TaskAssignment.status.label('assignment_status'),
        Task.reward_amount,
        TaskAssignment.submit_time,
        TaskAssignment.review_time,
        TaskAssignment.created_at
    ).join(TaskAssignment, Task.id == TaskAssignment.task_id)

    query = query.filter(TaskAssignment.user_id == user_id)

    if status:
        query = query.filter(TaskAssignment.status == status)

    query = query.order_by(TaskAssignment.created_at.desc())
    query = query.offset(skip).limit(limit)

    results = query.all()

    return [
        UserTaskRecord(
            task_id=row.task_id,
            task_title=row.task_title,
            task_status=row.task_status,
            assignment_id=row.assignment_id,
            assignment_status=row.assignment_status,
            reward_amount=row.reward_amount,
            submit_time=row.submit_time,
            review_time=row.review_time,
            created_at=row.created_at
        )
        for row in results
    ]


def get_user_published_tasks(db: Session, user_id: int, status: Optional[str] = None,
                           skip: int = 0, limit: int = 20) -> List[UserPublishedTask]:
    """Get user's published tasks.

    Args:
        db: SQLAlchemy session
        user_id: User ID (publisher)
        status: Optional task status filter
        skip: Pagination offset
        limit: Pagination limit

    Returns:
        List of published tasks
    """
    # 子查询：获取每个任务的总接取数和待审核数
    assignment_stats = db.query(
        TaskAssignment.task_id,
        func.count(TaskAssignment.id).label('total_assignments'),
        func.sum(
            func.case(
                (TaskAssignment.status == AssignmentStatus.pending_review, 1),
                else_=0
            )
        ).label('pending_reviews')
    ).group_by(TaskAssignment.task_id).subquery()

    query = db.query(
        Task.id.label('task_id'),
        Task.title,
        Task.status,
        Task.reward_amount,
        Task.created_at,
        Task.updated_at,
        func.coalesce(assignment_stats.c.total_assignments, 0).label('total_assignments'),
        func.coalesce(assignment_stats.c.pending_reviews, 0).label('pending_reviews')
    ).outerjoin(
        assignment_stats, Task.id == assignment_stats.c.task_id
    )

    query = query.filter(Task.publisher_id == user_id)

    if status:
        query = query.filter(Task.status == status)

    query = query.order_by(Task.created_at.desc())
    query = query.offset(skip).limit(limit)

    results = query.all()

    return [
        UserPublishedTask(
            task_id=row.task_id,
            title=row.title,
            status=row.status,
            reward_amount=row.reward_amount,
            total_assignments=row.total_assignments,
            pending_reviews=row.pending_reviews,
            created_at=row.created_at,
            updated_at=row.updated_at
        )
        for row in results
    ]


def get_user_rewards(db: Session, user_id: int, status: Optional[str] = None,
                    skip: int = 0, limit: int = 20) -> List[UserRewardRecord]:
    """Get user's reward records.

    Args:
        db: SQLAlchemy session
        user_id: User ID
        status: Optional reward status filter
        skip: Pagination offset
        limit: Pagination limit

    Returns:
        List of reward records
    """
    query = db.query(
        Reward.id.label('reward_id'),
        Reward.assignment_id,
        Task.title.label('task_title'),
        Reward.amount,
        Reward.status,
        Reward.issued_time,
        Reward.created_at
    ).join(TaskAssignment, Reward.assignment_id == TaskAssignment.id)\
     .join(Task, TaskAssignment.task_id == Task.id)

    query = query.filter(TaskAssignment.user_id == user_id)

    if status:
        query = query.filter(Reward.status == status)

    query = query.order_by(Reward.created_at.desc())
    query = query.offset(skip).limit(limit)

    results = query.all()

    return [
        UserRewardRecord(
            reward_id=row.reward_id,
            assignment_id=row.assignment_id,
            task_title=row.task_title,
            amount=row.amount,
            status=row.status,
            issued_time=row.issued_time,
            created_at=row.created_at
        )
        for row in results
    ]


def get_user_statistics(db: Session, user_id: int) -> UserStatistics:
    """Get user statistics.

    Args:
        db: SQLAlchemy session
        user_id: User ID

    Returns:
        User statistics
    """
    # 任务统计
    total_tasks_taken = db.query(TaskAssignment).filter(
        TaskAssignment.user_id == user_id
    ).count()

    total_tasks_completed = db.query(TaskAssignment).filter(
        and_(
            TaskAssignment.user_id == user_id,
            TaskAssignment.status == AssignmentStatus.approved
        )
    ).count()

    # 发布任务统计
    total_tasks_published = db.query(Task).filter(
        Task.publisher_id == user_id
    ).count()

    # 奖励统计
    total_rewards_earned = db.query(func.sum(Reward.amount)).join(
        TaskAssignment, Reward.assignment_id == TaskAssignment.id
    ).filter(
        and_(
            TaskAssignment.user_id == user_id,
            Reward.status == RewardStatus.issued
        )
    ).scalar() or 0.0

    total_rewards_pending = db.query(func.sum(Reward.amount)).join(
        TaskAssignment, Reward.assignment_id == TaskAssignment.id
    ).filter(
        and_(
            TaskAssignment.user_id == user_id,
            Reward.status == RewardStatus.pending
        )
    ).scalar() or 0.0

    # 成功率
    success_rate = 0.0
    if total_tasks_taken > 0:
        success_rate = (total_tasks_completed / total_tasks_taken) * 100

    return UserStatistics(
        total_tasks_taken=total_tasks_taken,
        total_tasks_completed=total_tasks_completed,
        total_tasks_published=total_tasks_published,
        total_rewards_earned=float(total_rewards_earned),
        total_rewards_pending=float(total_rewards_pending),
        success_rate=round(success_rate, 2),
        average_rating=None  # TODO: 等评分系统实现后添加
    )


def get_user_task_stats(db: Session, user_id: int) -> UserTaskStats:
    """Get detailed user task statistics.

    Args:
        db: SQLAlchemy session
        user_id: User ID

    Returns:
        Detailed task statistics
    """
    # 接取任务统计
    taken_tasks = db.query(TaskAssignment).filter(
        TaskAssignment.user_id == user_id
    ).count()

    completed_tasks = db.query(TaskAssignment).filter(
        and_(
            TaskAssignment.user_id == user_id,
            TaskAssignment.status == AssignmentStatus.approved
        )
    ).count()

    pending_tasks = db.query(TaskAssignment).filter(
        and_(
            TaskAssignment.user_id == user_id,
            TaskAssignment.status == AssignmentStatus.pending_review
        )
    ).count()

    rejected_tasks = db.query(TaskAssignment).filter(
        and_(
            TaskAssignment.user_id == user_id,
            TaskAssignment.status == AssignmentStatus.rejected
        )
    ).count()

    # 发布任务统计
    published_tasks = db.query(Task).filter(
        Task.publisher_id == user_id
    ).count()

    published_completed = db.query(Task).filter(
        and_(
            Task.publisher_id == user_id,
            Task.status == TaskStatus.completed
        )
    ).count()

    published_in_progress = db.query(Task).filter(
        and_(
            Task.publisher_id == user_id,
            Task.status == TaskStatus.in_progress
        )
    ).count()

    # 奖励统计
    total_earned = db.query(func.sum(Reward.amount)).join(
        TaskAssignment, Reward.assignment_id == TaskAssignment.id
    ).filter(
        and_(
            TaskAssignment.user_id == user_id,
            Reward.status == RewardStatus.issued
        )
    ).scalar() or 0.0

    total_pending = db.query(func.sum(Reward.amount)).join(
        TaskAssignment, Reward.assignment_id == TaskAssignment.id
    ).filter(
        and_(
            TaskAssignment.user_id == user_id,
            Reward.status == RewardStatus.pending
        )
    ).scalar() or 0.0

    # 本月统计
    current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    monthly_earned = db.query(func.sum(Reward.amount)).join(
        TaskAssignment, Reward.assignment_id == TaskAssignment.id
    ).filter(
        and_(
            TaskAssignment.user_id == user_id,
            Reward.status == RewardStatus.issued,
            Reward.issued_time >= current_month
        )
    ).scalar() or 0.0

    monthly_completed = db.query(TaskAssignment).filter(
        and_(
            TaskAssignment.user_id == user_id,
            TaskAssignment.status == AssignmentStatus.approved,
            TaskAssignment.review_time >= current_month
        )
    ).count()

    return UserTaskStats(
        taken_tasks=taken_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        rejected_tasks=rejected_tasks,
        published_tasks=published_tasks,
        published_completed=published_completed,
        published_in_progress=published_in_progress,
        total_earned=float(total_earned),
        total_pending=float(total_pending),
        monthly_earned=float(monthly_earned),
        monthly_completed=monthly_completed
    )