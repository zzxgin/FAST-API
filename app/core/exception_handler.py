"""Global exception handler module.

Handles all exceptions in FastAPI application and returns unified error response format.
"""
import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST

from app.core.response import error_response


# Configure logging
logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions.
    
    Args:
        request: FastAPI request object.
        exc: Exception instance.
    
    Returns:
        JSONResponse containing error information.
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
    """Handle HTTP exceptions (e.g., 404, 403).
    
    Args:
        request: FastAPI request object.
        exc: HTTPException instance.
    
    Returns:
        JSONResponse containing error information.
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
    """Handle request validation errors (422).
    
    Args:
        request: FastAPI request object.
        exc: RequestValidationError instance.
    
    Returns:
        JSONResponse containing detailed validation error information.
    """
    errors = exc.errors()
    logger.warning(f"Validation error at {request.url}: {errors}")
    
    # Format validation error messages
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
    """Handle database integrity constraint errors (e.g., unique key violations).
    
    Args:
        request: FastAPI request object.
        exc: IntegrityError instance.
    
    Returns:
        JSONResponse containing error information.
    """
    logger.error(f"Database integrity error at {request.url}: {exc}")
    
    # Try to extract more friendly error message
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
    """Handle other SQLAlchemy database errors.
    
    Args:
        request: FastAPI request object.
        exc: SQLAlchemyError instance.
    
    Returns:
        JSONResponse containing error information.
    """
    logger.error(f"Database error at {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            code=HTTP_500_INTERNAL_SERVER_ERROR,
            message="数据库操作失败，请稍后重试"
        )
    )

