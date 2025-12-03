from datetime import date
from typing import List, Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.fleet import LogType, VehicleLog
from app.schemas.fleet import VehicleLogCreate, VehicleLogUpdate
from app.services.base import CRUDBase


class VehicleLogService(CRUDBase[VehicleLog, VehicleLogCreate, VehicleLogUpdate]):
    """Service for VehicleLog operations"""

    def get_logs_for_vehicle(
        self,
        db: Session,
        vehicle_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
    ) -> List[VehicleLog]:
        """Get logs for a vehicle"""
        query = db.query(VehicleLog).filter(VehicleLog.vehicle_id == vehicle_id)

        if organization_id:
            query = query.filter(VehicleLog.organization_id == organization_id)

        return query.order_by(VehicleLog.log_date.desc()).offset(skip).limit(limit).all()

    def get_logs_for_courier(
        self,
        db: Session,
        courier_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
    ) -> List[VehicleLog]:
        """Get logs for a courier"""
        query = db.query(VehicleLog).filter(VehicleLog.courier_id == courier_id)

        if organization_id:
            query = query.filter(VehicleLog.organization_id == organization_id)

        return query.order_by(VehicleLog.log_date.desc()).offset(skip).limit(limit).all()

    def get_logs_by_date_range(
        self,
        db: Session,
        start_date: date,
        end_date: date,
        vehicle_id: int = None,
        *,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
    ) -> List[VehicleLog]:
        """Get logs within a date range"""
        query = db.query(VehicleLog).filter(
            and_(VehicleLog.log_date >= start_date, VehicleLog.log_date <= end_date)
        )

        if organization_id:
            query = query.filter(VehicleLog.organization_id == organization_id)

        if vehicle_id:
            query = query.filter(VehicleLog.vehicle_id == vehicle_id)

        return query.order_by(VehicleLog.log_date.desc()).offset(skip).limit(limit).all()

    def get_fuel_logs(
        self,
        db: Session,
        vehicle_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
    ) -> List[VehicleLog]:
        """Get fuel refill logs for a vehicle"""
        query = (
            db.query(VehicleLog)
            .filter(VehicleLog.vehicle_id == vehicle_id)
            .filter(VehicleLog.log_type == LogType.FUEL_REFILL)
        )

        if organization_id:
            query = query.filter(VehicleLog.organization_id == organization_id)

        return query.order_by(VehicleLog.log_date.desc()).offset(skip).limit(limit).all()


vehicle_log_service = VehicleLogService(VehicleLog)
