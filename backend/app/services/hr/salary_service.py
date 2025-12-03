"""Salary Service"""

from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import and_, extract, func
from sqlalchemy.orm import Session

from app.models.hr.salary import Salary
from app.schemas.hr.salary import SalaryCreate, SalaryUpdate
from app.services.base import CRUDBase


class SalaryService(CRUDBase[Salary, SalaryCreate, SalaryUpdate]):
    """Service for salary management operations"""

    def get_by_courier(
        self,
        db: Session,
        *,
        courier_id: int,
        year: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Salary]:
        """
        Get salary records for a courier, optionally filtered by year

        Args:
            db: Database session
            courier_id: ID of the courier
            year: Optional year to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of salary records
        """
        query = db.query(self.model).filter(self.model.courier_id == courier_id)

        if year:
            query = query.filter(self.model.year == year)

        return (
            query.order_by(self.model.year.desc(), self.model.month.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_month(
        self, db: Session, *, month: int, year: int, skip: int = 0, limit: int = 100
    ) -> List[Salary]:
        """
        Get all salary records for a specific month and year

        Args:
            db: Database session
            month: Month (1-12)
            year: Year
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of salary records
        """
        return (
            db.query(self.model)
            .filter(and_(self.model.month == month, self.model.year == year))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_salary_for_period(
        self, db: Session, *, courier_id: int, month: int, year: int
    ) -> Optional[Salary]:
        """
        Get a specific salary record for a courier, month, and year

        Args:
            db: Database session
            courier_id: ID of the courier
            month: Month (1-12)
            year: Year

        Returns:
            Salary record or None if not found
        """
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.courier_id == courier_id,
                    self.model.month == month,
                    self.model.year == year,
                )
            )
            .first()
        )

    def calculate_salary(
        self,
        db: Session,
        *,
        courier_id: int,
        month: int,
        year: int,
        base_salary: Decimal,
        allowances: Decimal = Decimal("0"),
        deductions: Decimal = Decimal("0"),
        loan_deduction: Decimal = Decimal("0"),
        gosi_employee: Decimal = Decimal("0"),
    ) -> Salary:
        """
        Calculate and create/update salary for a courier for a specific month

        Args:
            db: Database session
            courier_id: ID of the courier
            month: Month (1-12)
            year: Year
            base_salary: Base salary amount
            allowances: Additional allowances
            deductions: General deductions
            loan_deduction: Loan repayment deduction
            gosi_employee: GOSI employee contribution

        Returns:
            Created or updated salary record
        """
        # Calculate gross and net salary
        gross_salary = base_salary + allowances
        total_deductions = deductions + loan_deduction + gosi_employee
        net_salary = gross_salary - total_deductions

        # Check if salary record already exists
        existing_salary = self.get_salary_for_period(
            db, courier_id=courier_id, month=month, year=year
        )

        if existing_salary:
            # Update existing record
            update_data = SalaryUpdate(
                base_salary=base_salary,
                allowances=allowances,
                deductions=deductions,
                loan_deduction=loan_deduction,
                gosi_employee=gosi_employee,
                gross_salary=gross_salary,
                net_salary=net_salary,
            )
            return self.update(db, db_obj=existing_salary, obj_in=update_data)
        else:
            # Create new record
            salary_data = SalaryCreate(
                courier_id=courier_id,
                month=month,
                year=year,
                base_salary=base_salary,
                allowances=allowances,
                deductions=deductions,
                loan_deduction=loan_deduction,
                gosi_employee=gosi_employee,
            )

            # Create the salary record
            salary = self.model(**salary_data.model_dump())
            salary.gross_salary = gross_salary
            salary.net_salary = net_salary

            db.add(salary)
            db.commit()
            db.refresh(salary)
            return salary

    def mark_as_paid(
        self, db: Session, *, salary_id: int, payment_date: Optional[date] = None
    ) -> Optional[Salary]:
        """
        Mark a salary as paid

        Args:
            db: Database session
            salary_id: ID of the salary record
            payment_date: Date of payment (defaults to today)

        Returns:
            Updated salary record or None if not found
        """
        salary = db.query(self.model).filter(self.model.id == salary_id).first()
        if not salary:
            return None

        salary.payment_date = payment_date or date.today()

        db.commit()
        db.refresh(salary)
        return salary

    def get_statistics(
        self, db: Session, *, year: Optional[int] = None, courier_id: Optional[int] = None
    ) -> Dict:
        """
        Get salary statistics for a year or overall

        Args:
            db: Database session
            year: Optional year to filter by
            courier_id: Optional courier ID to filter by

        Returns:
            Dictionary with salary statistics
        """
        query = db.query(self.model)

        if year:
            query = query.filter(self.model.year == year)
        if courier_id:
            query = query.filter(self.model.courier_id == courier_id)

        # Get all salaries for calculations
        salaries = query.all()

        # Calculate statistics
        total_records = len(salaries)
        total_gross_salary = sum(salary.gross_salary for salary in salaries)
        total_net_salary = sum(salary.net_salary for salary in salaries)
        total_deductions = sum(salary.deductions for salary in salaries)
        total_loan_deductions = sum(salary.loan_deduction for salary in salaries)
        total_gosi = sum(salary.gosi_employee for salary in salaries)
        total_allowances = sum(salary.allowances for salary in salaries)

        paid_salaries = sum(1 for salary in salaries if salary.payment_date)
        unpaid_salaries = total_records - paid_salaries

        return {
            "total_salary_records": total_records,
            "paid_salaries": paid_salaries,
            "unpaid_salaries": unpaid_salaries,
            "total_gross_salary": float(total_gross_salary),
            "total_net_salary": float(total_net_salary),
            "total_allowances": float(total_allowances),
            "total_deductions": float(total_deductions),
            "total_loan_deductions": float(total_loan_deductions),
            "total_gosi_contributions": float(total_gosi),
            "average_gross_salary": (
                float(total_gross_salary / total_records) if total_records > 0 else 0
            ),
            "average_net_salary": (
                float(total_net_salary / total_records) if total_records > 0 else 0
            ),
        }

    def get_annual_summary(self, db: Session, *, courier_id: int, year: int) -> Dict:
        """
        Get annual salary summary for a courier

        Args:
            db: Database session
            courier_id: ID of the courier
            year: Year to summarize

        Returns:
            Dictionary with annual summary
        """
        salaries = self.get_by_courier(db, courier_id=courier_id, year=year)

        total_gross = sum(salary.gross_salary for salary in salaries)
        total_net = sum(salary.net_salary for salary in salaries)
        total_deductions = sum(
            salary.deductions + salary.loan_deduction + salary.gosi_employee for salary in salaries
        )

        months_paid = len(salaries)

        return {
            "year": year,
            "courier_id": courier_id,
            "months_paid": months_paid,
            "total_gross_salary": float(total_gross),
            "total_net_salary": float(total_net),
            "total_deductions": float(total_deductions),
            "average_monthly_gross": float(total_gross / months_paid) if months_paid > 0 else 0,
            "average_monthly_net": float(total_net / months_paid) if months_paid > 0 else 0,
        }


salary_service = SalaryService(Salary)
