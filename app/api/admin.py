"""Admin API endpoints.

Provides endpoints for user/task management, risk control and site statistics.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.admin import AdminUserItem, AdminUserUpdate, AdminTaskItem, AdminTaskUpdate, SiteStatistics
from app.core.response import success_response, ApiResponse
from app.crud import admin as crud_admin
from app.schemas.user import UserRead

router = APIRouter(prefix="/api/admin", tags=["admin"])

def admin_only(user = Depends(get_current_user)):
    """Verify admin privileges.
    
    Args:
        user: Current authenticated user
    
    Returns:
        User object if admin
    
    Raises:
        HTTPException: 403 if not admin
    """
    if user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user


@router.get("/users", response_model=ApiResponse[List[AdminUserItem]])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(admin_only)):
    """Get all users list.
    
    Args:
        skip: Records to skip for pagination
        limit: Maximum records to return
    
    Returns:
        List of users
    """
    users = crud_admin.list_users(db, skip=skip, limit=limit)
    return success_response(data=users, message="获取成功")


@router.put("/users/{user_id}", response_model=ApiResponse[AdminUserItem])
def update_user(user_id: int, update: AdminUserUpdate, db: Session = Depends(get_db), _=Depends(admin_only)):
    """Update user role and active status.
    
    Args:
        user_id: User ID to update
        update: Update data (role, is_active)
    
    Returns:
        Updated user information
    """
    user = crud_admin.update_user(db, user_id, role=update.role, is_active=update.is_active)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return success_response(data=user, message="更新成功")


@router.get("/tasks", response_model=ApiResponse[List[AdminTaskItem]])
def list_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(admin_only)):
    """Get all tasks list.
    
    Args:
        skip: Records to skip for pagination
        limit: Maximum records to return
    
    Returns:
        List of tasks
    """
    tasks = crud_admin.list_tasks(db, skip=skip, limit=limit)
    return success_response(data=tasks, message="获取成功")


@router.put("/tasks/{task_id}", response_model=ApiResponse[AdminTaskItem])
def update_task(task_id: int, update: AdminTaskUpdate, db: Session = Depends(get_db), _=Depends(admin_only)):
    """Update task status.
    
    Args:
        task_id: Task ID to update
        update: Update data (status)
    
    Returns:
        Updated task information
    """
    if update.status is None:
        raise HTTPException(status_code=400, detail="No update fields provided")
    task = crud_admin.update_task_status(db, task_id, update.status)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return success_response(data=task, message="更新成功")


@router.post("/tasks/{task_id}/flag", response_model=ApiResponse[AdminTaskItem])
def flag_task(task_id: int, db: Session = Depends(get_db), _=Depends(admin_only)):
    """Flag a task as risky.
    
    Args:
        task_id: Task ID to flag
    
    Returns:
        Flagged task information
    """
    task = crud_admin.flag_task(db, task_id, flagged=True)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return success_response(data=task, message="标记成功")


@router.get("/statistics", response_model=ApiResponse[SiteStatistics])
def site_statistics(db: Session = Depends(get_db), _=Depends(admin_only)):
    """Get site-wide statistics and metrics.
    
    Provides comprehensive platform statistics for admin dashboard,
    including total users, tasks, assignments, rewards issued, active users,
    and pending reviews count.
    
    Args:
        db: Database session
        _: Admin privilege verification
    
    Returns:
        SiteStatistics object containing:
            - total_users: Total registered users
            - total_tasks: Total published tasks
            - total_assignments: Total task assignments
            - total_rewards_issued: Sum of all issued rewards
            - active_users: Users active in current period
            - pending_reviews: Assignments awaiting review
    """
    stats = crud_admin.get_site_statistics(db)
    return success_response(data=stats, message="获取成功")
