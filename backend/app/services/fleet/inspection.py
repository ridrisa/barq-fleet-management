from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, timedelta
from app.models.fleet import Inspection, InspectionStatus, InspectionType
from app.schemas.fleet import InspectionCreate, InspectionUpdate
from app.services.base import CRUDBase


class InspectionService(CRUDBase[Inspection, InspectionCreate, InspectionUpdate]):
    """Service for Inspection operations"""

    def get_for_vehicle(self, db: Session, vehicle_id: int, *, skip: int = 0, limit: int = 100) -> List[Inspection]:
        """Get inspections for a vehicle"""
        return (
            db.query(Inspection)
            .filter(Inspection.vehicle_id == vehicle_id)
            .order_by(Inspection.inspection_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_latest_for_vehicle(self, db: Session, vehicle_id: int) -> Inspection:
        """Get latest inspection for a vehicle"""
        return (
            db.query(Inspection)
            .filter(Inspection.vehicle_id == vehicle_id)
            .order_by(Inspection.inspection_date.desc())
            .first()
        )

    def get_failed_inspections(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Inspection]:
        """Get failed inspections"""
        return (
            db.query(Inspection)
            .filter(Inspection.status == InspectionStatus.FAILED)
            .order_by(Inspection.inspection_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_type(
        self,
        db: Session,
        inspection_type: InspectionType,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Inspection]:
        """Get inspections by type"""
        return (
            db.query(Inspection)
            .filter(Inspection.inspection_type == inspection_type)
            .order_by(Inspection.inspection_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_requiring_follow_up(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Inspection]:
        """Get inspections requiring follow-up"""
        return (
            db.query(Inspection)
            .filter(Inspection.requires_follow_up == True)
            .filter(Inspection.repairs_completed == False)
            .order_by(Inspection.follow_up_date)
            .offset(skip)
            .limit(limit)
            .all()
        )


inspection_service = InspectionService(Inspection)
