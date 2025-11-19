"""
全局异常处理器模块
处理所有 FastAPI 应用中的异常，并返回统一的错误响应格式
"""
import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST

from app.core.response import error_response


# 配置日志
logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    处理所有未捕获的异常
    
    Args:
        request: FastAPI 请求对象
        exc: 异常实例
    
    Returns:
        包含错误信息的 JSON 响应
    """
    logger.error(f"Unhandled exception at {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            code=HTTP_500_INTERNAL_SERVER_ERROR,
            message="服务器内部错误，请稍后重试"
        )
    )


async def custom_http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    处理 HTTP 异常（如 404, 403 等）
    
    Args:
        request: FastAPI 请求对象
        exc: HTTPException 实例
    
    Returns:
        包含错误信息的 JSON 响应
    """
    logger.warning(f"HTTP exception at {request.url}: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            code=exc.status_code,
            message=exc.detail or "请求失败"
        )
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    处理请求数据验证错误（422）
    
    Args:
        request: FastAPI 请求对象
        exc: RequestValidationError 实例
    
    Returns:
        包含详细验证错误信息的 JSON 响应
    """
    errors = exc.errors()
    logger.warning(f"Validation error at {request.url}: {errors}")
    
    # 格式化验证错误信息
    formatted_errors = []
    for error in errors:
        field = " -> ".join(str(loc) for loc in error["loc"])
        formatted_errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=422,
        content=error_response(
            code=422,
            message="请求数据验证失败",
            data={"errors": formatted_errors}
        )
    )


async def db_integrity_exception_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """
    处理数据库完整性约束错误（如唯一键冲突）
    
    Args:
        request: FastAPI 请求对象
        exc: IntegrityError 实例
    
    Returns:
        包含错误信息的 JSON 响应
    """
    logger.error(f"Database integrity error at {request.url}: {exc}")
    
    # 尝试提取更友好的错误消息
    error_msg = str(exc.orig) if hasattr(exc, 'orig') else str(exc)
    
    if "Duplicate entry" in error_msg or "UNIQUE constraint" in error_msg:
        message = "数据已存在，违反唯一性约束"
    elif "foreign key constraint" in error_msg.lower():
        message = "数据关联错误，请检查相关数据是否存在"
    else:
        message = "数据库约束冲突"
    
    return JSONResponse(
        status_code=409,
        content=error_response(
            code=409,
            message=message
        )
    )


async def db_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    处理其他 SQLAlchemy 数据库错误
    
    Args:
        request: FastAPI 请求对象
        exc: SQLAlchemyError 实例
    
    Returns:
        包含错误信息的 JSON 响应
    """
    logger.error(f"Database error at {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            code=HTTP_500_INTERNAL_SERVER_ERROR,
            message="数据库操作失败，请稍后重试"
        )
    )

