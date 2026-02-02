from datetime import datetime, timezone
from typing import Any, Generic, Optional, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(from_attributes=True)

    success: bool = Field(..., description="Indicates if the request was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(default=None, description="Response data payload")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Response timestamp in ISO format",
    )
    status_code: int = Field(..., description="HTTP status code")

    @classmethod
    def success_response(
        cls, data: T = None, message: str = "Success", status_code: int = 200
    ) -> "ApiResponse[T]":
        return cls(
            success=True,
            message=message,
            data=jsonable_encoder(data),
            status_code=status_code,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    @classmethod
    def error_response(
        cls, message: str, status_code: int = 400, data: Optional[T] = None
    ) -> "ApiResponse[T]":
        return cls(
            success=False,
            message=message,
            data=jsonable_encoder(data) if data else None,
            status_code=status_code,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def model_dump(self, **kwargs):
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)
