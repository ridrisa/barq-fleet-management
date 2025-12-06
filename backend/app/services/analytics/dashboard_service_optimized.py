"""Optimized Dashboard Service with Efficient Aggregation Queries"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy import and_, case, extract, func, or_
from sqlalchemy.orm import Session

from app.models.fleet.assignment import CourierVehicleAssignment
from app.models.fleet.courier import Courier, CourierStatus, ProjectType, SponsorshipStatus
from app.models.fleet.vehicle import Vehicle

# Optional imports for delivery tracking
try:
    from app.models.operations.delivery import Delivery, DeliveryStatus
    HAS_DELIVERY = True
except ImportError:
    HAS_DELIVERY = False


class DashboardServiceOptimized:
    """
    Optimized dashboard service that uses database-level aggregations
    instead of loading all records into memory
    """

    @staticmethod
    def get_fleet_statistics(
        db: Session,
        organization_id: int
    ) -> Dict:
        """
        Get comprehensive fleet statistics with a single optimized query

        Optimizations:
        - Uses database aggregation with CASE expressions
        - Single query instead of multiple COUNT queries
        - Uses indexed columns for filtering
        """
        # Get courier statistics in one query
        courier_stats = (
            db.query(
                func.count(Courier.id).label('total'),
                func.sum(case((Courier.status == CourierStatus.ACTIVE, 1), else_=0)).label('active'),
                func.sum(case((Courier.status == CourierStatus.INACTIVE, 1), else_=0)).label('inactive'),
                func.sum(case((Courier.status == CourierStatus.ON_LEAVE, 1), else_=0)).label('on_leave'),
                func.sum(case((Courier.status == CourierStatus.ONBOARDING, 1), else_=0)).label('onboarding'),
                func.sum(case((Courier.status == CourierStatus.SUSPENDED, 1), else_=0)).label('suspended'),
                func.sum(case((Courier.current_vehicle_id.isnot(None), 1), else_=0)).label('with_vehicle'),
                func.sum(case((Courier.sponsorship_status == SponsorshipStatus.AJEER, 1), else_=0)).label('ajeer'),
                func.sum(case((Courier.sponsorship_status == SponsorshipStatus.INHOUSE, 1), else_=0)).label('inhouse'),
                func.sum(case((Courier.sponsorship_status == SponsorshipStatus.FREELANCER, 1), else_=0)).label('freelancer'),
                func.sum(case((Courier.project_type == ProjectType.ECOMMERCE, 1), else_=0)).label('ecommerce'),
                func.sum(case((Courier.project_type == ProjectType.FOOD, 1), else_=0)).label('food'),
                func.sum(case((Courier.project_type == ProjectType.WAREHOUSE, 1), else_=0)).label('warehouse'),
                func.sum(case((Courier.project_type == ProjectType.BARQ, 1), else_=0)).label('barq'),
            )
            .filter(Courier.organization_id == organization_id)
            .one()
        )

        # Get vehicle statistics in one query
        vehicle_stats = (
            db.query(
                func.count(Vehicle.id).label('total'),
                func.sum(case((Vehicle.status == "available", 1), else_=0)).label('available'),
                func.sum(case((Vehicle.status == "assigned", 1), else_=0)).label('assigned'),
                func.sum(case((Vehicle.status == "maintenance", 1), else_=0)).label('maintenance'),
                func.sum(case((Vehicle.status == "out_of_service", 1), else_=0)).label('out_of_service'),
            )
            .filter(Vehicle.organization_id == organization_id)
            .one()
        )

        # Get assignment count
        total_assignments = (
            db.query(func.count(CourierVehicleAssignment.id))
            .filter(CourierVehicleAssignment.organization_id == organization_id)
            .scalar() or 0
        )

        total_couriers = courier_stats.total or 0
        active_couriers = courier_stats.active or 0
        total_vehicles = vehicle_stats.total or 0
        vehicles_assigned = vehicle_stats.assigned or 0

        return {
            # Overall counts
            "total_couriers": total_couriers,
            "total_vehicles": total_vehicles,
            "total_assignments": total_assignments,

            # Courier status breakdown
            "active_couriers": active_couriers,
            "inactive_couriers": courier_stats.inactive or 0,
            "on_leave_couriers": courier_stats.on_leave or 0,
            "onboarding_couriers": courier_stats.onboarding or 0,
            "suspended_couriers": courier_stats.suspended or 0,

            # Vehicle status breakdown
            "vehicles_available": vehicle_stats.available or 0,
            "vehicles_assigned": vehicles_assigned,
            "vehicles_maintenance": vehicle_stats.maintenance or 0,
            "vehicles_out_of_service": vehicle_stats.out_of_service or 0,

            # Utilization metrics
            "courier_utilization": round(
                (active_couriers / total_couriers * 100) if total_couriers > 0 else 0, 1
            ),
            "vehicle_utilization": round(
                (vehicles_assigned / total_vehicles * 100) if total_vehicles > 0 else 0, 1
            ),
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
        }

    @staticmethod
    def get_growth_metrics(
        db: Session,
        organization_id: int
    ) -> Dict:
        """
        Get growth metrics with optimized queries

        Optimizations:
        - Uses database filtering with date ranges
        - Single query per metric with COUNT
        - Uses indexed created_at column
        """
        week_ago = datetime.utcnow() - timedelta(days=7)
        month_ago = datetime.utcnow() - timedelta(days=30)
        two_weeks_ago = datetime.utcnow() - timedelta(days=14)

        # Get new couriers this week and month
        new_couriers_this_week = (
            db.query(func.count(Courier.id))
            .filter(
                Courier.organization_id == organization_id,
                Courier.created_at >= week_ago
            )
            .scalar() or 0
        )

        new_couriers_this_month = (
            db.query(func.count(Courier.id))
            .filter(
                Courier.organization_id == organization_id,
                Courier.created_at >= month_ago
            )
            .scalar() or 0
        )

        # Get new assignments this week
        new_assignments_this_week = (
            db.query(func.count(CourierVehicleAssignment.id))
            .filter(
                CourierVehicleAssignment.organization_id == organization_id,
                CourierVehicleAssignment.created_at >= week_ago
            )
            .scalar() or 0
        )

        # Calculate growth rate
        couriers_two_weeks = (
            db.query(func.count(Courier.id))
            .filter(
                Courier.organization_id == organization_id,
                and_(
                    Courier.created_at >= two_weeks_ago,
                    Courier.created_at < week_ago
                )
            )
            .scalar() or 0
        )

        growth_rate = 0
        if couriers_two_weeks > 0:
            growth_rate = round(
                ((new_couriers_this_week - couriers_two_weeks) / couriers_two_weeks) * 100, 1
            )
        elif new_couriers_this_week > 0:
            growth_rate = 100

        return {
            "new_couriers_this_week": new_couriers_this_week,
            "new_couriers_this_month": new_couriers_this_month,
            "new_assignments_this_week": new_assignments_this_week,
            "courier_growth_rate": growth_rate,
        }

    @staticmethod
    def get_expiry_alerts(
        db: Session,
        organization_id: int,
        warning_days: int = 30
    ) -> Dict:
        """
        Get document expiry alerts with optimized queries

        Optimizations:
        - Uses partial indexes on expiry date columns
        - Filters by organization and status
        - Efficient date range filtering
        """
        today = date.today()

        # Expiring and expired Iqamas
        expiring_iqamas = (
            db.query(func.count(Courier.id))
            .filter(
                Courier.organization_id == organization_id,
                and_(
                    Courier.iqama_expiry_date.isnot(None),
                    Courier.iqama_expiry_date <= today + timedelta(days=warning_days),
                    Courier.iqama_expiry_date > today,
                    Courier.status == CourierStatus.ACTIVE,
                )
            )
            .scalar() or 0
        )

        expired_iqamas = (
            db.query(func.count(Courier.id))
            .filter(
                Courier.organization_id == organization_id,
                and_(
                    Courier.iqama_expiry_date.isnot(None),
                    Courier.iqama_expiry_date <= today,
                    Courier.status == CourierStatus.ACTIVE,
                )
            )
            .scalar() or 0
        )

        # Expiring and expired licenses
        expiring_licenses = (
            db.query(func.count(Courier.id))
            .filter(
                Courier.organization_id == organization_id,
                and_(
                    Courier.license_expiry_date.isnot(None),
                    Courier.license_expiry_date <= today + timedelta(days=warning_days),
                    Courier.license_expiry_date > today,
                    Courier.status == CourierStatus.ACTIVE,
                )
            )
            .scalar() or 0
        )

        expired_licenses = (
            db.query(func.count(Courier.id))
            .filter(
                Courier.organization_id == organization_id,
                and_(
                    Courier.license_expiry_date.isnot(None),
                    Courier.license_expiry_date <= today,
                    Courier.status == CourierStatus.ACTIVE,
                )
            )
            .scalar() or 0
        )

        # Vehicles in maintenance
        vehicles_in_maintenance = (
            db.query(func.count(Vehicle.id))
            .filter(
                Vehicle.organization_id == organization_id,
                Vehicle.status == "maintenance"
            )
            .scalar() or 0
        )

        # Active couriers without vehicles
        active_without_vehicle = (
            db.query(func.count(Courier.id))
            .filter(
                Courier.organization_id == organization_id,
                and_(
                    Courier.status == CourierStatus.ACTIVE,
                    Courier.current_vehicle_id.is_(None)
                )
            )
            .scalar() or 0
        )

        return {
            "expired_iqamas": expired_iqamas,
            "expiring_iqamas": expiring_iqamas,
            "expired_licenses": expired_licenses,
            "expiring_licenses": expiring_licenses,
            "vehicles_in_maintenance": vehicles_in_maintenance,
            "active_without_vehicle": active_without_vehicle,
        }

    @staticmethod
    def get_city_distribution(
        db: Session,
        organization_id: int,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get courier distribution by city with optimized GROUP BY

        Optimizations:
        - Uses database GROUP BY aggregation
        - Limits results at database level
        - Uses indexed city column
        """
        city_counts = (
            db.query(
                Courier.city,
                func.count(Courier.id).label("count")
            )
            .filter(
                Courier.organization_id == organization_id,
                Courier.city.isnot(None)
            )
            .group_by(Courier.city)
            .order_by(func.count(Courier.id).desc())
            .limit(limit)
            .all()
        )

        return [
            {"city": city or "Unknown", "count": count}
            for city, count in city_counts
        ]

    @staticmethod
    def get_monthly_trends(
        db: Session,
        organization_id: int,
        months: int = 6
    ) -> List[Dict]:
        """
        Get monthly courier onboarding trends with optimized queries

        Optimizations:
        - Uses database date truncation and filtering
        - Aggregates at database level
        - Single loop with efficient queries
        """
        today = datetime.utcnow().date()
        trends = []

        for i in range(months - 1, -1, -1):
            # Calculate month boundaries
            month_date = today.replace(day=1) - timedelta(days=i * 30)
            month_start = month_date.replace(day=1)

            # Get next month start
            if month_start.month == 12:
                next_month = month_start.replace(year=month_start.year + 1, month=1)
            else:
                next_month = month_start.replace(month=month_start.month + 1)

            # Count new couriers
            new_couriers = (
                db.query(func.count(Courier.id))
                .filter(
                    Courier.organization_id == organization_id,
                    and_(
                        Courier.created_at >= month_start,
                        Courier.created_at < next_month
                    )
                )
                .scalar() or 0
            )

            # Count terminated couriers
            terminated = (
                db.query(func.count(Courier.id))
                .filter(
                    Courier.organization_id == organization_id,
                    and_(
                        Courier.status == CourierStatus.TERMINATED,
                        Courier.updated_at >= month_start,
                        Courier.updated_at < next_month
                    )
                )
                .scalar() or 0
            )

            trends.append({
                "month": month_start.strftime("%b %Y"),
                "new_couriers": new_couriers,
                "terminated": terminated,
                "net_change": new_couriers - terminated,
            })

        return trends

    @staticmethod
    def get_top_performers(
        db: Session,
        organization_id: int,
        limit: int = 5
    ) -> List[Dict]:
        """
        Get top performing couriers with optimized query

        Optimizations:
        - Uses indexed columns for sorting
        - Limits results at database level
        - Loads only required columns
        """
        top_couriers = (
            db.query(
                Courier.id,
                Courier.barq_id,
                Courier.full_name,
                Courier.performance_score,
                Courier.total_deliveries,
                Courier.city,
                Courier.project_type
            )
            .filter(
                Courier.organization_id == organization_id,
                Courier.status == CourierStatus.ACTIVE
            )
            .order_by(
                Courier.performance_score.desc().nullslast(),
                Courier.total_deliveries.desc().nullslast()
            )
            .limit(limit)
            .all()
        )

        return [
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
            for i, courier in enumerate(top_couriers)
        ]


# Create singleton instance
dashboard_service_optimized = DashboardServiceOptimized()
