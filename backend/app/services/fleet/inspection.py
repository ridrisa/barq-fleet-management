from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.fleet import Inspection, InspectionStatus, InspectionType
from app.schemas.fleet import InspectionCreate, InspectionUpdate
from app.services.base import CRUDBase


class InspectionService(CRUDBase[Inspection, InspectionCreate, InspectionUpdate]):
    """Service for Inspection operations"""

    def get_for_vehicle(
        self,
        db: Session,
        vehicle_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
    ) -> List[Inspection]:
        """Get inspections for a vehicle"""
        query = db.query(Inspection).filter(Inspection.vehicle_id == vehicle_id)

        if organization_id:
            query = query.filter(Inspection.organization_id == organization_id)

        return query.order_by(Inspection.inspection_date.desc()).offset(skip).limit(limit).all()

    def get_latest_for_vehicle(
        self, db: Session, vehicle_id: int, organization_id: Optional[int] = None
    ) -> Inspection:
        """Get latest inspection for a vehicle"""
        query = db.query(Inspection).filter(Inspection.vehicle_id == vehicle_id)

        if organization_id:
            query = query.filter(Inspection.organization_id == organization_id)

        return query.order_by(Inspection.inspection_date.desc()).first()

    def get_failed_inspections(
        self, db: Session, *, skip: int = 0, limit: int = 100, organization_id: Optional[int] = None
    ) -> List[Inspection]:
        """Get failed inspections"""
        query = db.query(Inspection).filter(Inspection.status == InspectionStatus.FAILED)

        if organization_id:
            query = query.filter(Inspection.organization_id == organization_id)

        return query.order_by(Inspection.inspection_date.desc()).offset(skip).limit(limit).all()

    def get_by_type(
        self,
        db: Session,
        inspection_type: InspectionType,
        *,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
    ) -> List[Inspection]:
        """Get inspections by type"""
        query = db.query(Inspection).filter(Inspection.inspection_type == inspection_type)

        if organization_id:
            query = query.filter(Inspection.organization_id == organization_id)

        return query.order_by(Inspection.inspection_date.desc()).offset(skip).limit(limit).all()

    def get_requiring_follow_up(
        self, db: Session, *, skip: int = 0, limit: int = 100, organization_id: Optional[int] = None
    ) -> List[Inspection]:
        """Get inspections requiring follow-up"""
        query = (
            db.query(Inspection)
            .filter(Inspection.requires_follow_up == True)
            .filter(Inspection.repairs_completed == False)
        )

        if organization_id:
            query = query.filter(Inspection.organization_id == organization_id)

        return query.order_by(Inspection.follow_up_date).offset(skip).limit(limit).all()


inspection_service = InspectionService(Inspection)
