"""
Global exception handler for FastAPI.
"""
import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

class BusinessError(Exception):
    """Custom business logic error."""
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions and return 500 error."""
    logging.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"}
    )

async def custom_http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTPException using FastAPI's default handler."""
    return await http_exception_handler(request, exc)

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors (422)."""
    logging.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body}
    )

async def db_integrity_exception_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """Handle database integrity errors (409)."""
    logging.error(f"Database integrity error: {exc}")
    return JSONResponse(
        status_code=409,
        content={"detail": "Database integrity error", "msg": str(exc)}
    )

async def business_exception_handler(request: Request, exc: BusinessError) -> JSONResponse:
    """Handle business logic errors (custom)."""
    logging.warning(f"Business exception: {exc.message}")
    return JSONResponse(
        status_code=exc.code,
        content={"detail": exc.message}
    )
