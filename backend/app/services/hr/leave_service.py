"""Leave Service"""

from datetime import date
from typing import Dict, List, Optional

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.hr.leave import Leave, LeaveStatus, LeaveType
from app.schemas.hr.leave import LeaveCreate, LeaveUpdate
from app.services.base import CRUDBase


class LeaveService(CRUDBase[Leave, LeaveCreate, LeaveUpdate]):
    """Service for leave management operations"""

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, organization_id: int | None = None
    ) -> List[Leave]:
        """Get multiple leave requests with courier data"""
        query = db.query(self.model).options(joinedload(self.model.courier))
        if organization_id:
            query = query.filter(self.model.organization_id == organization_id)
        return query.order_by(self.model.start_date.desc()).offset(skip).limit(limit).all()

    def get_by_courier(
        self, db: Session, *, courier_id: int, skip: int = 0, limit: int = 100, organization_id: int | None = None
    ) -> List[Leave]:
        """Get all leave requests for a courier"""
        query = (
            db.query(self.model)
            .options(joinedload(self.model.courier))
            .filter(self.model.courier_id == courier_id)
        )
        if organization_id:
            query = query.filter(self.model.organization_id == organization_id)
        return (
            query
            .order_by(self.model.start_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(
        self, db: Session, *, status: LeaveStatus, skip: int = 0, limit: int = 100, organization_id: int | None = None
    ) -> List[Leave]:
        """Get leave requests by status"""
        query = (
            db.query(self.model)
            .options(joinedload(self.model.courier))
            .filter(self.model.status == status)
        )
        if organization_id:
            query = query.filter(self.model.organization_id == organization_id)
        return (
            query
            .order_by(
                self.model.requested_at.desc()
                if hasattr(self.model, "requested_at")
                else self.model.start_date.desc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_date_range(
        self, db: Session, *, start_date: date, end_date: date, skip: int = 0, limit: int = 100, organization_id: int | None = None
    ) -> List[Leave]:
        """Get leave requests within a date range"""
        query = (
            db.query(self.model)
            .options(joinedload(self.model.courier))
            .filter(
                or_(
                    and_(self.model.start_date >= start_date, self.model.start_date <= end_date),
                    and_(self.model.end_date >= start_date, self.model.end_date <= end_date),
                    and_(self.model.start_date <= start_date, self.model.end_date >= end_date),
                )
            )
        )
        if organization_id:
            query = query.filter(self.model.organization_id == organization_id)
        return (
            query
            .order_by(self.model.start_date)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_leave_type(
        self, db: Session, *, leave_type: LeaveType, skip: int = 0, limit: int = 100, organization_id: int | None = None
    ) -> List[Leave]:
        """Get leave requests by leave type (annual, sick, emergency, unpaid)"""
        query = (
            db.query(self.model)
            .options(joinedload(self.model.courier))
            .filter(self.model.leave_type == leave_type)
        )
        if organization_id:
            query = query.filter(self.model.organization_id == organization_id)
        return (
            query
            .order_by(self.model.start_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def approve_leave(
        self, db: Session, *, leave_id: int, approved_by: int, notes: Optional[str] = None
    ) -> Optional[Leave]:
        """Approve a leave request"""
        leave = db.query(self.model).options(joinedload(self.model.courier)).filter(self.model.id == leave_id).first()
        if not leave:
            return None

        leave.status = LeaveStatus.APPROVED
        leave.approved_by = approved_by
        leave.approved_at = date.today()
        if notes and hasattr(leave, "notes"):
            leave.notes = notes

        db.commit()
        db.refresh(leave)
        return leave

    def reject_leave(
        self, db: Session, *, leave_id: int, approved_by: int, reason: Optional[str] = None
    ) -> Optional[Leave]:
        """Reject a leave request"""
        leave = db.query(self.model).options(joinedload(self.model.courier)).filter(self.model.id == leave_id).first()
        if not leave:
            return None

        leave.status = LeaveStatus.REJECTED
        leave.approved_by = approved_by
        leave.approved_at = date.today()
        if reason and hasattr(leave, "notes"):
            leave.notes = reason

        db.commit()
        db.refresh(leave)
        return leave

    def cancel_leave(self, db: Session, *, leave_id: int) -> Optional[Leave]:
        """Cancel a leave request"""
        leave = db.query(self.model).options(joinedload(self.model.courier)).filter(self.model.id == leave_id).first()
        if not leave:
            return None

        leave.status = LeaveStatus.CANCELLED
        db.commit()
        db.refresh(leave)
        return leave

    def get_leave_balance(self, db: Session, *, courier_id: int, year: int) -> Dict[str, float]:
        """Calculate leave balance for a courier for a given year"""
        # Get approved leaves for the year
        leaves = (
            db.query(self.model)
            .filter(
                and_(
                    self.model.courier_id == courier_id,
                    self.model.status == LeaveStatus.APPROVED,
                    func.extract("year", self.model.start_date) == year,
                )
            )
            .all()
        )

        total_days_taken = sum(leave.days for leave in leaves)

        # Assuming 30 days annual leave entitlement
        annual_entitlement = 30
        remaining = annual_entitlement - total_days_taken

        return {
            "annual_entitlement": annual_entitlement,
            "days_taken": total_days_taken,
            "days_remaining": remaining,
        }

    def get_statistics(self, db: Session) -> Dict:
        """Get leave statistics"""
        total = db.query(func.count(self.model.id)).scalar()

        pending = (
            db.query(func.count(self.model.id))
            .filter(self.model.status == LeaveStatus.PENDING)
            .scalar()
        )

        approved = (
            db.query(func.count(self.model.id))
            .filter(self.model.status == LeaveStatus.APPROVED)
            .scalar()
        )

        rejected = (
            db.query(func.count(self.model.id))
            .filter(self.model.status == LeaveStatus.REJECTED)
            .scalar()
        )

        return {
            "total": total or 0,
            "pending": pending or 0,
            "approved": approved or 0,
            "rejected": rejected or 0,
        }


leave_service = LeaveService(Leave)
