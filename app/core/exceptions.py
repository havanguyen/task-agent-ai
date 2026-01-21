"""
Global Exception Handler and API Response Format
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Any, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger("app")


class ApiResponse(BaseModel):
    """Standard API Response Format"""

    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[list] = None


def create_response(
    success: bool,
    message: str,
    data: Any = None,
    errors: list = None,
    status_code: int = 200,
) -> JSONResponse:
    """Create a standardized JSON response"""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": success,
            "message": message,
            "data": data,
            "errors": errors,
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.url}")
    return create_response(
        success=False, message=str(exc.detail), status_code=exc.status_code
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({"field": field, "message": error["msg"], "type": error["type"]})

    logger.warning(f"Validation error: {errors} - {request.url}")
    return create_response(
        success=False, message="Validation error", errors=errors, status_code=422
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {exc} - {request.url}", exc_info=True)
    return create_response(
        success=False, message="Internal server error", status_code=500
    )
