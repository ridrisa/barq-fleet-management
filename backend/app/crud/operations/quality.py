from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
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


class CRUDQualityMetric(CRUDBase[QualityMetric, QualityMetricCreate, QualityMetricUpdate]):
    def get_by_code(self, db: Session, *, metric_code: str) -> Optional[QualityMetric]:
        """Get metric by code"""
        return db.query(QualityMetric).filter(QualityMetric.metric_code == metric_code).first()

    def get_active_metrics(self, db: Session) -> List[QualityMetric]:
        """Get all active quality metrics"""
        return db.query(QualityMetric).filter(QualityMetric.is_active == True).all()

    def get_by_type(self, db: Session, *, metric_type: QualityMetricType) -> List[QualityMetric]:
        """Get metrics by type"""
        return (
            db.query(QualityMetric)
            .filter(QualityMetric.metric_type == metric_type, QualityMetric.is_active == True)
            .all()
        )

    def get_critical_metrics(self, db: Session) -> List[QualityMetric]:
        """Get critical quality metrics"""
        return (
            db.query(QualityMetric)
            .filter(QualityMetric.is_critical == True, QualityMetric.is_active == True)
            .all()
        )


class CRUDQualityInspection(
    CRUDBase[QualityInspection, QualityInspectionCreate, QualityInspectionUpdate]
):
    def create_with_number(
        self, db: Session, *, obj_in: QualityInspectionCreate
    ) -> QualityInspection:
        """Create inspection with auto-generated number"""
        last_inspection = db.query(QualityInspection).order_by(QualityInspection.id.desc()).first()
        next_number = 1 if not last_inspection else last_inspection.id + 1
        inspection_number = f"QI-{datetime.now().strftime('%Y%m%d')}-{next_number:04d}"

        obj_in_data = obj_in.model_dump()
        db_obj = QualityInspection(**obj_in_data, inspection_number=inspection_number)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_number(self, db: Session, *, inspection_number: str) -> Optional[QualityInspection]:
        """Get inspection by number"""
        return (
            db.query(QualityInspection)
            .filter(QualityInspection.inspection_number == inspection_number)
            .first()
        )

    def get_by_courier(
        self, db: Session, *, courier_id: int, skip: int = 0, limit: int = 100
    ) -> List[QualityInspection]:
        """Get inspections for a courier"""
        return (
            db.query(QualityInspection)
            .filter(QualityInspection.courier_id == courier_id)
            .order_by(QualityInspection.scheduled_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_vehicle(
        self, db: Session, *, vehicle_id: int, skip: int = 0, limit: int = 100
    ) -> List[QualityInspection]:
        """Get inspections for a vehicle"""
        return (
            db.query(QualityInspection)
            .filter(QualityInspection.vehicle_id == vehicle_id)
            .order_by(QualityInspection.scheduled_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_scheduled_for_date(self, db: Session, *, target_date: date) -> List[QualityInspection]:
        """Get inspections scheduled for a specific date"""
        return (
            db.query(QualityInspection)
            .filter(
                QualityInspection.scheduled_date == target_date,
                QualityInspection.status == InspectionStatus.SCHEDULED,
            )
            .all()
        )

    def get_requiring_followup(self, db: Session) -> List[QualityInspection]:
        """Get inspections requiring follow-up"""
        return (
            db.query(QualityInspection)
            .filter(
                QualityInspection.requires_followup == True,
                QualityInspection.followup_completed == False,
            )
            .all()
        )

    def get_failed_inspections(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[QualityInspection]:
        """Get all failed inspections"""
        return (
            db.query(QualityInspection)
            .filter(QualityInspection.passed == False)
            .order_by(QualityInspection.inspection_date.desc())
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


quality_metric = CRUDQualityMetric(QualityMetric)
quality_inspection = CRUDQualityInspection(QualityInspection)
