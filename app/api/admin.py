"""Admin API endpoints for user/task management, risk control and statistics."""
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
    """
    管理员权限验证依赖
    
    验证当前用户是否具有管理员权限。此依赖函数用于保护管理员专用接口。
    
    Args:
        user: 当前登录用户（从 JWT token 解析）
    
    Returns:
        User: 验证通过的管理员用户对象
    
    Raises:
        HTTPException: 403 如果用户不是管理员
    """
    if user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user


@router.get("/users", response_model=ApiResponse[List[AdminUserItem]])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(admin_only)):
    """
    获取用户列表
    
    管理员专用接口，用于查看和管理系统中的所有用户。
    
    Args:
        skip: 跳过的记录数，用于分页
        limit: 返回的最大记录数
        db: 数据库会话
        _: 管理员权限验证
    
    Returns:
        JSONResponse: 包含用户列表的响应
        - code: 0 表示成功
        - message: "获取成功"
        - data: 用户列表数组
    
    Raises:
        HTTPException: 403 如果非管理员访问
    """
    users = crud_admin.list_users(db, skip=skip, limit=limit)
    return success_response(data=users, message="获取成功")


@router.put("/users/{user_id}", response_model=ApiResponse[AdminUserItem])
def update_user(user_id: int, update: AdminUserUpdate, db: Session = Depends(get_db), _=Depends(admin_only)):
    """
    更新用户信息
    
    管理员可以修改用户的角色（普通用户/管理员）和激活状态。
    
    Args:
        user_id: 要更新的用户ID
        update: 更新数据，包含 role（角色）和 is_active（是否激活）
        db: 数据库会话
        _: 管理员权限验证
    
    Returns:
        JSONResponse: 包含更新后用户信息的响应
        - code: 0 表示成功
        - message: "更新成功"
        - data: 更新后的用户对象
    
    Raises:
        HTTPException: 404 如果用户不存在
        HTTPException: 403 如果非管理员访问
    """
    user = crud_admin.update_user(db, user_id, role=update.role, is_active=update.is_active)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return success_response(data=user, message="更新成功")


@router.get("/tasks", response_model=ApiResponse[List[AdminTaskItem]])
def list_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(admin_only)):
    """
    获取任务列表
    
    管理员专用接口，用于查看系统中的所有任务，包括待审核、进行中、已完成等状态。
    
    Args:
        skip: 跳过的记录数，用于分页
        limit: 返回的最大记录数
        db: 数据库会话
        _: 管理员权限验证
    
    Returns:
        JSONResponse: 包含任务列表的响应
        - code: 0 表示成功
        - message: "获取成功"
        - data: 任务列表数组
    
    Raises:
        HTTPException: 403 如果非管理员访问
    """
    tasks = crud_admin.list_tasks(db, skip=skip, limit=limit)
    return success_response(data=tasks, message="获取成功")


@router.put("/tasks/{task_id}", response_model=ApiResponse[AdminTaskItem])
def update_task(task_id: int, update: AdminTaskUpdate, db: Session = Depends(get_db), _=Depends(admin_only)):
    """
    更新任务状态
    
    管理员可以修改任务状态（如审核通过、拒绝、关闭等）。
    
    Args:
        task_id: 要更新的任务ID
        update: 更新数据，包含 status（任务状态）
        db: 数据库会话
        _: 管理员权限验证
    
    Returns:
        JSONResponse: 包含更新后任务信息的响应
        - code: 0 表示成功
        - message: "更新成功"
        - data: 更新后的任务对象
    
    Raises:
        HTTPException: 400 如果没有提供更新字段
        HTTPException: 404 如果任务不存在
        HTTPException: 403 如果非管理员访问
    """
    if update.status is None:
        raise HTTPException(status_code=400, detail="No update fields provided")
    task = crud_admin.update_task_status(db, task_id, update.status)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return success_response(data=task, message="更新成功")


@router.post("/tasks/{task_id}/flag", response_model=ApiResponse[AdminTaskItem])
def flag_task(task_id: int, db: Session = Depends(get_db), _=Depends(admin_only)):
    """
    标记错误任务
    
    管理员可以将可疑或违规的任务标记为错误任务，用于风控管理。
    
    Args:
        task_id: 要标记的任务ID
        db: 数据库会话
        _: 管理员权限验证
    
    Returns:
        JSONResponse: 包含标记后任务信息的响应
        - code: 0 表示成功
        - message: "标记成功"
        - data: 标记后的任务对象
    
    Raises:
        HTTPException: 404 如果任务不存在
        HTTPException: 403 如果非管理员访问
    """
    task = crud_admin.flag_task(db, task_id, flagged=True)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return success_response(data=task, message="标记成功")


@router.get("/statistics", response_model=ApiResponse[SiteStatistics])
def site_statistics(db: Session = Depends(get_db), _=Depends(admin_only)):
    """
    获取站点统计数据
    
    管理员专用接口，返回平台的整体运营数据，包括用户数、任务数、
    完成率、活跃度等关键指标。
    
    Args:
        db: 数据库会话
        _: 管理员权限验证
    
    Returns:
        JSONResponse: 包含统计数据的响应
        - code: 0 表示成功
        - message: "获取成功"
        - data: 统计数据对象（SiteStatistics）
            - total_users: 总用户数
            - total_tasks: 总任务数
            - total_assignments: 总作业数
            - completion_rate: 完成率
            - etc.
    
    Raises:
        HTTPException: 403 如果非管理员访问
    """
    stats = crud_admin.get_site_statistics(db)
    return success_response(data=stats, message="获取成功")
