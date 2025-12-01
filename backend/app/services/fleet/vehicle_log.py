from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date
from app.models.fleet import VehicleLog, LogType
from app.schemas.fleet import VehicleLogCreate, VehicleLogUpdate
from app.services.base import CRUDBase


class VehicleLogService(CRUDBase[VehicleLog, VehicleLogCreate, VehicleLogUpdate]):
    """Service for VehicleLog operations"""

    def get_logs_for_vehicle(self, db: Session, vehicle_id: int, *, skip: int = 0, limit: int = 100) -> List[VehicleLog]:
        """Get logs for a vehicle"""
        return (
            db.query(VehicleLog)
            .filter(VehicleLog.vehicle_id == vehicle_id)
            .order_by(VehicleLog.log_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_logs_for_courier(self, db: Session, courier_id: int, *, skip: int = 0, limit: int = 100) -> List[VehicleLog]:
        """Get logs for a courier"""
        return (
            db.query(VehicleLog)
            .filter(VehicleLog.courier_id == courier_id)
            .order_by(VehicleLog.log_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_logs_by_date_range(
        self,
        db: Session,
        start_date: date,
        end_date: date,
        vehicle_id: int = None,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[VehicleLog]:
        """Get logs within a date range"""
        query = db.query(VehicleLog).filter(
            and_(VehicleLog.log_date >= start_date, VehicleLog.log_date <= end_date)
        )

        if vehicle_id:
            query = query.filter(VehicleLog.vehicle_id == vehicle_id)

        return query.order_by(VehicleLog.log_date.desc()).offset(skip).limit(limit).all()

    def get_fuel_logs(self, db: Session, vehicle_id: int, *, skip: int = 0, limit: int = 100) -> List[VehicleLog]:
        """Get fuel refill logs for a vehicle"""
        return (
            db.query(VehicleLog)
            .filter(VehicleLog.vehicle_id == vehicle_id)
            .filter(VehicleLog.log_type == LogType.FUEL_REFILL)
            .order_by(VehicleLog.log_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


vehicle_log_service = VehicleLogService(VehicleLog)
