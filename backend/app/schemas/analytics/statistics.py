"""
Typed Statistics Schemas

Provides strongly-typed Pydantic schemas for statistics and analytics endpoints.
Replaces untyped dict responses with proper validation and documentation.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Vehicle Statistics
# ============================================================================


class VehicleStatusBreakdown(BaseModel):
    """Vehicle status distribution."""

    available: int = Field(ge=0, description="Number of available vehicles")
    assigned: int = Field(ge=0, description="Number of assigned vehicles")
    maintenance: int = Field(ge=0, description="Number of vehicles in maintenance")
    out_of_service: int = Field(ge=0, description="Number of vehicles out of service")


class VehicleStatisticsResponse(BaseModel):
    """Response schema for vehicle statistics endpoint."""

    total_vehicles: int = Field(ge=0, description="Total number of vehicles")
    active_vehicles: int = Field(ge=0, description="Number of active vehicles")
    inactive_vehicles: int = Field(ge=0, description="Number of inactive vehicles")
    maintenance_due: int = Field(ge=0, description="Vehicles with maintenance due")
    status_breakdown: VehicleStatusBreakdown
    utilization_rate: float = Field(ge=0, le=100, description="Vehicle utilization percentage")


# ============================================================================
# Courier Statistics
# ============================================================================


class CourierStatusBreakdown(BaseModel):
    """Courier status distribution."""

    active: int = Field(ge=0, description="Number of active couriers")
    inactive: int = Field(ge=0, description="Number of inactive couriers")
    on_leave: int = Field(ge=0, description="Number of couriers on leave")
    onboarding: int = Field(ge=0, description="Number of onboarding couriers")
    suspended: int = Field(ge=0, description="Number of suspended couriers")
    terminated: int = Field(ge=0, description="Number of terminated couriers")


class SponsorshipBreakdown(BaseModel):
    """Courier sponsorship distribution."""

    ajeer: int = Field(ge=0, description="Number of Ajeer couriers")
    inhouse: int = Field(ge=0, description="Number of in-house couriers")
    freelancer: int = Field(ge=0, description="Number of freelancer couriers")


class ProjectBreakdown(BaseModel):
    """Courier project type distribution."""

    ecommerce: int = Field(ge=0, description="E-commerce project couriers")
    food: int = Field(ge=0, description="Food delivery couriers")
    warehouse: int = Field(ge=0, description="Warehouse project couriers")
    barq: int = Field(ge=0, description="BARQ project couriers")


class CourierStatisticsResponse(BaseModel):
    """Response schema for courier statistics endpoint."""

    total_couriers: int = Field(ge=0, description="Total number of couriers")
    active_couriers: int = Field(ge=0, description="Number of active couriers")
    couriers_with_vehicle: int = Field(ge=0, description="Couriers with assigned vehicles")
    status_breakdown: CourierStatusBreakdown
    sponsorship_breakdown: SponsorshipBreakdown
    project_breakdown: ProjectBreakdown
    utilization_rate: float = Field(ge=0, le=100, description="Courier utilization percentage")


# ============================================================================
# Dashboard Statistics
# ============================================================================


class DashboardInsights(BaseModel):
    """Dashboard insights and health indicators."""

    fleet_health: str = Field(description="Fleet health status: good, needs_attention")
    courier_availability: str = Field(description="Courier availability: high, moderate, low")
    growth_trend: str = Field(description="Growth trend: growing, stable, declining")
    vehicle_coverage: str = Field(description="Vehicle coverage: full, partial")


class DashboardStatsResponse(BaseModel):
    """Response schema for main dashboard statistics."""

    model_config = ConfigDict(from_attributes=True)

    # Totals
    total_users: int = Field(ge=0)
    total_vehicles: int = Field(ge=0)
    total_couriers: int = Field(ge=0)
    total_assignments: int = Field(ge=0)

    # Courier status counts
    active_couriers: int = Field(ge=0)
    inactive_couriers: int = Field(ge=0)
    on_leave_couriers: int = Field(ge=0)
    onboarding_couriers: int = Field(ge=0)
    suspended_couriers: int = Field(ge=0)

    # Vehicle status counts
    vehicles_available: int = Field(ge=0)
    vehicles_assigned: int = Field(ge=0)
    vehicles_maintenance: int = Field(ge=0)
    vehicles_out_of_service: int = Field(ge=0)

    # Trends
    new_couriers_this_week: int = Field(ge=0)
    new_couriers_this_month: int = Field(ge=0)
    new_assignments_this_week: int = Field(ge=0)
    courier_growth_rate: float

    # Utilization
    courier_utilization: float = Field(ge=0, le=100)
    vehicle_utilization: float = Field(ge=0, le=100)
    couriers_with_vehicle: int = Field(ge=0)

    # Breakdowns
    sponsorship_breakdown: SponsorshipBreakdown
    project_breakdown: ProjectBreakdown

    # Insights
    insights: DashboardInsights


# ============================================================================
# Chart Data
# ============================================================================


class ChartDataPoint(BaseModel):
    """Generic chart data point."""

    name: str
    value: int = Field(ge=0)
    color: Optional[str] = None


class DeliveryTrendPoint(BaseModel):
    """Delivery trend data point."""

    date: str
    day: str
    deliveries: int = Field(ge=0)
    completed: int = Field(ge=0)
    failed: int = Field(ge=0)


class MonthlyTrendPoint(BaseModel):
    """Monthly trend data point."""

    month: str
    new_couriers: int = Field(ge=0)
    terminated: int = Field(ge=0)
    net_change: int


class FleetStatusResponse(BaseModel):
    """Response for fleet status chart."""

    fleet_status: List[ChartDataPoint]


class CourierStatusChartResponse(BaseModel):
    """Response for courier status chart."""

    courier_status: List[ChartDataPoint]


class SponsorshipDistributionResponse(BaseModel):
    """Response for sponsorship distribution chart."""

    sponsorship_distribution: List[ChartDataPoint]


class ProjectDistributionResponse(BaseModel):
    """Response for project type distribution chart."""

    project_distribution: List[ChartDataPoint]


class CityDistributionResponse(BaseModel):
    """Response for city distribution chart."""

    city_distribution: List[ChartDataPoint]


class DeliveryTrendsResponse(BaseModel):
    """Response for delivery trends chart."""

    trend_data: List[DeliveryTrendPoint]


class MonthlyTrendsResponse(BaseModel):
    """Response for monthly trends chart."""

    monthly_trends: List[MonthlyTrendPoint]


# ============================================================================
# Alerts
# ============================================================================


class DashboardAlert(BaseModel):
    """Dashboard alert item."""

    type: str = Field(description="Alert type: critical, warning, info")
    category: str = Field(description="Alert category: documents, fleet, etc.")
    title: str
    message: str
    count: int = Field(ge=0)
    action: str


class AlertSummary(BaseModel):
    """Alert counts by type."""

    critical: int = Field(ge=0)
    warning: int = Field(ge=0)
    info: int = Field(ge=0)


class DashboardAlertsResponse(BaseModel):
    """Response for dashboard alerts."""

    alerts: List[DashboardAlert]
    summary: AlertSummary


# ============================================================================
# Top Performers
# ============================================================================


class TopCourierItem(BaseModel):
    """Top courier item for performance ranking."""

    rank: int = Field(ge=1)
    id: int
    barq_id: str
    name: str
    performance_score: float = Field(ge=0)  # Removed upper bound for BigQuery real data
    total_deliveries: int = Field(ge=0)
    city: Optional[str] = None
    project_type: Optional[str] = None
    # BigQuery-specific fields (optional for backward compatibility)
    total_revenue: Optional[float] = None
    vehicle: Optional[str] = None
    plate: Optional[str] = None


class TopCouriersResponse(BaseModel):
    """Response for top couriers endpoint."""

    top_couriers: List[TopCourierItem]


# ============================================================================
# Recent Activity
# ============================================================================


class ActivityItem(BaseModel):
    """Recent activity item."""

    type: str
    title: str
    description: str
    timestamp: Optional[str] = None
    icon: str
    color: str


class RecentActivityResponse(BaseModel):
    """Response for recent activity endpoint."""

    activities: List[ActivityItem]


# ============================================================================
# Health Score
# ============================================================================


class HealthScoreBreakdown(BaseModel):
    """Individual health score component."""

    name: str
    score: float = Field(ge=0, le=100)
    weight: str


class FleetHealthScore(BaseModel):
    """Fleet health score response."""

    overall_score: float = Field(ge=0, le=100)
    status: str = Field(description="Status: excellent, good, fair, needs_attention")
    color: str
    breakdown: List[HealthScoreBreakdown]


# ============================================================================
# Executive Summary
# ============================================================================


class SummaryMetrics(BaseModel):
    """Summary metrics for executive dashboard."""

    total_couriers: int = Field(ge=0)
    active_couriers: int = Field(ge=0)
    active_rate: float = Field(ge=0, le=100)
    total_vehicles: int = Field(ge=0)
    avg_performance_score: float = Field(ge=0, le=100)
    avg_deliveries_per_courier: float = Field(ge=0)


class SummaryTrends(BaseModel):
    """Trend data for executive summary."""

    new_couriers_this_week: int = Field(ge=0)
    courier_change: int
    courier_change_pct: float
    trend_direction: str = Field(description="Trend direction: up, down, stable")


class ExecutiveSummaryResponse(BaseModel):
    """Response for executive summary endpoint."""

    summary: SummaryMetrics
    trends: SummaryTrends
    health_score: FleetHealthScore


# ============================================================================
# Aggregated Analytics
# ============================================================================


class FleetOverviewResponse(BaseModel):
    """Aggregated fleet overview with all key metrics."""

    model_config = ConfigDict(from_attributes=True)

    # Vehicles
    total_vehicles: int = Field(ge=0)
    vehicle_status: VehicleStatusBreakdown
    vehicle_utilization: float = Field(ge=0, le=100)

    # Couriers
    total_couriers: int = Field(ge=0)
    courier_status: CourierStatusBreakdown
    courier_utilization: float = Field(ge=0, le=100)

    # Coverage
    couriers_with_vehicles: int = Field(ge=0)
    unassigned_couriers: int = Field(ge=0)
    available_vehicles: int = Field(ge=0)

    # Health
    health_score: FleetHealthScore

    # Timestamp
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class OperationsOverviewResponse(BaseModel):
    """Operations overview with delivery and performance metrics."""

    model_config = ConfigDict(from_attributes=True)

    # Deliveries
    total_deliveries_today: int = Field(ge=0)
    completed_deliveries: int = Field(ge=0)
    failed_deliveries: int = Field(ge=0)
    pending_deliveries: int = Field(ge=0)

    # Rates
    success_rate: float = Field(ge=0, le=100)
    on_time_rate: float = Field(ge=0, le=100)

    # Trends
    delivery_trend: List[DeliveryTrendPoint]

    # Timestamp
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# KPI Dashboard
# ============================================================================


class KPIMetric(BaseModel):
    """Single KPI metric with trend information."""

    name: str
    value: float
    unit: Optional[str] = None
    target: Optional[float] = None
    change_pct: Optional[float] = None
    trend: Optional[str] = Field(None, description="up, down, stable")
    status: Optional[str] = Field(None, description="on_track, at_risk, off_track")


class KPIDashboardResponse(BaseModel):
    """Response for KPI dashboard with multiple metrics."""

    metrics: List[KPIMetric]
    period: str = Field(description="Time period for the KPIs")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
