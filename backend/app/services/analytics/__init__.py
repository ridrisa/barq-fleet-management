"""Analytics services"""

from app.services.analytics.performance_service import performance_service, PerformanceService
from app.services.analytics.fleet_analytics_service import fleet_analytics_service, FleetAnalyticsService
from app.services.analytics.hr_analytics_service import hr_analytics_service, HRAnalyticsService

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
