from datetime import datetime
from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.operations.handover import Handover, HandoverStatus, HandoverType
from app.schemas.operations.handover import HandoverCreate, HandoverUpdate


class CRUDHandover(CRUDBase[Handover, HandoverCreate, HandoverUpdate]):
    def create_with_number(self, db: Session, *, obj_in: HandoverCreate) -> Handover:
        """Create handover with auto-generated number"""
        # Generate handover number
        last_handover = db.query(Handover).order_by(Handover.id.desc()).first()
        next_number = 1 if not last_handover else last_handover.id + 1
        handover_number = f"HO-{datetime.now().strftime('%Y%m%d')}-{next_number:04d}"

        obj_in_data = obj_in.model_dump()
        db_obj = Handover(**obj_in_data, handover_number=handover_number)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_number(self, db: Session, *, handover_number: str) -> Optional[Handover]:
        """Get handover by unique number"""
        return db.query(Handover).filter(Handover.handover_number == handover_number).first()

    def get_by_courier(
        self, db: Session, *, courier_id: int, skip: int = 0, limit: int = 100
    ) -> List[Handover]:
        """Get handovers involving a specific courier"""
        return (
            db.query(Handover)
            .filter(
                or_(Handover.from_courier_id == courier_id, Handover.to_courier_id == courier_id)
            )
            .order_by(Handover.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_vehicle(
        self, db: Session, *, vehicle_id: int, skip: int = 0, limit: int = 100
    ) -> List[Handover]:
        """Get handovers for a specific vehicle"""
        return (
            db.query(Handover)
            .filter(Handover.vehicle_id == vehicle_id)
            .order_by(Handover.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_pending(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Handover]:
        """Get all pending handovers"""
        return (
            db.query(Handover)
            .filter(Handover.status == HandoverStatus.PENDING)
            .order_by(Handover.scheduled_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def approve(self, db: Session, *, handover_id: int, approved_by_id: int) -> Optional[Handover]:
        """Approve a handover"""
        handover = self.get(db, id=handover_id)
        if handover and handover.status == HandoverStatus.PENDING:
            handover.status = HandoverStatus.APPROVED
            handover.approved_by_id = approved_by_id
            handover.approved_at = datetime.utcnow()
            db.add(handover)
            db.commit()
            db.refresh(handover)
        return handover

    def reject(self, db: Session, *, handover_id: int, rejection_reason: str) -> Optional[Handover]:
        """Reject a handover"""
        handover = self.get(db, id=handover_id)
        if handover and handover.status == HandoverStatus.PENDING:
            handover.status = HandoverStatus.REJECTED
            handover.rejection_reason = rejection_reason
            db.add(handover)
            db.commit()
            db.refresh(handover)
        return handover

    def complete(self, db: Session, *, handover_id: int) -> Optional[Handover]:
        """Mark handover as completed"""
        handover = self.get(db, id=handover_id)
        if handover and handover.status == HandoverStatus.APPROVED:
            handover.status = HandoverStatus.COMPLETED
            handover.completed_at = datetime.utcnow()
            db.add(handover)
            db.commit()
            db.refresh(handover)
        return handover


handover = CRUDHandover(Handover)
