from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, timedelta
from app.models.fleet import VehicleMaintenance, MaintenanceStatus, MaintenanceType
from app.schemas.fleet import MaintenanceCreate, MaintenanceUpdate
from app.services.base import CRUDBase


class MaintenanceService(CRUDBase[VehicleMaintenance, MaintenanceCreate, MaintenanceUpdate]):
    """Service for VehicleMaintenance operations"""

    def get_for_vehicle(self, db: Session, vehicle_id: int, *, skip: int = 0, limit: int = 100) -> List[VehicleMaintenance]:
        """Get maintenance records for a vehicle"""
        return (
            db.query(VehicleMaintenance)
            .filter(VehicleMaintenance.vehicle_id == vehicle_id)
            .order_by(VehicleMaintenance.scheduled_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_scheduled(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[VehicleMaintenance]:
        """Get scheduled maintenance"""
        return (
            db.query(VehicleMaintenance)
            .filter(VehicleMaintenance.status == MaintenanceStatus.SCHEDULED)
            .order_by(VehicleMaintenance.scheduled_date)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_overdue(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[VehicleMaintenance]:
        """Get overdue maintenance"""
        today = date.today()
        return (
            db.query(VehicleMaintenance)
            .filter(
                and_(
                    VehicleMaintenance.status == MaintenanceStatus.SCHEDULED,
                    VehicleMaintenance.scheduled_date < today
                )
            )
            .order_by(VehicleMaintenance.scheduled_date)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_in_progress(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[VehicleMaintenance]:
        """Get maintenance in progress"""
        return (
            db.query(VehicleMaintenance)
            .filter(VehicleMaintenance.status == MaintenanceStatus.IN_PROGRESS)
            .order_by(VehicleMaintenance.start_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


maintenance_service = MaintenanceService(VehicleMaintenance)
