"""
Optimized Dashboard Service with Caching and N+1 Query Prevention

This service provides performance-optimized dashboard data:
- Multi-layer caching (memory + Redis)
- Minimized database queries
- Batch query optimization
- Query result caching

Performance targets:
- API response time: < 200ms (p95)
- Cache hit rate: > 80%
- Database queries per request: < 5
"""

from datetime import datetime, timedelta, date
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, case, func, or_
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.cache import cache_manager, cached
from app.models.fleet.assignment import CourierVehicleAssignment
from app.models.fleet.courier import Courier, CourierStatus, ProjectType, SponsorshipStatus
from app.models.fleet.vehicle import Vehicle, VehicleStatus

# Try importing optional models
try:
    from app.models.operations.delivery import Delivery, DeliveryStatus

    HAS_DELIVERY = True
except ImportError:
    HAS_DELIVERY = False


class DashboardPerformanceService:
    """Optimized dashboard service with caching"""

    # Cache TTLs
    STATS_CACHE_TTL = 300  # 5 minutes for stats
    CHARTS_CACHE_TTL = 600  # 10 minutes for charts
    ALERTS_CACHE_TTL = 180  # 3 minutes for alerts

    @staticmethod
    def _make_cache_key(org_id: int, key_suffix: str) -> str:
        """Create organization-scoped cache key"""
        return f"org_{org_id}:{key_suffix}"

    def get_dashboard_stats(self, db: Session, org_id: int) -> Dict[str, Any]:
        """
        Get comprehensive dashboard statistics with caching.

        Optimizations:
        - Cached for 5 minutes
        - Single query per metric type
        - Aggregated counts in database
        """
        cache_key = self._make_cache_key(org_id, "dashboard_stats")

        # Try cache first
        cached_stats = cache_manager.get("dashboard", cache_key)
        if cached_stats:
            return cached_stats

        # Calculate stats
        stats = self._calculate_dashboard_stats(db, org_id)

        # Cache results
        cache_manager.set("dashboard", cache_key, stats, self.STATS_CACHE_TTL)

        return stats

    def _calculate_dashboard_stats(self, db: Session, org_id: int) -> Dict[str, Any]:
        """Calculate dashboard statistics (called when cache misses)"""

        # OPTIMIZATION: Single query with aggregations instead of multiple count queries
        courier_stats = (
            db.query(
                func.count(Courier.id).label("total"),
                func.sum(
                    case((Courier.status == CourierStatus.ACTIVE, 1), else_=0)
                ).label("active"),
                func.sum(
                    case((Courier.status == CourierStatus.INACTIVE, 1), else_=0)
                ).label("inactive"),
                func.sum(
                    case((Courier.status == CourierStatus.ON_LEAVE, 1), else_=0)
                ).label("on_leave"),
                func.sum(
                    case((Courier.status == CourierStatus.ONBOARDING, 1), else_=0)
                ).label("onboarding"),
                func.sum(
                    case((Courier.status == CourierStatus.SUSPENDED, 1), else_=0)
                ).label("suspended"),
                func.sum(
                    case((Courier.current_vehicle_id.isnot(None), 1), else_=0)
                ).label("with_vehicle"),
                # Sponsorship breakdown
                func.sum(
                    case((Courier.sponsorship_status == SponsorshipStatus.AJEER, 1), else_=0)
                ).label("ajeer"),
                func.sum(
                    case((Courier.sponsorship_status == SponsorshipStatus.INHOUSE, 1), else_=0)
                ).label("inhouse"),
                func.sum(
                    case((Courier.sponsorship_status == SponsorshipStatus.FREELANCER, 1), else_=0)
                ).label("freelancer"),
                # Project breakdown
                func.sum(
                    case((Courier.project_type == ProjectType.ECOMMERCE, 1), else_=0)
                ).label("ecommerce"),
                func.sum(case((Courier.project_type == ProjectType.FOOD, 1), else_=0)).label(
                    "food"
                ),
                func.sum(
                    case((Courier.project_type == ProjectType.WAREHOUSE, 1), else_=0)
                ).label("warehouse"),
                func.sum(case((Courier.project_type == ProjectType.BARQ, 1), else_=0)).label(
                    "barq"
                ),
            )
            .filter(Courier.organization_id == org_id)
            .one()
        )

        # Vehicle stats - single query with aggregations
        # Using VehicleStatus enum: ACTIVE, MAINTENANCE, INACTIVE, RETIRED, REPAIR
        vehicle_stats = (
            db.query(
                func.count(Vehicle.id).label("total"),
                func.sum(case((Vehicle.status == VehicleStatus.ACTIVE, 1), else_=0)).label("active"),
                func.sum(case((Vehicle.status == VehicleStatus.MAINTENANCE, 1), else_=0)).label("maintenance"),
                func.sum(case((Vehicle.status.in_([VehicleStatus.INACTIVE, VehicleStatus.RETIRED, VehicleStatus.REPAIR]), 1), else_=0)).label(
                    "out_of_service"
                ),
            )
            .filter(Vehicle.organization_id == org_id)
            .one()
        )

        # Assignment count
        total_assignments = (
            db.query(func.count(CourierVehicleAssignment.id))
            .filter(CourierVehicleAssignment.organization_id == org_id)
            .scalar()
        )

        # Recent activity - single query
        week_ago = datetime.utcnow() - timedelta(days=7)
        month_ago = datetime.utcnow() - timedelta(days=30)

        new_couriers_this_week = (
            db.query(func.count(Courier.id))
            .filter(Courier.organization_id == org_id, Courier.created_at >= week_ago)
            .scalar()
        )

        new_couriers_this_month = (
            db.query(func.count(Courier.id))
            .filter(Courier.organization_id == org_id, Courier.created_at >= month_ago)
            .scalar()
        )

        new_assignments_this_week = (
            db.query(func.count(CourierVehicleAssignment.id))
            .filter(
                CourierVehicleAssignment.organization_id == org_id,
                CourierVehicleAssignment.created_at >= week_ago,
            )
            .scalar()
        )

        # Calculate metrics
        total_couriers = courier_stats.total or 0
        active_couriers = courier_stats.active or 0
        total_vehicles = vehicle_stats.total or 0
        # Active vehicles count (we don't have a separate "assigned" status in the enum)
        vehicles_active = vehicle_stats.active or 0
        # Available = active vehicles that aren't assigned to any courier
        # For simplicity, we'll need to query assigned vehicles separately
        vehicles_with_assigned_couriers = (
            db.query(func.count(Vehicle.id))
            .filter(
                Vehicle.organization_id == org_id,
                Vehicle.status == VehicleStatus.ACTIVE,
                Vehicle.assigned_couriers.any()
            )
            .scalar() or 0
        )
        vehicles_available = vehicles_active - vehicles_with_assigned_couriers
        vehicles_assigned = vehicles_with_assigned_couriers

        courier_utilization = (
            round((active_couriers / total_couriers * 100), 1) if total_couriers > 0 else 0
        )
        vehicle_utilization = (
            round((vehicles_assigned / total_vehicles * 100), 1) if total_vehicles > 0 else 0
        )

        # Growth rate calculation
        two_weeks_ago = datetime.utcnow() - timedelta(days=14)
        couriers_two_weeks = (
            db.query(func.count(Courier.id))
            .filter(
                Courier.organization_id == org_id,
                and_(Courier.created_at >= two_weeks_ago, Courier.created_at < week_ago),
            )
            .scalar()
        )

        growth_rate = 0
        if couriers_two_weeks and couriers_two_weeks > 0:
            growth_rate = round(
                ((new_couriers_this_week - couriers_two_weeks) / couriers_two_weeks) * 100, 1
            )
        elif new_couriers_this_week > 0:
            growth_rate = 100

        return {
            "total_users": 0,  # Placeholder
            "total_vehicles": total_vehicles,
            "total_couriers": total_couriers,
            "total_assignments": total_assignments or 0,
            # Courier status
            "active_couriers": active_couriers,
            "inactive_couriers": courier_stats.inactive or 0,
            "on_leave_couriers": courier_stats.on_leave or 0,
            "onboarding_couriers": courier_stats.onboarding or 0,
            "suspended_couriers": courier_stats.suspended or 0,
            # Vehicle status
            "vehicles_available": vehicles_available,
            "vehicles_assigned": vehicles_assigned,
            "vehicles_maintenance": vehicle_stats.maintenance or 0,
            "vehicles_out_of_service": vehicle_stats.out_of_service or 0,
            # Trends
            "new_couriers_this_week": new_couriers_this_week or 0,
            "new_couriers_this_month": new_couriers_this_month or 0,
            "new_assignments_this_week": new_assignments_this_week or 0,
            "courier_growth_rate": growth_rate,
            # Utilization
            "courier_utilization": courier_utilization,
            "vehicle_utilization": vehicle_utilization,
            "couriers_with_vehicle": courier_stats.with_vehicle or 0,
            # Sponsorship breakdown
            "sponsorship_breakdown": {
                "ajeer": courier_stats.ajeer or 0,
                "inhouse": courier_stats.inhouse or 0,
                "freelancer": courier_stats.freelancer or 0,
            },
            # Project breakdown
            "project_breakdown": {
                "ecommerce": courier_stats.ecommerce or 0,
                "food": courier_stats.food or 0,
                "warehouse": courier_stats.warehouse or 0,
                "barq": courier_stats.barq or 0,
            },
            # Summary insights
            "insights": {
                "fleet_health": "good" if vehicle_utilization > 50 else "needs_attention",
                "courier_availability": (
                    "high"
                    if active_couriers > total_couriers * 0.7
                    else "moderate" if active_couriers > total_couriers * 0.4 else "low"
                ),
                "growth_trend": (
                    "growing" if growth_rate > 0 else "stable" if growth_rate == 0 else "declining"
                ),
                "vehicle_coverage": (
                    "full" if courier_stats.with_vehicle >= active_couriers else "partial"
                ),
            },
        }

    def get_top_couriers(
        self, db: Session, org_id: int, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get top performing couriers with caching.

        Optimizations:
        - Cached for 10 minutes
        - Single query with ordering
        - No N+1 queries
        """
        cache_key = self._make_cache_key(org_id, f"top_couriers_{limit}")

        # Try cache
        cached_result = cache_manager.get("dashboard", cache_key)
        if cached_result:
            return cached_result

        # Single query with proper ordering
        top_couriers = (
            db.query(Courier)
            .filter(Courier.organization_id == org_id, Courier.status == CourierStatus.ACTIVE)
            .order_by(
                Courier.performance_score.desc().nullslast(),
                Courier.total_deliveries.desc().nullslast(),
            )
            .limit(limit)
            .all()
        )

        result = []
        for i, courier in enumerate(top_couriers):
            result.append(
                {
                    "rank": i + 1,
                    "id": courier.id,
                    "barq_id": courier.barq_id,
                    "name": courier.full_name,
                    "performance_score": float(courier.performance_score or 0),
                    "total_deliveries": courier.total_deliveries or 0,
                    "city": courier.city,
                    "project_type": courier.project_type.value if courier.project_type else None,
                }
            )

        # Cache for 10 minutes
        cache_manager.set("dashboard", cache_key, result, self.CHARTS_CACHE_TTL)

        return result

    def invalidate_dashboard_cache(self, org_id: int):
        """
        Invalidate all dashboard-related cache for an organization.

        Call this when data changes that affect dashboard stats.
        """
        # Invalidate all dashboard cache entries for this organization
        cache_manager.delete_pattern("dashboard", f"org_{org_id}:*")


# Global service instance
dashboard_service = DashboardPerformanceService()
