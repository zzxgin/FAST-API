"""
统一的 API 响应格式模块
提供标准的成功和失败响应结构
"""

from typing import Any, Optional, TypeVar, Generic
from pydantic import BaseModel


T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """
    统一的 API 响应格式
    
    Attributes:
        code: 响应代码，0 表示成功，非 0 表示失败
        message: 响应消息
        data: 响应数据
    """
    code: int
    message: str
    data: Optional[T] = None


def success_response(data: Any = None, message: str = "操作成功") -> dict:
    """
    创建成功响应
    
    Args:
        data: 响应数据
        message: 成功消息
    
    Returns:
        标准的成功响应字典
    
    Example:
        >>> return success_response(data=user, message="用户创建成功")
        {"code": 0, "message": "用户创建成功", "data": {...}}
    """
    return {
        "code": 0,
        "message": message,
        "data": data
    }

