"""
Standard API response schemas for consistent response formatting.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    """Standard success response wrapper."""

    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Standard error response wrapper."""

    success: bool = False
    error: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class ValidationErrorDetail(BaseModel):
    """Detail for a single validation error."""

    field: str
    message: str
    type: str


class ValidationErrorResponse(BaseModel):
    """Response for validation errors."""

    success: bool = False
    error: str = "Validation Error"
    error_code: str = "VALIDATION_ERROR"
    details: List[ValidationErrorDetail]


class DeleteResponse(BaseModel):
    """Response for delete operations."""

    success: bool = True
    deleted_id: int
    message: str = "Successfully deleted"


class BulkDeleteResponse(BaseModel):
    """Response for bulk delete operations."""

    success: bool = True
    deleted_count: int
    failed_ids: List[int] = Field(default_factory=list)
    message: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Response for health check endpoint."""

    status: str = "healthy"
    version: str
    environment: str
    database: bool = True
    cache: bool = True
    timestamp: str
