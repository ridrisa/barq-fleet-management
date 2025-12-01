"""Analytics schemas"""

from app.schemas.analytics.performance import (
    PerformanceBase,
    PerformanceCreate,
    PerformanceUpdate,
    PerformanceResponse,
    PerformanceList,
    PerformanceStats,
    TopPerformer,
    PerformanceTrend,
    CourierComparison,
    DateRangeQuery,
    PerformanceBulkCreate,
)

__all__ = [
    # Base schemas
    "PerformanceBase",
    "PerformanceCreate",
    "PerformanceUpdate",
    "PerformanceResponse",
    "PerformanceList",
    # Analytics schemas
    "PerformanceStats",
    "TopPerformer",
    "PerformanceTrend",
    "CourierComparison",
    "DateRangeQuery",
    "PerformanceBulkCreate",
]
