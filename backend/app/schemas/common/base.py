"""
Base schemas and mixins for consistent schema patterns across the application.
These should be inherited by domain-specific schemas to reduce duplication.
"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field


# Type variable for generic response schemas
T = TypeVar("T")


class TimestampMixin(BaseModel):
    """Mixin for created_at and updated_at timestamps."""

    created_at: datetime
    updated_at: Optional[datetime] = None


class AuditMixin(BaseModel):
    """Mixin for audit fields (created_by, updated_by)."""

    created_by: Optional[int] = None
    updated_by: Optional[int] = None


class StatusMixin(BaseModel):
    """Mixin for common status-related fields."""

    is_active: bool = True
    is_deleted: bool = False


class BaseCreateSchema(BaseModel):
    """
    Base schema for create operations.
    Extend this for domain-specific create schemas.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class BaseUpdateSchema(BaseModel):
    """
    Base schema for update operations where all fields are optional.
    Extend this for domain-specific update schemas.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class BaseResponse(BaseModel):
    """
    Base response schema with common fields.
    All response schemas should inherit from this.
    """

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PaginationParams(BaseModel):
    """Standard pagination parameters."""

    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum records to return")


class SortParams(BaseModel):
    """Standard sorting parameters."""

    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="Sort order")


class FilterParams(BaseModel):
    """Base filter parameters. Extend for domain-specific filters."""

    search: Optional[str] = Field(None, description="Search term")
    status: Optional[str] = Field(None, description="Filter by status")


class ListQueryParams(PaginationParams, SortParams):
    """Combined query parameters for list endpoints."""

    search: Optional[str] = Field(None, description="Search term")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response wrapper.
    Usage: PaginatedResponse[CourierResponse]
    """

    items: List[T]
    total: int
    skip: int
    limit: int
    has_more: bool = False

    @classmethod
    def create(cls, items: List[T], total: int, skip: int, limit: int):
        """Factory method to create paginated response."""
        return cls(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + len(items)) < total,
        )


class BulkActionResponse(BaseModel):
    """Response for bulk operations."""

    success: bool
    affected_count: int
    failed_count: int = 0
    errors: List[str] = Field(default_factory=list)
    message: Optional[str] = None
