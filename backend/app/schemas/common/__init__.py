"""
Common/Shared Pydantic Schemas for BARQ Fleet Management

This module provides reusable base schemas and mixins that can be inherited
by domain-specific schemas to reduce code duplication.
"""

from app.schemas.common.base import (
    BaseResponse,
    BaseCreateSchema,
    BaseUpdateSchema,
    PaginatedResponse,
    BulkActionResponse,
    TimestampMixin,
    AuditMixin,
    StatusMixin,
    PaginationParams,
    SortParams,
    FilterParams,
    ListQueryParams,
)
from app.schemas.common.statistics import (
    BaseStatistics,
    CountByStatusResponse,
    TrendDataPoint,
    TrendResponse,
    SummaryStatistics,
)
from app.schemas.common.responses import (
    SuccessResponse,
    ErrorResponse,
    ValidationErrorDetail,
    ValidationErrorResponse,
    DeleteResponse,
    BulkDeleteResponse,
)

__all__ = [
    # Base schemas
    "BaseResponse",
    "BaseCreateSchema",
    "BaseUpdateSchema",
    "PaginatedResponse",
    "BulkActionResponse",
    # Mixins
    "TimestampMixin",
    "AuditMixin",
    "StatusMixin",
    # Query params
    "PaginationParams",
    "SortParams",
    "FilterParams",
    "ListQueryParams",
    # Statistics
    "BaseStatistics",
    "CountByStatusResponse",
    "TrendDataPoint",
    "TrendResponse",
    "SummaryStatistics",
    # Responses
    "SuccessResponse",
    "ErrorResponse",
    "ValidationErrorDetail",
    "ValidationErrorResponse",
    "DeleteResponse",
    "BulkDeleteResponse",
]
