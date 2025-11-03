"""
CRUD operations for Reward model.
"""
from sqlalchemy.orm import Session
from app.models.reward import Reward, RewardStatus
from app.schemas.reward import RewardCreate, RewardUpdate
from datetime import datetime

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
    return db.query(Reward).filter(Reward.id == reward_id).first()

def get_rewards_by_user(db: Session, user_id: int):
    # Query rewards by joining assignment to get user_id
    from app.models.assignment import TaskAssignment
    return db.query(Reward).join(TaskAssignment, Reward.assignment_id == TaskAssignment.id).filter(TaskAssignment.user_id == user_id).all()

def update_reward(db: Session, reward_id: int, reward_update: RewardUpdate):
    db_reward = get_reward(db, reward_id)
    if not db_reward:
        return None
    for field, value in reward_update.dict(exclude_unset=True).items():
        setattr(db_reward, field, value)
    db.commit()
    db.refresh(db_reward)
    return db_reward
