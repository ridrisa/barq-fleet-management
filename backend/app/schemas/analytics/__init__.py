"""Analytics schemas"""

from app.schemas.analytics.common import (
    AlertItem,
    ChartData,
    ComparisonData,
    ComparisonType,
    DateRangeParams,
    DistributionBucket,
    ExportRequest,
    KPICard,
    MetricValue,
    PaginatedResponse,
    PaginationParams,
    PerformanceCategory,
    PeriodType,
    TopPerformerItem,
    TrendDataPoint,
    TrendDirection,
)
from app.schemas.analytics.performance import (
    CourierComparison,
    DateRangeQuery,
    PerformanceBase,
    PerformanceBulkCreate,
    PerformanceCreate,
    PerformanceList,
    PerformanceResponse,
    PerformanceStats,
    PerformanceTrend,
    PerformanceUpdate,
    TopPerformer,
)
from app.schemas.analytics.statistics import (
    # Vehicle statistics
    VehicleStatusBreakdown,
    VehicleStatisticsResponse,
    # Courier statistics
    CourierStatusBreakdown,
    SponsorshipBreakdown,
    ProjectBreakdown,
    CourierStatisticsResponse,
    # Dashboard statistics
    DashboardInsights,
    DashboardStatsResponse,
    # Chart data
    ChartDataPoint,
    DeliveryTrendPoint,
    MonthlyTrendPoint,
    FleetStatusResponse,
    CourierStatusChartResponse,
    SponsorshipDistributionResponse,
    ProjectDistributionResponse,
    CityDistributionResponse,
    DeliveryTrendsResponse,
    MonthlyTrendsResponse,
    # Alerts
    DashboardAlert,
    AlertSummary,
    DashboardAlertsResponse,
    # Top performers
    TopCourierItem,
    TopCouriersResponse,
    # Recent activity
    ActivityItem,
    RecentActivityResponse,
    # Health score
    HealthScoreBreakdown,
    FleetHealthScore,
    # Executive summary
    SummaryMetrics,
    SummaryTrends,
    ExecutiveSummaryResponse,
    # Aggregated analytics
    FleetOverviewResponse,
    OperationsOverviewResponse,
    # KPI Dashboard
    KPIMetric,
    KPIDashboardResponse,
)

__all__ = [
    # Performance schemas
    "PerformanceBase",
    "PerformanceCreate",
    "PerformanceUpdate",
    "PerformanceResponse",
    "PerformanceList",
    "PerformanceStats",
    "TopPerformer",
    "PerformanceTrend",
    "CourierComparison",
    "DateRangeQuery",
    "PerformanceBulkCreate",
    # Common analytics schemas
    "PeriodType",
    "ComparisonType",
    "TrendDirection",
    "PerformanceCategory",
    "DateRangeParams",
    "MetricValue",
    "TrendDataPoint",
    "ComparisonData",
    "KPICard",
    "ChartData",
    "TopPerformerItem",
    "DistributionBucket",
    "AlertItem",
    "ExportRequest",
    "PaginationParams",
    "PaginatedResponse",
    # Statistics schemas - Vehicle
    "VehicleStatusBreakdown",
    "VehicleStatisticsResponse",
    # Statistics schemas - Courier
    "CourierStatusBreakdown",
    "SponsorshipBreakdown",
    "ProjectBreakdown",
    "CourierStatisticsResponse",
    # Statistics schemas - Dashboard
    "DashboardInsights",
    "DashboardStatsResponse",
    # Statistics schemas - Charts
    "ChartDataPoint",
    "DeliveryTrendPoint",
    "MonthlyTrendPoint",
    "FleetStatusResponse",
    "CourierStatusChartResponse",
    "SponsorshipDistributionResponse",
    "ProjectDistributionResponse",
    "CityDistributionResponse",
    "DeliveryTrendsResponse",
    "MonthlyTrendsResponse",
    # Statistics schemas - Alerts
    "DashboardAlert",
    "AlertSummary",
    "DashboardAlertsResponse",
    # Statistics schemas - Top performers
    "TopCourierItem",
    "TopCouriersResponse",
    # Statistics schemas - Activity
    "ActivityItem",
    "RecentActivityResponse",
    # Statistics schemas - Health
    "HealthScoreBreakdown",
    "FleetHealthScore",
    # Statistics schemas - Executive summary
    "SummaryMetrics",
    "SummaryTrends",
    "ExecutiveSummaryResponse",
    # Statistics schemas - Aggregated
    "FleetOverviewResponse",
    "OperationsOverviewResponse",
    # Statistics schemas - KPI
    "KPIMetric",
    "KPIDashboardResponse",
]
