"""
Reward API routes for issuing and managing rewards.
All endpoints use OpenAPI English doc comments.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import ApiResponse, success_response
from app.core.security import get_current_user
from app.crud.reward import (
    create_reward,
    get_reward,
    get_reward_stats,
    get_rewards_by_user,
    list_rewards,
    update_reward,
)
from app.schemas.reward import (
    RewardCreate,
    RewardRead,
    RewardStats,
    RewardUpdate,
)

router = APIRouter(prefix="/api/reward", tags=["reward"])


@router.post("/issue", response_model=ApiResponse[RewardRead])
def issue_reward(reward: RewardCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Issue a reward to a user for an assignment.
    - Only admin can issue rewards.
    """
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admin can issue rewards")
    created = create_reward(db, reward)
    return success_response(data=RewardRead.from_orm(created), message="奖励发放成功")
@router.get("/lists", response_model=ApiResponse[List[RewardRead]])
def list_rewards_api(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all rewards with pagination.

    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=403, detail="Only admin can list all rewards"
        )
    rewards = list_rewards(db, skip=skip, limit=limit)
    return success_response(
        data=[RewardRead.from_orm(r) for r in rewards], message="获取成功"
    )
@router.get("/{reward_id}", response_model=ApiResponse[RewardRead])
def get_reward_detail(reward_id: int, db: Session = Depends(get_db)):
    """
    Get reward detail by ID.
    """
    reward = get_reward(db, reward_id)
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")
    return success_response(data=RewardRead.from_orm(reward), message="获取成功")

@router.get("/user/{user_id}", response_model=ApiResponse[List[RewardRead]])
def list_rewards_by_user(user_id: int, db: Session = Depends(get_db)):
    """
    List all rewards for a user.
    """
    rewards = get_rewards_by_user(db, user_id)
    return success_response(
        data=[RewardRead.from_orm(r) for r in rewards],
        message="获取成功"
    )

@router.put("/{reward_id}", response_model=ApiResponse[RewardRead])
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
    return success_response(data=RewardRead.from_orm(updated), message="更新成功")

@router.get("/stats", response_model=ApiResponse[RewardStats])
def get_reward_statistics(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=403, detail="Only admin can view reward statistics"
        )
    
    stats = get_reward_stats(db)
    return success_response(data=stats, message="获取统计信息成功")

