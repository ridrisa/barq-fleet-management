from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.operations.sla import SLADefinition, SLAStatus, SLATracking, SLAType
from app.schemas.operations.sla import (
    SLADefinitionCreate,
    SLADefinitionUpdate,
    SLATrackingCreate,
    SLATrackingUpdate,
)


class CRUDSLADefinition(CRUDBase[SLADefinition, SLADefinitionCreate, SLADefinitionUpdate]):
    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SLADefinition]:
        """Get multiple definitions with organization filter"""
        query = db.query(self.model)
        if organization_id:
            query = query.filter(self.model.organization_id == organization_id)
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        return query.offset(skip).limit(limit).all()

    def get_by_code(
        self, db: Session, *, sla_code: str, organization_id: Optional[int] = None
    ) -> Optional[SLADefinition]:
        """Get SLA definition by code"""
        query = db.query(SLADefinition).filter(SLADefinition.sla_code == sla_code)
        if organization_id:
            query = query.filter(SLADefinition.organization_id == organization_id)
        return query.first()

    def get_active_slas(
        self, db: Session, *, organization_id: Optional[int] = None
    ) -> List[SLADefinition]:
        """Get all active SLA definitions"""
        now = datetime.utcnow()
        query = db.query(SLADefinition).filter(
            SLADefinition.is_active == True,
            SLADefinition.effective_from <= now,
            (SLADefinition.effective_until.is_(None)) | (SLADefinition.effective_until >= now),
        )
        if organization_id:
            query = query.filter(SLADefinition.organization_id == organization_id)
        return query.all()

    def get_by_type(
        self, db: Session, *, sla_type: SLAType, organization_id: Optional[int] = None
    ) -> List[SLADefinition]:
        """Get SLA definitions by type"""
        query = db.query(SLADefinition).filter(
            SLADefinition.sla_type == sla_type, SLADefinition.is_active == True
        )
        if organization_id:
            query = query.filter(SLADefinition.organization_id == organization_id)
        return query.all()

    def get_by_zone(
        self, db: Session, *, zone_id: int, organization_id: Optional[int] = None
    ) -> List[SLADefinition]:
        """Get SLA definitions for a specific zone"""
        query = db.query(SLADefinition).filter(
            SLADefinition.applies_to_zone_id == zone_id, SLADefinition.is_active == True
        )
        if organization_id:
            query = query.filter(SLADefinition.organization_id == organization_id)
        return query.all()

    def create(
        self, db: Session, *, obj_in: SLADefinitionCreate, organization_id: Optional[int] = None
    ) -> SLADefinition:
        """Create a new SLA definition"""
        obj_in_data = obj_in.model_dump()
        if organization_id:
            obj_in_data["organization_id"] = organization_id
        db_obj = SLADefinition(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDSLATracking(CRUDBase[SLATracking, SLATrackingCreate, SLATrackingUpdate]):
    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SLATracking]:
        """Get multiple trackings with organization filter"""
        query = db.query(self.model)
        if organization_id:
            query = query.filter(self.model.organization_id == organization_id)
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        return query.order_by(self.model.id.desc()).offset(skip).limit(limit).all()

    def create_with_number(
        self, db: Session, *, obj_in: SLATrackingCreate, organization_id: Optional[int] = None
    ) -> SLATracking:
        """Create SLA tracking with auto-generated number"""
        last_tracking = db.query(SLATracking).order_by(SLATracking.id.desc()).first()
        next_number = 1 if not last_tracking else last_tracking.id + 1
        tracking_number = f"SLA-{datetime.now().strftime('%Y%m%d')}-{next_number:04d}"

        obj_in_data = obj_in.model_dump()
        if organization_id:
            obj_in_data["organization_id"] = organization_id
        db_obj = SLATracking(**obj_in_data, tracking_number=tracking_number)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_number(
        self, db: Session, *, tracking_number: str, organization_id: Optional[int] = None
    ) -> Optional[SLATracking]:
        """Get SLA tracking by number"""
        query = db.query(SLATracking).filter(SLATracking.tracking_number == tracking_number)
        if organization_id:
            query = query.filter(SLATracking.organization_id == organization_id)
        return query.first()

    def get_active(
        self, db: Session, *, skip: int = 0, limit: int = 100, organization_id: Optional[int] = None
    ) -> List[SLATracking]:
        """Get all active SLA trackings"""
        query = db.query(SLATracking).filter(SLATracking.status == SLAStatus.ACTIVE)
        if organization_id:
            query = query.filter(SLATracking.organization_id == organization_id)
        return query.offset(skip).limit(limit).all()

    def get_at_risk(
        self, db: Session, *, skip: int = 0, limit: int = 100, organization_id: Optional[int] = None
    ) -> List[SLATracking]:
        """Get SLA trackings at risk of breach"""
        query = db.query(SLATracking).filter(SLATracking.status == SLAStatus.AT_RISK)
        if organization_id:
            query = query.filter(SLATracking.organization_id == organization_id)
        return query.order_by(SLATracking.target_completion_time.asc()).offset(skip).limit(limit).all()

    def get_breached(
        self, db: Session, *, skip: int = 0, limit: int = 100, organization_id: Optional[int] = None
    ) -> List[SLATracking]:
        """Get breached SLAs"""
        query = db.query(SLATracking).filter(SLATracking.is_breached == True)
        if organization_id:
            query = query.filter(SLATracking.organization_id == organization_id)
        return query.order_by(SLATracking.breach_time.desc()).offset(skip).limit(limit).all()

    def get_by_delivery(
        self, db: Session, *, delivery_id: int, organization_id: Optional[int] = None
    ) -> List[SLATracking]:
        """Get SLA trackings for a delivery"""
        query = db.query(SLATracking).filter(SLATracking.delivery_id == delivery_id)
        if organization_id:
            query = query.filter(SLATracking.organization_id == organization_id)
        return query.all()

    def get_by_courier(
        self,
        db: Session,
        *,
        courier_id: int,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
    ) -> List[SLATracking]:
        """Get SLA trackings for a courier"""
        query = db.query(SLATracking).filter(SLATracking.courier_id == courier_id)
        if organization_id:
            query = query.filter(SLATracking.organization_id == organization_id)
        return query.order_by(SLATracking.start_time.desc()).offset(skip).limit(limit).all()

    def mark_as_breached(
        self, db: Session, *, tracking_id: int, breach_reason: str, severity: str
    ) -> Optional[SLATracking]:
        """Mark SLA as breached"""
        tracking = self.get(db, id=tracking_id)
        if tracking:
            tracking.status = SLAStatus.BREACHED
            tracking.is_breached = True
            tracking.breach_time = datetime.utcnow()
            tracking.breach_reason = breach_reason
            tracking.breach_severity = severity
            db.add(tracking)
            db.commit()
            db.refresh(tracking)
        return tracking

    def mark_as_met(
        self, db: Session, *, tracking_id: int, actual_value: float
    ) -> Optional[SLATracking]:
        """Mark SLA as met"""
        tracking = self.get(db, id=tracking_id)
        if tracking:
            tracking.status = SLAStatus.MET
            tracking.actual_completion_time = datetime.utcnow()
            tracking.actual_value = actual_value
            # Calculate variance
            tracking.variance = actual_value - float(tracking.target_value)
            if tracking.target_value != 0:
                tracking.variance_percentage = (
                    tracking.variance / float(tracking.target_value)
                ) * 100
            # Calculate compliance score
            tracking.compliance_score = max(0, min(100, 100 - abs(tracking.variance_percentage)))
            db.add(tracking)
            db.commit()
            db.refresh(tracking)
        return tracking

    def escalate(
        self, db: Session, *, tracking_id: int, escalated_to_id: int
    ) -> Optional[SLATracking]:
        """Escalate SLA tracking"""
        tracking = self.get(db, id=tracking_id)
        if tracking:
            tracking.escalated = True
            tracking.escalated_to_id = escalated_to_id
            tracking.escalated_at = datetime.utcnow()
            db.add(tracking)
            db.commit()
            db.refresh(tracking)
        return tracking


sla_definition = CRUDSLADefinition(SLADefinition)
sla_tracking = CRUDSLATracking(SLATracking)
