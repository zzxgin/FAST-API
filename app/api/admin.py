"""Admin API endpoints for user/task management, risk control and statistics."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.admin import AdminUserItem, AdminUserUpdate, AdminTaskItem, AdminTaskUpdate, SiteStatistics
from app.core.response import success_response
from app.crud import admin as crud_admin
from app.schemas.user import UserRead

router = APIRouter(prefix="/api/admin", tags=["admin"])

def admin_only(user = Depends(get_current_user)):
    if user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user


@router.get("/users")
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(admin_only)):
    users = crud_admin.list_users(db, skip=skip, limit=limit)
    return success_response(data=users, message="获取成功")


@router.put("/users/{user_id}")
def update_user(user_id: int, update: AdminUserUpdate, db: Session = Depends(get_db), _=Depends(admin_only)):
    user = crud_admin.update_user(db, user_id, role=update.role, is_active=update.is_active)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return success_response(data=user, message="更新成功")


@router.get("/tasks")
def list_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(admin_only)):
    tasks = crud_admin.list_tasks(db, skip=skip, limit=limit)
    return success_response(data=tasks, message="获取成功")


@router.put("/tasks/{task_id}")
def update_task(task_id: int, update: AdminTaskUpdate, db: Session = Depends(get_db), _=Depends(admin_only)):
    if update.status is None:
        raise HTTPException(status_code=400, detail="No update fields provided")
    task = crud_admin.update_task_status(db, task_id, update.status)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return success_response(data=task, message="更新成功")


@router.post("/tasks/{task_id}/flag")
def flag_task(task_id: int, db: Session = Depends(get_db), _=Depends(admin_only)):
    task = crud_admin.flag_task(db, task_id, flagged=True)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return success_response(data=task, message="标记成功")


@router.get("/statistics")
def site_statistics(db: Session = Depends(get_db), _=Depends(admin_only)):
    stats = crud_admin.get_site_statistics(db)
    return success_response(data=stats, message="获取成功")
