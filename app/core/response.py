"""
Unified API response format module.
Provides standard success and failure response structures.
"""

from typing import Any, Optional, TypeVar, Generic, Type
from pydantic import BaseModel


T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """
    Unified API response format.
    
    Attributes:
        code: Response code, 0 indicates success, non-zero indicates failure.
        message: Response message.
        data: Response data.
    
    Example:
        >>> # Use in router decorator
        >>> @router.post("/users", response_model=ApiResponse[UserRead])
        >>> def create_user(...):
        >>>     return success_response(data=user, message="Created successfully")
    """
    code: int
    message: str
    data: Optional[T] = None
    
    class Config:
        # Allow creation from ORM models
        orm_mode = True


def success_response(data: Any = None, message: str = "Operation successful") -> dict:
    """
    Create a success response.
    
    When using response_model=ApiResponse[SomeModel], the returned dictionary will be automatically validated and serialized to JSON.
    
    Args:
        data: Response data (can be Pydantic model, dict, list, etc.).
        message: Success message.
    
    Returns:
        Standard success response dictionary (FastAPI's response_model will automatically serialize to JSON).
    
    Example:
        >>> @router.post("/users", response_model=ApiResponse[UserRead])
        >>> def create_user(...):
        >>>     return success_response(data=user, message="Created successfully")
    
    Note:
        - FastAPI will automatically handle serialization based on response_model.
        - Pydantic models will be automatically converted to JSON-compatible dictionaries.
        - No need to manually call .dict() or json.dumps().
    """
    return {
        "code": 0,
        "message": message,
        "data": data
    }


def error_response(code: int, message: str, data: Any = None) -> dict:
    """
    Create an error response.
    
    Args:
        code: Error code (non-zero, usually HTTP status code).
        message: Error message.
        data: Additional error data (optional).
    
    Returns:
        Standard error response dictionary.
    
    Example:
        >>> return error_response(code=404, message="User not found")
    """
    return {
        "code": code,
        "message": message,
        "data": data
    }

