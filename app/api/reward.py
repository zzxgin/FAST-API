"""
Reward API routes for issuing and managing rewards.
All endpoints use OpenAPI English doc comments.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.reward import RewardCreate, RewardRead, RewardUpdate
from app.crud.reward import create_reward, get_reward, get_rewards_by_user, update_reward
from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/api/reward", tags=["reward"])

@router.post("/issue", response_model=RewardRead)
def issue_reward(reward: RewardCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Issue a reward to a user for an assignment.
    - Only admin can issue rewards.
    """
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admin can issue rewards")
    created = create_reward(db, reward)
    return RewardRead.from_orm(created)

@router.get("/{reward_id}", response_model=RewardRead)
def get_reward_detail(reward_id: int, db: Session = Depends(get_db)):
    """
    Get reward detail by ID.
    """
    reward = get_reward(db, reward_id)
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")
    return RewardRead.from_orm(reward)

@router.get("/user/{user_id}", response_model=list[RewardRead])
def list_rewards_by_user(user_id: int, db: Session = Depends(get_db)):
    """
    List all rewards for a user.
    """
    rewards = get_rewards_by_user(db, user_id)
    return [RewardRead.from_orm(r) for r in rewards]

@router.put("/{reward_id}", response_model=RewardRead)
def update_reward_detail(reward_id: int, reward_update: RewardUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Update reward info (status, issued_time).
    - Only admin can update.
    """
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update rewards")
    reward = get_reward(db, reward_id)
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")
    updated = update_reward(db, reward_id, reward_update)
    return RewardRead.from_orm(updated)
