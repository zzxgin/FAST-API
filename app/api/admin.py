"""Admin API routes for user/task management, risk control and site statistics.
All endpoints use OpenAPI English doc comments.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.admin import AdminUserItem, AdminUserUpdate, AdminTaskItem, AdminTaskUpdate, SiteStatistics
from app.core.response import success_response, ApiResponse
from app.crud import admin as crud_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])

def admin_only(user = Depends(get_current_user)):
    """
    Verify admin privileges.
    - Only users with admin role can access.
    """
    if user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user


@router.get("/users", response_model=ApiResponse[List[AdminUserItem]])
def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=1000, description="Number of records to return"),
    username: str = Query(None, description="Filter by username (fuzzy search)"),
    db: Session = Depends(get_db),
    _=Depends(admin_only)
):
    """
    Get all users list with pagination.
    - Admin only.
    - Max limit: 100
    """
    users = crud_admin.list_users(db, skip=skip, limit=limit, username=username)
    return success_response(data=users, message="Retrieved successfully")


@router.put("/users/{user_id}", response_model=ApiResponse[AdminUserItem])
def update_user(user_id: int, update: AdminUserUpdate, db: Session = Depends(get_db), _=Depends(admin_only)):
    """
    Update user role, password, username or email.
    - Admin only.
    """
    user = crud_admin.update_user(
        db, 
        user_id, 
        username=update.username,
        email=update.email,
        role=update.role, 
        password=update.password
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return success_response(data=user, message="Updated successfully")


@router.get("/tasks", response_model=ApiResponse[List[AdminTaskItem]])
def list_tasks(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    _=Depends(admin_only)
):
    """
    Get all tasks list with pagination.
    - Admin only.
    - Max limit: 1000
    """
    tasks = crud_admin.list_tasks(db, skip=skip, limit=limit)
    return success_response(data=tasks, message="Retrieved successfully")


@router.put("/tasks/{task_id}", response_model=ApiResponse[AdminTaskItem])
def update_task(task_id: int, update: AdminTaskUpdate, db: Session = Depends(get_db), _=Depends(admin_only)):
    """
    Update task status.
    - Admin only.
    """
    if update.status is None:
        raise HTTPException(status_code=400, detail="No update fields provided")
    task = crud_admin.update_task_status(db, task_id, update.status)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return success_response(data=task, message="Updated successfully")


@router.post("/tasks/{task_id}/flag", response_model=ApiResponse[AdminTaskItem])
def flag_task(task_id: int, db: Session = Depends(get_db), _=Depends(admin_only)):
    """
    Flag a task as risky and close it.
    - Admin only.
    """
    task = crud_admin.flag_task(db, task_id, flagged=True)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return success_response(data=task, message="Flagged successfully")


@router.get("/statistics", response_model=ApiResponse[SiteStatistics])
def site_statistics(db: Session = Depends(get_db), _=Depends(admin_only)):
    """
    Get site-wide statistics and metrics.
    - Admin only.
    - Returns: total users, tasks, assignments, rewards, pending reviews.
    """
    stats = crud_admin.get_site_statistics(db)
    return success_response(data=stats, message="Retrieved successfully")
