"""Bonus Service

Service layer for bonus management operations.
"""

from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.hr.bonus import Bonus, BonusType, PaymentStatus
from app.schemas.hr.bonus import BonusCreate, BonusUpdate
from app.services.base import CRUDBase


class BonusService(CRUDBase[Bonus, BonusCreate, BonusUpdate]):
    """Service for bonus management operations"""

    def get_by_courier(
        self,
        db: Session,
        *,
        courier_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Bonus]:
        """
        Get all bonuses for a specific courier

        Args:
            db: Database session
            courier_id: ID of the courier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of bonus records
        """
        return (
            db.query(self.model)
            .filter(self.model.courier_id == courier_id)
            .order_by(self.model.bonus_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_type(
        self,
        db: Session,
        *,
        bonus_type: BonusType,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Bonus]:
        """
        Get all bonuses of a specific type

        Args:
            db: Database session
            bonus_type: Type of bonus
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of bonus records
        """
        return (
            db.query(self.model)
            .filter(self.model.bonus_type == bonus_type)
            .order_by(self.model.bonus_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(
        self,
        db: Session,
        *,
        payment_status: PaymentStatus,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Bonus]:
        """
        Get all bonuses with a specific payment status

        Args:
            db: Database session
            payment_status: Payment status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of bonus records
        """
        return (
            db.query(self.model)
            .filter(self.model.payment_status == payment_status)
            .order_by(self.model.bonus_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_date_range(
        self,
        db: Session,
        *,
        start_date: date,
        end_date: date,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Bonus]:
        """
        Get all bonuses within a date range

        Args:
            db: Database session
            start_date: Start date
            end_date: End date
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of bonus records
        """
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.bonus_date >= start_date,
                    self.model.bonus_date <= end_date,
                )
            )
            .order_by(self.model.bonus_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def approve_bonus(
        self,
        db: Session,
        *,
        bonus_id: int,
        approved_by: int,
        approval_date: Optional[date] = None,
    ) -> Optional[Bonus]:
        """
        Approve a bonus

        Args:
            db: Database session
            bonus_id: ID of the bonus to approve
            approved_by: User ID who is approving
            approval_date: Date of approval (defaults to today)

        Returns:
            Updated bonus record or None if not found
        """
        bonus = self.get(db, bonus_id)
        if not bonus:
            return None

        bonus.payment_status = PaymentStatus.APPROVED
        bonus.approved_by = approved_by
        bonus.approval_date = approval_date or date.today()

        db.commit()
        db.refresh(bonus)
        return bonus

    def mark_as_paid(
        self,
        db: Session,
        *,
        bonus_id: int,
    ) -> Optional[Bonus]:
        """
        Mark a bonus as paid

        Args:
            db: Database session
            bonus_id: ID of the bonus

        Returns:
            Updated bonus record or None if not found
        """
        bonus = self.get(db, bonus_id)
        if not bonus:
            return None

        bonus.payment_status = PaymentStatus.PAID

        db.commit()
        db.refresh(bonus)
        return bonus

    def get_courier_total_bonuses(
        self,
        db: Session,
        *,
        courier_id: int,
        year: Optional[int] = None,
    ) -> Decimal:
        """
        Get total bonus amount for a courier

        Args:
            db: Database session
            courier_id: ID of the courier
            year: Optional year to filter by

        Returns:
            Total bonus amount
        """
        query = db.query(self.model).filter(self.model.courier_id == courier_id)

        if year:
            from sqlalchemy import extract

            query = query.filter(extract("year", self.model.bonus_date) == year)

        bonuses = query.all()
        return sum(bonus.amount for bonus in bonuses) if bonuses else Decimal("0")

    def get_statistics(
        self,
        db: Session,
        *,
        year: Optional[int] = None,
        courier_id: Optional[int] = None,
    ) -> Dict:
        """
        Get bonus statistics

        Args:
            db: Database session
            year: Optional year to filter by
            courier_id: Optional courier ID to filter by

        Returns:
            Dictionary with bonus statistics
        """
        query = db.query(self.model)

        if year:
            from sqlalchemy import extract

            query = query.filter(extract("year", self.model.bonus_date) == year)

        if courier_id:
            query = query.filter(self.model.courier_id == courier_id)

        bonuses = query.all()

        total_records = len(bonuses)
        total_amount = sum(bonus.amount for bonus in bonuses) if bonuses else Decimal("0")

        pending_count = sum(1 for b in bonuses if b.payment_status == PaymentStatus.PENDING)
        approved_count = sum(1 for b in bonuses if b.payment_status == PaymentStatus.APPROVED)
        paid_count = sum(1 for b in bonuses if b.payment_status == PaymentStatus.PAID)

        by_type = {}
        for bonus_type in BonusType:
            type_bonuses = [b for b in bonuses if b.bonus_type == bonus_type]
            by_type[bonus_type.value] = {
                "count": len(type_bonuses),
                "total": float(sum(b.amount for b in type_bonuses)) if type_bonuses else 0,
            }

        return {
            "total_records": total_records,
            "total_amount": float(total_amount),
            "pending_count": pending_count,
            "approved_count": approved_count,
            "paid_count": paid_count,
            "by_type": by_type,
            "average_amount": float(total_amount / total_records) if total_records > 0 else 0,
        }


bonus_service = BonusService(Bonus)
