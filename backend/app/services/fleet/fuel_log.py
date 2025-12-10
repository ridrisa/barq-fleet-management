from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.fleet.fuel_log import FuelLog
from app.schemas.fleet.fuel_log import FuelLogCreate, FuelLogSummary, FuelLogUpdate
from app.services.base import CRUDBase


class FuelLogService(CRUDBase[FuelLog, FuelLogCreate, FuelLogUpdate]):
    """Service for FuelLog operations with business logic"""

    def get_by_vehicle(
        self,
        db: Session,
        vehicle_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
    ) -> List[FuelLog]:
        """Get all fuel logs for a specific vehicle"""
        query = db.query(FuelLog).filter(FuelLog.vehicle_id == vehicle_id)

        if organization_id:
            query = query.filter(FuelLog.organization_id == organization_id)

        return query.order_by(FuelLog.fuel_date.desc()).offset(skip).limit(limit).all()

    def get_by_courier(
        self,
        db: Session,
        courier_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
    ) -> List[FuelLog]:
        """Get all fuel logs recorded by a specific courier"""
        query = db.query(FuelLog).filter(FuelLog.courier_id == courier_id)

        if organization_id:
            query = query.filter(FuelLog.organization_id == organization_id)

        return query.order_by(FuelLog.fuel_date.desc()).offset(skip).limit(limit).all()

    def get_by_date_range(
        self,
        db: Session,
        *,
        start_date: date,
        end_date: date,
        vehicle_id: Optional[int] = None,
        courier_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
    ) -> List[FuelLog]:
        """Get fuel logs within a date range"""
        query = db.query(FuelLog).filter(
            and_(
                FuelLog.fuel_date >= start_date,
                FuelLog.fuel_date <= end_date,
            )
        )

        if vehicle_id:
            query = query.filter(FuelLog.vehicle_id == vehicle_id)

        if courier_id:
            query = query.filter(FuelLog.courier_id == courier_id)

        if organization_id:
            query = query.filter(FuelLog.organization_id == organization_id)

        return query.order_by(FuelLog.fuel_date.desc()).offset(skip).limit(limit).all()

    def get_summary(
        self,
        db: Session,
        *,
        vehicle_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        organization_id: Optional[int] = None,
    ) -> FuelLogSummary:
        """
        Get fuel consumption summary with aggregated statistics.
        Can be filtered by vehicle and/or date range.
        """
        query = db.query(FuelLog)

        if vehicle_id:
            query = query.filter(FuelLog.vehicle_id == vehicle_id)

        if start_date:
            query = query.filter(FuelLog.fuel_date >= start_date)

        if end_date:
            query = query.filter(FuelLog.fuel_date <= end_date)

        if organization_id:
            query = query.filter(FuelLog.organization_id == organization_id)

        # Get aggregated values
        result = query.with_entities(
            func.sum(FuelLog.fuel_quantity).label("total_fuel_quantity"),
            func.sum(FuelLog.fuel_cost).label("total_fuel_cost"),
            func.avg(FuelLog.cost_per_liter).label("average_cost_per_liter"),
            func.count(FuelLog.id).label("log_count"),
        ).first()

        # Calculate total distance (difference between max and min odometer readings)
        odometer_result = query.with_entities(
            func.max(FuelLog.odometer_reading).label("max_odometer"),
            func.min(FuelLog.odometer_reading).label("min_odometer"),
        ).first()

        total_distance = Decimal("0.0")
        if odometer_result.max_odometer and odometer_result.min_odometer:
            total_distance = Decimal(str(odometer_result.max_odometer)) - Decimal(
                str(odometer_result.min_odometer)
            )

        total_fuel_quantity = Decimal(str(result.total_fuel_quantity or 0))
        average_consumption = Decimal("0.0")
        if total_fuel_quantity > 0 and total_distance > 0:
            average_consumption = total_distance / total_fuel_quantity

        return FuelLogSummary(
            total_fuel_quantity=total_fuel_quantity,
            total_fuel_cost=Decimal(str(result.total_fuel_cost or 0)),
            average_cost_per_liter=Decimal(str(result.average_cost_per_liter or 0)),
            total_distance=total_distance,
            average_consumption=average_consumption,
            log_count=result.log_count or 0,
        )

    def get_vehicle_summary(
        self,
        db: Session,
        vehicle_id: int,
        *,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        organization_id: Optional[int] = None,
    ) -> FuelLogSummary:
        """Get fuel consumption summary for a specific vehicle"""
        return self.get_summary(
            db,
            vehicle_id=vehicle_id,
            start_date=start_date,
            end_date=end_date,
            organization_id=organization_id,
        )

    def get_monthly_statistics(
        self,
        db: Session,
        *,
        year: int,
        month: int,
        vehicle_id: Optional[int] = None,
        organization_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get monthly fuel statistics"""
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

        summary = self.get_summary(
            db,
            vehicle_id=vehicle_id,
            start_date=start_date,
            end_date=end_date,
            organization_id=organization_id,
        )

        return {
            "year": year,
            "month": month,
            "summary": summary,
        }

    def get_recent_logs(
        self,
        db: Session,
        *,
        days: int = 7,
        vehicle_id: Optional[int] = None,
        organization_id: Optional[int] = None,
    ) -> List[FuelLog]:
        """Get fuel logs from the last N days"""
        cutoff_date = date.today() - timedelta(days=days)

        query = db.query(FuelLog).filter(FuelLog.fuel_date >= cutoff_date)

        if vehicle_id:
            query = query.filter(FuelLog.vehicle_id == vehicle_id)

        if organization_id:
            query = query.filter(FuelLog.organization_id == organization_id)

        return query.order_by(FuelLog.fuel_date.desc()).all()

    def get_statistics(
        self,
        db: Session,
        *,
        organization_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get overall fuel log statistics"""
        base_query = db.query(FuelLog)

        if organization_id:
            base_query = base_query.filter(FuelLog.organization_id == organization_id)

        total_logs = base_query.with_entities(func.count(FuelLog.id)).scalar()

        # Total fuel and cost
        totals = base_query.with_entities(
            func.sum(FuelLog.fuel_quantity).label("total_fuel"),
            func.sum(FuelLog.fuel_cost).label("total_cost"),
        ).first()

        # Logs by fuel type
        fuel_type_counts = (
            base_query.with_entities(FuelLog.fuel_type, func.count(FuelLog.id))
            .group_by(FuelLog.fuel_type)
            .all()
        )

        # Unique vehicles with logs
        unique_vehicles = base_query.with_entities(
            func.count(func.distinct(FuelLog.vehicle_id))
        ).scalar()

        return {
            "total_logs": total_logs,
            "total_fuel_quantity": float(totals.total_fuel or 0),
            "total_fuel_cost": float(totals.total_cost or 0),
            "fuel_type_breakdown": dict(fuel_type_counts),
            "unique_vehicles": unique_vehicles,
        }


# Create instance
fuel_log_service = FuelLogService(FuelLog)
