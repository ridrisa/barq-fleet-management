"""Common Analytics Schemas

Shared schemas used across analytics endpoints.
"""
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, Field
from enum import Enum


class PeriodType(str, Enum):
    """Time period types for analytics"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class ComparisonType(str, Enum):
    """Comparison types for analytics"""
    PREVIOUS_PERIOD = "previous_period"
    SAME_PERIOD_LAST_YEAR = "same_period_last_year"
    CUSTOM = "custom"


class TrendDirection(str, Enum):
    """Trend direction indicators"""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"


class PerformanceCategory(str, Enum):
    """Performance category classifications"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"


class DateRangeParams(BaseModel):
    """Common date range parameters"""
    start_date: date = Field(..., description="Start date for analytics")
    end_date: date = Field(..., description="End date for analytics")
    comparison_type: Optional[ComparisonType] = Field(
        ComparisonType.PREVIOUS_PERIOD,
        description="Type of comparison period"
    )
    period_type: Optional[PeriodType] = Field(
        PeriodType.DAILY,
        description="Aggregation period"
    )


class MetricValue(BaseModel):
    """Single metric value with metadata"""
    value: float = Field(..., description="Metric value")
    label: str = Field(..., description="Metric label")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    change_percentage: Optional[float] = Field(None, description="Percentage change")
    trend: Optional[TrendDirection] = Field(None, description="Trend direction")
    target: Optional[float] = Field(None, description="Target value")
    is_good: Optional[bool] = Field(True, description="Whether current state is good")


class TrendDataPoint(BaseModel):
    """Single point in a trend line"""
    period: str = Field(..., description="Period label (date or period name)")
    value: float = Field(..., description="Metric value for period")
    label: Optional[str] = Field(None, description="Optional display label")


class ComparisonData(BaseModel):
    """Comparison between current and previous periods"""
    current_value: float
    previous_value: float
    change_percentage: float
    change_absolute: float
    trend: TrendDirection
    is_improvement: bool


class KPICard(BaseModel):
    """KPI card data for dashboard"""
    title: str
    value: float
    formatted_value: str
    unit: Optional[str] = None
    icon: Optional[str] = None
    change_percentage: Optional[float] = None
    trend: Optional[TrendDirection] = None
    color: Optional[str] = None
    target: Optional[float] = None
    progress: Optional[float] = None


class ChartData(BaseModel):
    """Generic chart data structure"""
    title: str
    chart_type: str = Field(..., description="Type of chart (line, bar, pie, etc.)")
    data: List[Dict[str, Any]]
    labels: Optional[List[str]] = None
    datasets: Optional[List[Dict[str, Any]]] = None


class TopPerformerItem(BaseModel):
    """Single top performer entry"""
    rank: int
    id: int
    name: str
    value: float
    metric_name: str
    details: Optional[Dict[str, Any]] = None


class DistributionBucket(BaseModel):
    """Bucket in a distribution analysis"""
    range_label: str
    count: int
    percentage: float
    value: Optional[float] = None


class AlertItem(BaseModel):
    """Alert or notification item"""
    id: int
    severity: str = Field(..., description="Severity level (critical, warning, info)")
    title: str
    message: str
    timestamp: datetime
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    is_resolved: bool = False


class ExportRequest(BaseModel):
    """Request for data export"""
    format: str = Field(..., description="Export format (csv, excel, json, pdf)")
    include_columns: Optional[List[str]] = Field(None, description="Columns to include")
    exclude_columns: Optional[List[str]] = Field(None, description="Columns to exclude")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")
    sort_by: Optional[str] = Field(None, description="Column to sort by")
    sort_desc: bool = Field(False, description="Sort in descending order")


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(50, ge=1, le=1000, description="Items per page")


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    data: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
