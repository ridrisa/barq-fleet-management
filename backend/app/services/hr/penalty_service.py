"""
Penalty Service for HR module.

Handles CRUD operations and business logic for courier penalties.
"""

import secrets
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.hr.penalty import Penalty, PenaltyStatus, PenaltyType


class PenaltyService:
    """Service for managing courier penalties"""

    @staticmethod
    def generate_reference_number() -> str:
        """Generate a unique reference number for the penalty"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = secrets.token_hex(3).upper()
        return f"PEN-{timestamp}-{random_suffix}"

    def get(self, db: Session, id: int) -> Optional[Penalty]:
        """Get a penalty by ID"""
        return db.query(Penalty).filter(Penalty.id == id).first()

    def get_multi(
        self,
        db: Session,
        *,
        organization_id: int,
        skip: int = 0,
        limit: int = 100,
        courier_id: Optional[int] = None,
        penalty_type: Optional[PenaltyType] = None,
        status: Optional[PenaltyStatus] = None,
    ) -> List[Penalty]:
        """Get multiple penalties with optional filters"""
        query = db.query(Penalty).filter(Penalty.organization_id == organization_id)

        if courier_id:
            query = query.filter(Penalty.courier_id == courier_id)
        if penalty_type:
            query = query.filter(Penalty.penalty_type == penalty_type)
        if status:
            query = query.filter(Penalty.status == status)

        return query.order_by(Penalty.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_courier(
        self,
        db: Session,
        *,
        courier_id: int,
        organization_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Penalty]:
        """Get all penalties for a specific courier"""
        return (
            db.query(Penalty)
            .filter(
                Penalty.courier_id == courier_id,
                Penalty.organization_id == organization_id,
            )
            .order_by(Penalty.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_pending(
        self,
        db: Session,
        *,
        organization_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Penalty]:
        """Get all pending penalties awaiting approval"""
        return (
            db.query(Penalty)
            .filter(
                Penalty.organization_id == organization_id,
                Penalty.status == PenaltyStatus.PENDING,
            )
            .order_by(Penalty.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(
        self,
        db: Session,
        *,
        courier_id: int,
        penalty_type: PenaltyType,
        amount: Decimal,
        reason: str,
        organization_id: int,
        incident_date: Optional[datetime] = None,
        incident_id: Optional[int] = None,
        sla_tracking_id: Optional[int] = None,
        delivery_id: Optional[int] = None,
        created_by_id: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> Penalty:
        """Create a new penalty"""
        penalty = Penalty(
            courier_id=courier_id,
            penalty_type=penalty_type,
            amount=amount,
            reason=reason,
            organization_id=organization_id,
            incident_date=incident_date or datetime.now().date(),
            reference_number=self.generate_reference_number(),
            incident_id=incident_id,
            sla_tracking_id=sla_tracking_id,
            delivery_id=delivery_id,
            created_by_id=created_by_id,
            status=PenaltyStatus.PENDING,
            notes=notes,
        )

        db.add(penalty)
        db.commit()
        db.refresh(penalty)
        return penalty

    def update(
        self,
        db: Session,
        *,
        penalty: Penalty,
        penalty_type: Optional[PenaltyType] = None,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None,
        incident_date: Optional[datetime] = None,
        notes: Optional[str] = None,
    ) -> Penalty:
        """Update a penalty (only if pending)"""
        if not penalty.is_editable:
            raise ValueError("Cannot edit penalty that is not in pending status")

        if penalty_type is not None:
            penalty.penalty_type = penalty_type
        if amount is not None:
            penalty.amount = amount
        if reason is not None:
            penalty.reason = reason
        if incident_date is not None:
            penalty.incident_date = incident_date
        if notes is not None:
            penalty.notes = notes

        db.commit()
        db.refresh(penalty)
        return penalty

    def approve(
        self,
        db: Session,
        *,
        penalty: Penalty,
        approved_by_id: int,
    ) -> Penalty:
        """Approve a pending penalty"""
        if penalty.status != PenaltyStatus.PENDING:
            raise ValueError("Can only approve pending penalties")

        penalty.status = PenaltyStatus.APPROVED
        penalty.approved_by_id = approved_by_id
        penalty.approved_at = datetime.utcnow()

        db.commit()
        db.refresh(penalty)
        return penalty

    def reject(
        self,
        db: Session,
        *,
        penalty: Penalty,
        rejected_by_id: int,
        rejection_reason: Optional[str] = None,
    ) -> Penalty:
        """Reject a pending penalty"""
        if penalty.status != PenaltyStatus.PENDING:
            raise ValueError("Can only reject pending penalties")

        penalty.status = PenaltyStatus.REJECTED
        penalty.approved_by_id = rejected_by_id
        penalty.approved_at = datetime.utcnow()
        if rejection_reason:
            penalty.notes = (penalty.notes or "") + f"\nRejection reason: {rejection_reason}"

        db.commit()
        db.refresh(penalty)
        return penalty

    def appeal(
        self,
        db: Session,
        *,
        penalty: Penalty,
        appeal_reason: str,
    ) -> Penalty:
        """Appeal a penalty"""
        if not penalty.is_appealable:
            raise ValueError("This penalty cannot be appealed")

        penalty.status = PenaltyStatus.APPEALED
        penalty.appeal_reason = appeal_reason

        db.commit()
        db.refresh(penalty)
        return penalty

    def resolve_appeal(
        self,
        db: Session,
        *,
        penalty: Penalty,
        resolution: str,
        waive: bool = False,
        resolved_by_id: int,
    ) -> Penalty:
        """Resolve an appealed penalty"""
        if penalty.status != PenaltyStatus.APPEALED:
            raise ValueError("Can only resolve appealed penalties")

        penalty.appeal_resolved_at = datetime.utcnow()
        penalty.appeal_resolution = resolution

        if waive:
            penalty.status = PenaltyStatus.WAIVED
        else:
            penalty.status = PenaltyStatus.APPROVED

        db.commit()
        db.refresh(penalty)
        return penalty

    def apply_to_salary(
        self,
        db: Session,
        *,
        penalty: Penalty,
        salary_id: int,
    ) -> Penalty:
        """Mark penalty as applied to a salary"""
        if penalty.status != PenaltyStatus.APPROVED:
            raise ValueError("Can only apply approved penalties to salary")

        penalty.status = PenaltyStatus.APPLIED
        penalty.salary_id = salary_id
        penalty.applied_at = datetime.utcnow()

        db.commit()
        db.refresh(penalty)
        return penalty

    def delete(self, db: Session, *, id: int) -> bool:
        """Delete a penalty (only if pending)"""
        penalty = self.get(db, id=id)
        if not penalty:
            return False

        if not penalty.is_editable:
            raise ValueError("Cannot delete penalty that is not in pending status")

        db.delete(penalty)
        db.commit()
        return True

    def get_total_penalties_for_courier(
        self,
        db: Session,
        *,
        courier_id: int,
        organization_id: int,
        year: Optional[int] = None,
        month: Optional[int] = None,
    ) -> Decimal:
        """Get total penalty amount for a courier"""
        from sqlalchemy import func, extract

        query = db.query(func.sum(Penalty.amount)).filter(
            Penalty.courier_id == courier_id,
            Penalty.organization_id == organization_id,
            Penalty.status.in_([PenaltyStatus.APPROVED, PenaltyStatus.APPLIED]),
        )

        if year:
            query = query.filter(extract("year", Penalty.incident_date) == year)
        if month:
            query = query.filter(extract("month", Penalty.incident_date) == month)

        result = query.scalar()
        return Decimal(result) if result else Decimal("0")


# Global service instance
penalty_service = PenaltyService()
