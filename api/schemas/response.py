"""Response schemas for the API."""

from pydantic import BaseModel
from typing import Any, Optional


class PredictionResponse(BaseModel):
    """Standard prediction response."""

    success: bool
    message: str
    data: Optional[dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Error response."""

    success: bool = False
    message: str
    detail: Optional[str] = None
