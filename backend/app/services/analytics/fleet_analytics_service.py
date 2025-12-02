"""Fleet Analytics Service

Provides analytics and insights for fleet operations:
- Vehicle utilization rates
- Maintenance costs analysis
- Fuel consumption trends
- Courier performance metrics
- Vehicle assignment patterns
"""
from typing import Dict, List, Optional, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case, extract

from app.models.fleet.vehicle import Vehicle, VehicleStatus
from app.models.fleet.courier import Courier, CourierStatus
from app.models.fleet.assignment import CourierVehicleAssignment as Assignment
from app.models.fleet.maintenance import VehicleMaintenance as Maintenance
from app.models.operations.delivery import Delivery, DeliveryStatus


class FleetAnalyticsService:
    """
    Service for fleet analytics and reporting

    Provides insights into:
    - Vehicle utilization
    - Maintenance costs and patterns
    - Courier performance
    - Assignment efficiency
    """

    def get_vehicle_utilization(
        self,
        db: Session,
        start_date: date,
        end_date: date,
        vehicle_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calculate vehicle utilization rate

        Utilization = (Days with assignments / Total days) * 100

        Args:
            db: Database session
            start_date: Start date for analysis
            end_date: End date for analysis
            vehicle_id: Optional specific vehicle ID

        Returns:
            Dictionary with utilization metrics
        """
        total_days = (end_date - start_date).days + 1

        # Query assignments
        query = db.query(Assignment)
        query = query.filter(
            and_(
                Assignment.start_date <= end_date,
                or_(
                    Assignment.end_date >= start_date,
                    Assignment.end_date.is_(None)
                )
            )
        )

        if vehicle_id:
            query = query.filter(Assignment.vehicle_id == vehicle_id)

        assignments = query.all()

        if vehicle_id:
            # Single vehicle analysis
            assigned_days = set()
            for assignment in assignments:
                end = assignment.end_date or end_date
                current = max(start_date, assignment.start_date)
                while current <= min(end, end_date):
                    assigned_days.add(current)
                    current += timedelta(days=1)

            utilization_rate = (len(assigned_days) / total_days) * 100

            return {
                "vehicle_id": vehicle_id,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "total_days": total_days
                },
                "assigned_days": len(assigned_days),
                "idle_days": total_days - len(assigned_days),
                "utilization_rate": round(utilization_rate, 2),
                "total_assignments": len(assignments)
            }

        else:
            # Fleet-wide analysis
            total_vehicles = db.query(func.count(Vehicle.id)).scalar()
            vehicle_utilization = {}

            for vehicle in db.query(Vehicle).all():
                vehicle_assignments = [a for a in assignments if a.vehicle_id == vehicle.id]
                assigned_days = set()

                for assignment in vehicle_assignments:
                    end = assignment.end_date or end_date
                    current = max(start_date, assignment.start_date)
                    while current <= min(end, end_date):
                        assigned_days.add(current)
                        current += timedelta(days=1)

                utilization = (len(assigned_days) / total_days) * 100
                vehicle_utilization[vehicle.id] = {
                    "vehicle_id": vehicle.id,
                    "license_plate": vehicle.license_plate,
                    "assigned_days": len(assigned_days),
                    "utilization_rate": round(utilization, 2)
                }

            avg_utilization = sum(v["utilization_rate"] for v in vehicle_utilization.values()) / total_vehicles if total_vehicles > 0 else 0

            return {
                "fleet_summary": {
                    "total_vehicles": total_vehicles,
                    "period": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "total_days": total_days
                    },
                    "average_utilization_rate": round(avg_utilization, 2)
                },
                "vehicles": list(vehicle_utilization.values())
            }

    def get_maintenance_costs(
        self,
        db: Session,
        start_date: date,
        end_date: date,
        vehicle_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyze maintenance costs

        Args:
            db: Database session
            start_date: Start date for analysis
            end_date: End date for analysis
            vehicle_id: Optional specific vehicle ID

        Returns:
            Dictionary with maintenance cost analysis
        """
        query = db.query(Maintenance).filter(
            and_(
                Maintenance.maintenance_date >= start_date,
                Maintenance.maintenance_date <= end_date
            )
        )

        if vehicle_id:
            query = query.filter(Maintenance.vehicle_id == vehicle_id)

        maintenances = query.all()

        total_cost = sum(m.cost for m in maintenances if m.cost)
        avg_cost = total_cost / len(maintenances) if maintenances else 0

        # Group by type
        cost_by_type = {}
        for maintenance in maintenances:
            m_type = maintenance.maintenance_type or "unknown"
            if m_type not in cost_by_type:
                cost_by_type[m_type] = {"count": 0, "total_cost": Decimal("0")}

            cost_by_type[m_type]["count"] += 1
            if maintenance.cost:
                cost_by_type[m_type]["total_cost"] += maintenance.cost

        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "vehicle_id": vehicle_id,
            "summary": {
                "total_maintenances": len(maintenances),
                "total_cost": float(total_cost),
                "average_cost": float(avg_cost)
            },
            "by_type": {
                k: {
                    "count": v["count"],
                    "total_cost": float(v["total_cost"]),
                    "average_cost": float(v["total_cost"] / v["count"]) if v["count"] > 0 else 0
                }
                for k, v in cost_by_type.items()
            }
        }

    def get_courier_performance(
        self,
        db: Session,
        start_date: date,
        end_date: date,
        courier_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyze courier performance based on deliveries

        Args:
            db: Database session
            start_date: Start date for analysis
            end_date: End date for analysis
            courier_id: Optional specific courier ID

        Returns:
            Dictionary with courier performance metrics
        """
        query = db.query(Delivery).filter(
            and_(
                Delivery.created_at >= datetime.combine(start_date, datetime.min.time()),
                Delivery.created_at <= datetime.combine(end_date, datetime.max.time())
            )
        )

        if courier_id:
            # Get courier's vehicle assignments
            assignments = (
                db.query(Assignment)
                .filter(Assignment.courier_id == courier_id)
                .all()
            )
            vehicle_ids = [a.vehicle_id for a in assignments]

            if vehicle_ids:
                query = query.filter(Delivery.vehicle_id.in_(vehicle_ids))

        deliveries = query.all()

        # Calculate metrics
        total_deliveries = len(deliveries)
        completed = sum(1 for d in deliveries if d.status == DeliveryStatus.DELIVERED)
        failed = sum(1 for d in deliveries if d.status == DeliveryStatus.FAILED)
        pending = sum(1 for d in deliveries if d.status == DeliveryStatus.PENDING)
        in_transit = sum(1 for d in deliveries if d.status == DeliveryStatus.IN_TRANSIT)

        success_rate = (completed / total_deliveries * 100) if total_deliveries > 0 else 0

        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "courier_id": courier_id,
            "summary": {
                "total_deliveries": total_deliveries,
                "completed": completed,
                "failed": failed,
                "pending": pending,
                "in_transit": in_transit,
                "success_rate": round(success_rate, 2)
            }
        }

    def get_fleet_status_summary(
        self,
        db: Session
    ) -> Dict[str, Any]:
        """
        Get current fleet status summary

        Args:
            db: Database session

        Returns:
            Dictionary with fleet status overview
        """
        # Vehicles by status
        vehicle_stats = (
            db.query(
                Vehicle.status,
                func.count(Vehicle.id)
            )
            .group_by(Vehicle.status)
            .all()
        )

        vehicles_by_status = {}
        total_vehicles = 0
        for status, count in vehicle_stats:
            vehicles_by_status[status.value] = count
            total_vehicles += count

        # Couriers by status
        courier_stats = (
            db.query(
                Courier.status,
                func.count(Courier.id)
            )
            .group_by(Courier.status)
            .all()
        )

        couriers_by_status = {}
        total_couriers = 0
        for status, count in courier_stats:
            couriers_by_status[status.value] = count
            total_couriers += count

        # Active assignments
        active_assignments = (
            db.query(func.count(Assignment.id))
            .filter(
                or_(
                    Assignment.end_date.is_(None),
                    Assignment.end_date >= date.today()
                )
            )
            .scalar()
        )

        return {
            "vehicles": {
                "total": total_vehicles,
                "by_status": vehicles_by_status
            },
            "couriers": {
                "total": total_couriers,
                "by_status": couriers_by_status
            },
            "assignments": {
                "active": active_assignments
            },
            "timestamp": datetime.utcnow().isoformat()
        }


# Singleton instance
fleet_analytics_service = FleetAnalyticsService()
