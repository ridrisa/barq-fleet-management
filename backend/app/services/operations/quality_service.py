"""Quality Service"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.operations.quality import (
    InspectionStatus,
    QualityInspection,
    QualityMetric,
    QualityMetricType,
)
from app.schemas.operations.quality import (
    QualityInspectionCreate,
    QualityInspectionUpdate,
    QualityMetricCreate,
    QualityMetricUpdate,
)
from app.services.base import CRUDBase


class QualityMetricService(CRUDBase[QualityMetric, QualityMetricCreate, QualityMetricUpdate]):
    """Service for quality metric management operations"""

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[QualityMetric]:
        """Get multiple metrics with organization filter"""
        query = db.query(self.model)
        if organization_id:
            query = query.filter(self.model.organization_id == organization_id)
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        return query.offset(skip).limit(limit).all()

    def get_by_code(
        self, db: Session, *, metric_code: str, organization_id: Optional[int] = None
    ) -> Optional[QualityMetric]:
        """Get metric by code"""
        query = db.query(QualityMetric).filter(QualityMetric.metric_code == metric_code)
        if organization_id:
            query = query.filter(QualityMetric.organization_id == organization_id)
        return query.first()

    def get_active_metrics(
        self, db: Session, *, organization_id: Optional[int] = None
    ) -> List[QualityMetric]:
        """Get all active quality metrics"""
        query = db.query(QualityMetric).filter(QualityMetric.is_active == True)
        if organization_id:
            query = query.filter(QualityMetric.organization_id == organization_id)
        return query.all()

    def get_by_type(
        self, db: Session, *, metric_type: QualityMetricType, organization_id: Optional[int] = None
    ) -> List[QualityMetric]:
        """Get metrics by type"""
        query = db.query(QualityMetric).filter(
            QualityMetric.metric_type == metric_type, QualityMetric.is_active == True
        )
        if organization_id:
            query = query.filter(QualityMetric.organization_id == organization_id)
        return query.all()

    def get_critical_metrics(
        self, db: Session, *, organization_id: Optional[int] = None
    ) -> List[QualityMetric]:
        """Get critical quality metrics"""
        query = db.query(QualityMetric).filter(
            QualityMetric.is_critical == True, QualityMetric.is_active == True
        )
        if organization_id:
            query = query.filter(QualityMetric.organization_id == organization_id)
        return query.all()

    def create(
        self, db: Session, *, obj_in: QualityMetricCreate, organization_id: Optional[int] = None
    ) -> QualityMetric:
        """Create a new quality metric"""
        obj_in_data = obj_in.model_dump()
        if organization_id:
            obj_in_data["organization_id"] = organization_id
        db_obj = QualityMetric(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class QualityInspectionService(
    CRUDBase[QualityInspection, QualityInspectionCreate, QualityInspectionUpdate]
):
    """Service for quality inspection management operations"""

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[QualityInspection]:
        """Get multiple inspections with organization filter"""
        query = db.query(self.model)
        if organization_id:
            query = query.filter(self.model.organization_id == organization_id)
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        return query.order_by(self.model.id.desc()).offset(skip).limit(limit).all()

    def create_with_number(
        self, db: Session, *, obj_in: QualityInspectionCreate, organization_id: Optional[int] = None
    ) -> QualityInspection:
        """Create inspection with auto-generated number"""
        last_inspection = (
            db.query(QualityInspection).order_by(QualityInspection.id.desc()).first()
        )
        next_number = 1 if not last_inspection else last_inspection.id + 1
        inspection_number = f"QI-{datetime.now().strftime('%Y%m%d')}-{next_number:04d}"

        obj_in_data = obj_in.model_dump()
        if organization_id:
            obj_in_data["organization_id"] = organization_id
        db_obj = QualityInspection(**obj_in_data, inspection_number=inspection_number)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_number(
        self, db: Session, *, inspection_number: str, organization_id: Optional[int] = None
    ) -> Optional[QualityInspection]:
        """Get inspection by number"""
        query = db.query(QualityInspection).filter(
            QualityInspection.inspection_number == inspection_number
        )
        if organization_id:
            query = query.filter(QualityInspection.organization_id == organization_id)
        return query.first()

    def get_by_courier(
        self,
        db: Session,
        *,
        courier_id: int,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
    ) -> List[QualityInspection]:
        """Get inspections for a courier"""
        query = db.query(QualityInspection).filter(QualityInspection.courier_id == courier_id)
        if organization_id:
            query = query.filter(QualityInspection.organization_id == organization_id)
        return (
            query.order_by(QualityInspection.scheduled_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_vehicle(
        self,
        db: Session,
        *,
        vehicle_id: int,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
    ) -> List[QualityInspection]:
        """Get inspections for a vehicle"""
        query = db.query(QualityInspection).filter(QualityInspection.vehicle_id == vehicle_id)
        if organization_id:
            query = query.filter(QualityInspection.organization_id == organization_id)
        return (
            query.order_by(QualityInspection.scheduled_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_scheduled_for_date(
        self, db: Session, *, target_date: date, organization_id: Optional[int] = None
    ) -> List[QualityInspection]:
        """Get inspections scheduled for a specific date"""
        query = db.query(QualityInspection).filter(
            QualityInspection.scheduled_date == target_date,
            QualityInspection.status == InspectionStatus.SCHEDULED,
        )
        if organization_id:
            query = query.filter(QualityInspection.organization_id == organization_id)
        return query.all()

    def get_requiring_followup(
        self, db: Session, *, organization_id: Optional[int] = None
    ) -> List[QualityInspection]:
        """Get inspections requiring follow-up"""
        query = db.query(QualityInspection).filter(
            QualityInspection.requires_followup == True,
            QualityInspection.followup_completed == False,
        )
        if organization_id:
            query = query.filter(QualityInspection.organization_id == organization_id)
        return query.all()

    def get_failed_inspections(
        self, db: Session, *, skip: int = 0, limit: int = 100, organization_id: Optional[int] = None
    ) -> List[QualityInspection]:
        """Get all failed inspections"""
        query = db.query(QualityInspection).filter(QualityInspection.passed == False)
        if organization_id:
            query = query.filter(QualityInspection.organization_id == organization_id)
        return (
            query.order_by(QualityInspection.inspection_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def complete_inspection(
        self, db: Session, *, inspection_id: int, score: float, passed: bool
    ) -> Optional[QualityInspection]:
        """Mark inspection as completed"""
        inspection = self.get(db, id=inspection_id)
        if inspection:
            inspection.status = InspectionStatus.PASSED if passed else InspectionStatus.FAILED
            inspection.overall_score = score
            inspection.passed = passed
            inspection.completed_date = datetime.utcnow()
            db.add(inspection)
            db.commit()
            db.refresh(inspection)
        return inspection


quality_metric_service = QualityMetricService(QualityMetric)
quality_inspection_service = QualityInspectionService(QualityInspection)
