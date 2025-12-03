"""Analytics services"""

from app.services.analytics.fleet_analytics_service import (
    FleetAnalyticsService,
    fleet_analytics_service,
)
from app.services.analytics.hr_analytics_service import HRAnalyticsService, hr_analytics_service
from app.services.analytics.performance_service import PerformanceService, performance_service

__all__ = [
    # Service instances (ready to use)
    "performance_service",
    "fleet_analytics_service",
    "hr_analytics_service",
    # Service classes (for customization if needed)
    "PerformanceService",
    "FleetAnalyticsService",
    "HRAnalyticsService",
]
