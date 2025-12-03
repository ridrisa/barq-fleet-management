from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.operations.dispatch import DispatchAssignment, DispatchPriority, DispatchStatus
from app.schemas.operations.dispatch import DispatchAssignmentCreate, DispatchAssignmentUpdate


class CRUDDispatchAssignment(
    CRUDBase[DispatchAssignment, DispatchAssignmentCreate, DispatchAssignmentUpdate]
):
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, organization_id: int = None
    ) -> List[DispatchAssignment]:
        """Get multiple dispatch assignments with optional organization filter"""
        query = db.query(DispatchAssignment)
        if organization_id:
            query = query.filter(DispatchAssignment.organization_id == organization_id)
        return query.order_by(DispatchAssignment.created_at_time.desc()).offset(skip).limit(limit).all()

    def create_with_number(
        self, db: Session, *, obj_in: DispatchAssignmentCreate, organization_id: int = None
    ) -> DispatchAssignment:
        """Create dispatch assignment with auto-generated number"""
        last_assignment = (
            db.query(DispatchAssignment).order_by(DispatchAssignment.id.desc()).first()
        )
        next_number = 1 if not last_assignment else last_assignment.id + 1
        assignment_number = f"DISP-{datetime.now().strftime('%Y%m%d')}-{next_number:04d}"

        obj_in_data = obj_in.model_dump()
        if organization_id:
            obj_in_data["organization_id"] = organization_id
        db_obj = DispatchAssignment(
            **obj_in_data, assignment_number=assignment_number, created_at_time=datetime.utcnow()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_number(
        self, db: Session, *, assignment_number: str, organization_id: int = None
    ) -> Optional[DispatchAssignment]:
        """Get dispatch by assignment number"""
        query = db.query(DispatchAssignment).filter(
            DispatchAssignment.assignment_number == assignment_number
        )
        if organization_id:
            query = query.filter(DispatchAssignment.organization_id == organization_id)
        return query.first()

    def get_by_delivery(
        self, db: Session, *, delivery_id: int, organization_id: int = None
    ) -> Optional[DispatchAssignment]:
        """Get active dispatch assignment for delivery"""
        query = db.query(DispatchAssignment).filter(
            DispatchAssignment.delivery_id == delivery_id,
            DispatchAssignment.status.in_(
                [
                    DispatchStatus.PENDING,
                    DispatchStatus.ASSIGNED,
                    DispatchStatus.ACCEPTED,
                    DispatchStatus.IN_PROGRESS,
                ]
            ),
        )
        if organization_id:
            query = query.filter(DispatchAssignment.organization_id == organization_id)
        return query.first()

    def get_by_courier(
        self, db: Session, *, courier_id: int, skip: int = 0, limit: int = 100, organization_id: int = None
    ) -> List[DispatchAssignment]:
        """Get assignments for a courier"""
        query = db.query(DispatchAssignment).filter(DispatchAssignment.courier_id == courier_id)
        if organization_id:
            query = query.filter(DispatchAssignment.organization_id == organization_id)
        return query.order_by(DispatchAssignment.created_at_time.desc()).offset(skip).limit(limit).all()

    def get_pending(
        self, db: Session, *, skip: int = 0, limit: int = 100, organization_id: int = None
    ) -> List[DispatchAssignment]:
        """Get all pending assignments"""
        query = db.query(DispatchAssignment).filter(DispatchAssignment.status == DispatchStatus.PENDING)
        if organization_id:
            query = query.filter(DispatchAssignment.organization_id == organization_id)
        return query.order_by(
            DispatchAssignment.priority.desc(), DispatchAssignment.created_at_time.asc()
        ).offset(skip).limit(limit).all()

    def get_active_by_courier(
        self, db: Session, *, courier_id: int, organization_id: int = None
    ) -> List[DispatchAssignment]:
        """Get active assignments for a courier"""
        query = db.query(DispatchAssignment).filter(
            DispatchAssignment.courier_id == courier_id,
            DispatchAssignment.status.in_(
                [DispatchStatus.ASSIGNED, DispatchStatus.ACCEPTED, DispatchStatus.IN_PROGRESS]
            ),
        )
        if organization_id:
            query = query.filter(DispatchAssignment.organization_id == organization_id)
        return query.all()

    def get_by_zone(
        self, db: Session, *, zone_id: int, skip: int = 0, limit: int = 100, organization_id: int = None
    ) -> List[DispatchAssignment]:
        """Get assignments for a zone"""
        query = db.query(DispatchAssignment).filter(DispatchAssignment.zone_id == zone_id)
        if organization_id:
            query = query.filter(DispatchAssignment.organization_id == organization_id)
        return query.order_by(DispatchAssignment.created_at_time.desc()).offset(skip).limit(limit).all()

    def assign_to_courier(
        self, db: Session, *, assignment_id: int, courier_id: int, assigned_by_id: int
    ) -> Optional[DispatchAssignment]:
        """Assign delivery to courier"""
        assignment = self.get(db, id=assignment_id)
        if assignment and assignment.status == DispatchStatus.PENDING:
            assignment.courier_id = courier_id
            assignment.status = DispatchStatus.ASSIGNED
            assignment.assigned_at = datetime.utcnow()
            assignment.assigned_by_id = assigned_by_id
            db.add(assignment)
            db.commit()
            db.refresh(assignment)
        return assignment

    def accept(self, db: Session, *, assignment_id: int) -> Optional[DispatchAssignment]:
        """Courier accepts assignment"""
        assignment = self.get(db, id=assignment_id)
        if assignment and assignment.status == DispatchStatus.ASSIGNED:
            assignment.status = DispatchStatus.ACCEPTED
            assignment.accepted_at = datetime.utcnow()
            db.add(assignment)
            db.commit()
            db.refresh(assignment)
        return assignment

    def reject(
        self, db: Session, *, assignment_id: int, rejection_reason: str
    ) -> Optional[DispatchAssignment]:
        """Courier rejects assignment"""
        assignment = self.get(db, id=assignment_id)
        if assignment and assignment.status in [DispatchStatus.PENDING, DispatchStatus.ASSIGNED]:
            assignment.status = DispatchStatus.REJECTED
            assignment.rejection_reason = rejection_reason
            assignment.rejected_at = datetime.utcnow()
            assignment.rejection_count += 1
            db.add(assignment)
            db.commit()
            db.refresh(assignment)
        return assignment

    def start(self, db: Session, *, assignment_id: int) -> Optional[DispatchAssignment]:
        """Start delivery"""
        assignment = self.get(db, id=assignment_id)
        if assignment and assignment.status == DispatchStatus.ACCEPTED:
            assignment.status = DispatchStatus.IN_PROGRESS
            assignment.started_at = datetime.utcnow()
            db.add(assignment)
            db.commit()
            db.refresh(assignment)
        return assignment

    def complete(self, db: Session, *, assignment_id: int) -> Optional[DispatchAssignment]:
        """Complete assignment"""
        assignment = self.get(db, id=assignment_id)
        if assignment and assignment.status == DispatchStatus.IN_PROGRESS:
            assignment.status = DispatchStatus.COMPLETED
            assignment.completed_at = datetime.utcnow()
            # Calculate actual time
            if assignment.started_at:
                duration = (assignment.completed_at - assignment.started_at).total_seconds() / 60
                assignment.actual_completion_time_minutes = int(duration)
                if assignment.estimated_time_minutes:
                    assignment.performance_variance = (
                        assignment.actual_completion_time_minutes
                        - assignment.estimated_time_minutes
                    )
            db.add(assignment)
            db.commit()
            db.refresh(assignment)
        return assignment

    def reassign(
        self, db: Session, *, assignment_id: int, new_courier_id: int, reason: str
    ) -> Optional[DispatchAssignment]:
        """Reassign to different courier"""
        assignment = self.get(db, id=assignment_id)
        if assignment:
            assignment.previous_courier_id = assignment.courier_id
            assignment.courier_id = new_courier_id
            assignment.is_reassignment = True
            assignment.reassignment_reason = reason
            assignment.status = DispatchStatus.ASSIGNED
            assignment.assigned_at = datetime.utcnow()
            db.add(assignment)
            db.commit()
            db.refresh(assignment)
        return assignment


dispatch_assignment = CRUDDispatchAssignment(DispatchAssignment)
