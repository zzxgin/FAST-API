"""
统一的 API 响应格式模块
提供标准的成功和失败响应结构
"""

from typing import Any, Optional, TypeVar, Generic, Type
from pydantic import BaseModel
from fastapi.responses import JSONResponse


T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """
    统一的 API 响应格式
    
    Attributes:
        code: 响应代码，0 表示成功，非 0 表示失败
        message: 响应消息
        data: 响应数据
    
    Example:
        >>> # 在路由装饰器中使用
        >>> @router.post("/users", response_model=ApiResponse[UserRead])
        >>> def create_user(...):
        >>>     return success_response(data=user, message="创建成功")
    """
    code: int
    message: str
    data: Optional[T] = None
    
    class Config:
        # 允许从 ORM 模型创建
        from_attributes = True


def success_response(data: Any = None, message: str = "操作成功") -> JSONResponse:
    """
    创建成功响应
    
    当使用 response_model=ApiResponse[SomeModel] 时，返回字典会被自动验证和序列化为 JSON。
    
    Args:
        data: 响应数据（可以是 Pydantic 模型、字典、列表等）
        message: 成功消息
    
    Returns:
        标准的成功响应字典（FastAPI 的 response_model 会自动序列化为 JSON）
    
    Example:
        >>> @router.post("/users", response_model=ApiResponse[UserRead])
        >>> def create_user(...):
        >>>     return success_response(data=user, message="创建成功")
    
    Note:
        - FastAPI 会根据 response_model 自动处理序列化
        - Pydantic 模型会自动转换为 JSON 兼容的字典
        - 不需要手动调用 .dict() 或 json.dumps()
    """
    return {
        "code": 0,
        "message": message,
        "data": data
    }


def error_response(code: int, message: str, data: Any = None) -> dict:
    """
    创建错误响应
    
    Args:
        code: 错误代码（非0，通常使用 HTTP 状态码）
        message: 错误消息
        data: 附加错误数据（可选）
    
    Returns:
        标准的错误响应字典
    
    Example:
        >>> return error_response(code=404, message="用户不存在")
    """
    return {
        "code": code,
        "message": message,
        "data": data
    }

