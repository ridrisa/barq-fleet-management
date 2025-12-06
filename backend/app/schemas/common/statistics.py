"""
Common statistics and analytics schemas used across the application.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class BaseStatistics(BaseModel):
    """
    Base statistics schema with common metrics.
    Extend for domain-specific statistics (vehicles, couriers, tickets, etc.)
    """

    total: int = 0
    active: int = 0
    inactive: int = 0


class CountByStatusResponse(BaseModel):
    """Generic count-by-status response."""

    status: str
    count: int
    percentage: float = 0.0


class TrendDataPoint(BaseModel):
    """Single data point for trend charts."""

    date: date
    value: float
    label: Optional[str] = None


class TrendResponse(BaseModel):
    """Response containing trend data for charts."""

    data: List[TrendDataPoint]
    total: float = 0.0
    average: float = 0.0
    min_value: float = 0.0
    max_value: float = 0.0
    change_percent: Optional[float] = None


class SummaryStatistics(BaseModel):
    """Summary statistics with common KPIs."""

    period_start: date
    period_end: date
    total_count: int = 0
    new_count: int = 0
    completed_count: int = 0
    pending_count: int = 0
    growth_rate: float = 0.0
    completion_rate: float = 0.0


class VehicleStatisticsResponse(BaseStatistics):
    """Statistics response for vehicles."""

    in_maintenance: int = 0
    out_of_service: int = 0
    total_mileage: Decimal = Decimal("0")
    avg_mileage: Decimal = Decimal("0")
    service_due: int = 0
    documents_expiring: int = 0


class CourierStatisticsResponse(BaseStatistics):
    """Statistics response for couriers."""

    onboarding: int = 0
    suspended: int = 0
    terminated: int = 0
    total_deliveries: int = 0
    avg_performance_score: Decimal = Decimal("0")
    documents_expiring: int = 0


class TicketStatisticsResponse(BaseStatistics):
    """Statistics response for support tickets."""

    open: int = 0
    in_progress: int = 0
    waiting: int = 0
    resolved: int = 0
    closed: int = 0
    escalated: int = 0
    avg_resolution_time_hours: float = 0.0
    sla_compliance_rate: float = 0.0


class FinancialStatisticsResponse(BaseModel):
    """Statistics response for financial data."""

    total_revenue: Decimal = Decimal("0")
    total_expenses: Decimal = Decimal("0")
    net_profit: Decimal = Decimal("0")
    profit_margin: float = 0.0
    pending_payments: Decimal = Decimal("0")
    overdue_payments: Decimal = Decimal("0")
