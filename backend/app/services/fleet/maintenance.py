from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.fleet import MaintenanceStatus, MaintenanceType, VehicleMaintenance
from app.schemas.fleet import MaintenanceCreate, MaintenanceUpdate
from app.services.base import CRUDBase


class MaintenanceService(CRUDBase[VehicleMaintenance, MaintenanceCreate, MaintenanceUpdate]):
    """Service for VehicleMaintenance operations"""

    def get_for_vehicle(
        self,
        db: Session,
        vehicle_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
    ) -> List[VehicleMaintenance]:
        """Get maintenance records for a vehicle"""
        query = db.query(VehicleMaintenance).filter(VehicleMaintenance.vehicle_id == vehicle_id)

        if organization_id:
            query = query.filter(VehicleMaintenance.organization_id == organization_id)

        return (
            query.order_by(VehicleMaintenance.scheduled_date.desc()).offset(skip).limit(limit).all()
        )

    def get_scheduled(
        self, db: Session, *, skip: int = 0, limit: int = 100, organization_id: Optional[int] = None
    ) -> List[VehicleMaintenance]:
        """Get scheduled maintenance"""
        query = db.query(VehicleMaintenance).filter(
            VehicleMaintenance.status == MaintenanceStatus.SCHEDULED
        )

        if organization_id:
            query = query.filter(VehicleMaintenance.organization_id == organization_id)

        return query.order_by(VehicleMaintenance.scheduled_date).offset(skip).limit(limit).all()

    def get_overdue(
        self, db: Session, *, skip: int = 0, limit: int = 100, organization_id: Optional[int] = None
    ) -> List[VehicleMaintenance]:
        """Get overdue maintenance"""
        today = date.today()
        query = db.query(VehicleMaintenance).filter(
            and_(
                VehicleMaintenance.status == MaintenanceStatus.SCHEDULED,
                VehicleMaintenance.scheduled_date < today,
            )
        )

        if organization_id:
            query = query.filter(VehicleMaintenance.organization_id == organization_id)

        return query.order_by(VehicleMaintenance.scheduled_date).offset(skip).limit(limit).all()

    def get_in_progress(
        self, db: Session, *, skip: int = 0, limit: int = 100, organization_id: Optional[int] = None
    ) -> List[VehicleMaintenance]:
        """Get maintenance in progress"""
        query = db.query(VehicleMaintenance).filter(
            VehicleMaintenance.status == MaintenanceStatus.IN_PROGRESS
        )

        if organization_id:
            query = query.filter(VehicleMaintenance.organization_id == organization_id)

        return query.order_by(VehicleMaintenance.start_date.desc()).offset(skip).limit(limit).all()


maintenance_service = MaintenanceService(VehicleMaintenance)
