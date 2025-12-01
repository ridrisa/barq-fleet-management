"""Loan Service"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import date
from decimal import Decimal

from app.services.base import CRUDBase
from app.models.hr.loan import Loan, LoanStatus
from app.schemas.hr.loan import LoanCreate, LoanUpdate


class LoanService(CRUDBase[Loan, LoanCreate, LoanUpdate]):
    """Service for loan management operations"""

    def get_by_courier(
        self,
        db: Session,
        *,
        courier_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Loan]:
        """
        Get all loans for a courier

        Args:
            db: Database session
            courier_id: ID of the courier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of loan records
        """
        return (
            db.query(self.model)
            .filter(self.model.courier_id == courier_id)
            .order_by(self.model.start_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active_loans(
        self,
        db: Session,
        *,
        courier_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Loan]:
        """
        Get active loans, optionally filtered by courier

        Args:
            db: Database session
            courier_id: Optional courier ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of active loan records
        """
        query = db.query(self.model).filter(self.model.status == LoanStatus.ACTIVE)

        if courier_id:
            query = query.filter(self.model.courier_id == courier_id)

        return (
            query.order_by(self.model.start_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def make_payment(
        self,
        db: Session,
        *,
        loan_id: int,
        payment_amount: Decimal
    ) -> Optional[Loan]:
        """
        Process a payment towards a loan

        Args:
            db: Database session
            loan_id: ID of the loan
            payment_amount: Amount being paid

        Returns:
            Updated loan record or None if not found
        """
        loan = db.query(self.model).filter(self.model.id == loan_id).first()
        if not loan:
            return None

        # Update outstanding balance
        new_balance = loan.outstanding_balance - payment_amount

        if new_balance <= 0:
            # Loan is fully paid
            loan.outstanding_balance = Decimal("0")
            loan.status = LoanStatus.COMPLETED
            loan.end_date = date.today()
        else:
            loan.outstanding_balance = new_balance

        db.commit()
        db.refresh(loan)
        return loan

    def approve_loan(
        self,
        db: Session,
        *,
        loan_id: int,
        approved_by: int
    ) -> Optional[Loan]:
        """
        Approve a loan application

        Args:
            db: Database session
            loan_id: ID of the loan
            approved_by: ID of the user approving the loan

        Returns:
            Updated loan record or None if not found
        """
        loan = db.query(self.model).filter(self.model.id == loan_id).first()
        if not loan:
            return None

        loan.approved_by = approved_by
        loan.status = LoanStatus.ACTIVE

        # Set outstanding balance to the loan amount if not set
        if not loan.outstanding_balance or loan.outstanding_balance == 0:
            loan.outstanding_balance = loan.amount

        db.commit()
        db.refresh(loan)
        return loan

    def cancel_loan(
        self,
        db: Session,
        *,
        loan_id: int
    ) -> Optional[Loan]:
        """
        Cancel a loan

        Args:
            db: Database session
            loan_id: ID of the loan

        Returns:
            Updated loan record or None if not found
        """
        loan = db.query(self.model).filter(self.model.id == loan_id).first()
        if not loan:
            return None

        loan.status = LoanStatus.CANCELLED
        loan.end_date = date.today()

        db.commit()
        db.refresh(loan)
        return loan

    def get_statistics(
        self,
        db: Session,
        *,
        courier_id: Optional[int] = None
    ) -> Dict:
        """
        Get loan statistics, optionally filtered by courier

        Args:
            db: Database session
            courier_id: Optional courier ID to filter by

        Returns:
            Dictionary with loan statistics
        """
        query = db.query(self.model)

        if courier_id:
            query = query.filter(self.model.courier_id == courier_id)

        # Get all loans for calculations
        all_loans = query.all()

        # Calculate statistics
        total_loans = len(all_loans)
        active_loans = sum(1 for loan in all_loans if loan.status == LoanStatus.ACTIVE)
        completed_loans = sum(1 for loan in all_loans if loan.status == LoanStatus.COMPLETED)
        cancelled_loans = sum(1 for loan in all_loans if loan.status == LoanStatus.CANCELLED)

        total_amount_disbursed = sum(loan.amount for loan in all_loans)
        total_outstanding = sum(
            loan.outstanding_balance for loan in all_loans
            if loan.status == LoanStatus.ACTIVE
        )
        total_repaid = total_amount_disbursed - total_outstanding

        return {
            "total_loans": total_loans,
            "active_loans": active_loans,
            "completed_loans": completed_loans,
            "cancelled_loans": cancelled_loans,
            "total_amount_disbursed": float(total_amount_disbursed),
            "total_outstanding_balance": float(total_outstanding),
            "total_amount_repaid": float(total_repaid),
            "repayment_rate": round(
                (float(total_repaid) / float(total_amount_disbursed) * 100), 2
            ) if total_amount_disbursed > 0 else 0
        }

    def get_monthly_deduction(
        self,
        db: Session,
        *,
        courier_id: int
    ) -> Decimal:
        """
        Get total monthly loan deduction for a courier

        Args:
            db: Database session
            courier_id: ID of the courier

        Returns:
            Total monthly deduction amount
        """
        active_loans = (
            db.query(self.model)
            .filter(
                and_(
                    self.model.courier_id == courier_id,
                    self.model.status == LoanStatus.ACTIVE
                )
            )
            .all()
        )

        total_deduction = sum(loan.monthly_deduction for loan in active_loans)
        return total_deduction


loan_service = LoanService(Loan)
