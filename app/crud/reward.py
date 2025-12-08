"""
CRUD operations for Reward model.
"""
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models.reward import Reward, RewardStatus
from app.models.assignment import TaskAssignment
from app.models.task import Task
from app.models.user import User
from app.schemas.reward import RewardCreate, RewardUpdate

def create_reward(db: Session, reward: RewardCreate):
    db_reward = Reward(
        assignment_id=reward.assignment_id,
        amount=reward.amount,
        status=RewardStatus.pending
    )
    db.add(db_reward)
    db.commit()
    db.refresh(db_reward)
    return db_reward

def get_reward(db: Session, reward_id: int):
    return db.query(Reward).options(joinedload(Reward.assignment).joinedload("user"), joinedload(Reward.assignment).joinedload("task")).filter(Reward.id == reward_id).first()

def get_rewards_by_user(db: Session, user_id: int):
    # Query rewards by joining assignment to get user_id
    from app.models.assignment import TaskAssignment
    return db.query(Reward).options(joinedload(Reward.assignment).joinedload("user"), joinedload(Reward.assignment).joinedload("task")).join(TaskAssignment, Reward.assignment_id == TaskAssignment.id).filter(TaskAssignment.user_id == user_id).all()

def update_reward(db: Session, reward_id: int, reward_update: RewardUpdate):
    db_reward = get_reward(db, reward_id)
    if not db_reward:
        return None
    for field, value in reward_update.dict(exclude_unset=True).items():
        setattr(db_reward, field, value)
    db.commit()
    db.refresh(db_reward)
    return db_reward


def list_rewards(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    user_name: Optional[str] = None,
    task_title: Optional[str] = None,
    task_status: Optional[str] = None,
    reward_status: Optional[RewardStatus] = None,
    publisher_id: Optional[int] = None,
    sort_by_time: Optional[str] = None,  # 'asc' or 'desc'
    sort_by_amount: Optional[str] = None,  # 'asc' or 'desc'
):
    query = db.query(Reward).options(
        joinedload(Reward.assignment).joinedload("user"),
        joinedload(Reward.assignment).joinedload("task")
    )

    if user_name or task_title or task_status or publisher_id:
        query = query.join(TaskAssignment, Reward.assignment_id == TaskAssignment.id)
        
        if user_name:
            query = query.join(User, TaskAssignment.user_id == User.id).filter(User.username.ilike(f"%{user_name}%"))
        
        if task_title or task_status or publisher_id:
            query = query.join(Task, TaskAssignment.task_id == Task.id)
            
            if task_title:
                query = query.filter(Task.title.ilike(f"%{task_title}%"))
            
            if task_status:
                query = query.filter(Task.status == task_status)
                
            if publisher_id:
                query = query.filter(Task.publisher_id == publisher_id)

    if reward_status:
        query = query.filter(Reward.status == reward_status)

    if sort_by_time:
        if sort_by_time.lower() == 'asc':
            query = query.order_by(Reward.created_at.asc())
        else:
            query = query.order_by(Reward.created_at.desc())
            
    if sort_by_amount:
        if sort_by_amount.lower() == 'asc':
            query = query.order_by(Reward.amount.asc())
        else:
            query = query.order_by(Reward.amount.desc())
            
    # Default sort if none specified
    if not sort_by_time and not sort_by_amount:
        query = query.order_by(Reward.id.desc())

    return query.offset(skip).limit(limit).all()

def get_reward_stats(db: Session):
    """Calculate reward statistics.

    Args:
        db: Database session.

    Returns:
        Dictionary containing stats.
    """
    stats = db.query(
        Reward.status, func.sum(Reward.amount)
    ).group_by(Reward.status).all()
    
    result = {
        "pending_amount": 0.0,
        "issued_amount": 0.0,
        "failed_amount": 0.0,
        "total_amount": 0.0
    }
    
    for status, amount in stats:
        if amount:
            if status == RewardStatus.pending:
                result["pending_amount"] = float(amount)
            elif status == RewardStatus.issued:
                result["issued_amount"] = float(amount)
            elif status == RewardStatus.failed:
                result["failed_amount"] = float(amount)
            
            result["total_amount"] += float(amount)
            
    return result



def get_reward_by_assignment_id(db: Session, assignment_id: int):
    return db.query(Reward).filter(Reward.assignment_id == assignment_id).first()
