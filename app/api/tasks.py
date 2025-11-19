"""
Task API routes for publishing, accepting, and managing tasks.

All endpoints use OpenAPI English doc comments.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.crud.task import create_task, get_task, get_tasks, update_task, accept_task, search_tasks, get_task_list
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.response import success_response, ApiResponse
from typing import List

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.post("/publish", response_model=ApiResponse[TaskRead])
def publish_task(task: TaskCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Publish a new task.
    - Only users with publisher and admin role can publish.
    """
    if current_user.role.value not in ["publisher", "admin"]:
        raise HTTPException(status_code=403, detail="Only publisher and admin can publish tasks")
    created = create_task(db, task, publisher_id=current_user.id)
    return success_response(data=TaskRead.from_orm(created), message="任务发布成功")

@router.get("/search/", response_model=ApiResponse[List[TaskRead]])
def search_task(
    keyword: str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Search tasks by keyword in title.
    """
    tasks = search_tasks(db, keyword, skip=skip, limit=limit)
    return success_response(
        data=[TaskRead.from_orm(t) for t in tasks],
        message="搜索成功"
    )

@router.get("/{task_id}", response_model=ApiResponse[TaskRead])
def get_task_detail(task_id: int, db: Session = Depends(get_db)):
    """
    Get task detail by ID.
    """
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return success_response(data=TaskRead.from_orm(task), message="获取成功")

@router.get("/", response_model=ApiResponse[List[TaskRead]])
def list_tasks(
    skip: int = 0,
    limit: int = 20,
    status: str = None,
    order_by: str = None,
    db: Session = Depends(get_db)
):
    """
    List all tasks (paginated, filterable, sortable).
    """
    tasks = get_task_list(db, skip=skip, limit=limit, status=status, order_by=order_by)
    return success_response(
        data=[TaskRead.from_orm(t) for t in tasks],
        message="获取成功"
    )

@router.put("/{task_id}", response_model=ApiResponse[TaskRead])
def update_task_detail(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Update task info (title, description, reward_amount, status).
    - Only publisher or admin can update.
    """
    if current_user.role.value not in ["publisher", "admin"]:
        raise HTTPException(status_code=403, detail="Only publisher or admin can update tasks")
    task = update_task(db, task_id, task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return success_response(data=TaskRead.from_orm(task), message="更新成功")

@router.post("/accept/{task_id}", response_model=ApiResponse[TaskRead])
def accept_task_api(task_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Accept a task (change status to accepted).
    """
    task = accept_task(db, task_id)
    if not task:
        raise HTTPException(status_code=400, detail="Task cannot be accepted")
    return success_response(data=TaskRead.from_orm(task), message="接取成功")
