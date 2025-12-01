"""Payroll Processing Engine Service

Automated payroll processing system that:
- Calculates monthly salaries for all employees/couriers
- Applies attendance-based bonuses and deductions
- Applies loan deductions
- Calculates GOSI contributions
- Generates salary records
- Provides payroll reports
"""
from decimal import Decimal
from datetime import date, datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.fleet.courier import Courier, CourierStatus
from app.models.hr.attendance import Attendance, AttendanceStatus
from app.models.hr.loan import Loan, LoanStatus
from app.models.hr.salary import Salary
from app.services.hr.gosi_calculator_service import gosi_calculator_service
from app.services.hr.salary_service import salary_service
from app.services.hr.attendance_service import attendance_service
from app.services.hr.loan_service import loan_service


class PayrollResult:
    """Result of payroll processing for a single employee"""

    def __init__(
        self,
        courier_id: int,
        courier_name: str,
        month: int,
        year: int
    ):
        self.courier_id = courier_id
        self.courier_name = courier_name
        self.month = month
        self.year = year
        self.base_salary = Decimal("0")
        self.attendance_bonus = Decimal("0")
        self.attendance_deduction = Decimal("0")
        self.loan_deduction = Decimal("0")
        self.gosi_employee = Decimal("0")
        self.gosi_employer = Decimal("0")
        self.other_allowances = Decimal("0")
        self.other_deductions = Decimal("0")
        self.gross_salary = Decimal("0")
        self.total_deductions = Decimal("0")
        self.net_salary = Decimal("0")
        self.errors = []
        self.warnings = []
        self.success = False

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "courier_id": self.courier_id,
            "courier_name": self.courier_name,
            "month": self.month,
            "year": self.year,
            "base_salary": float(self.base_salary),
            "attendance_bonus": float(self.attendance_bonus),
            "attendance_deduction": float(self.attendance_deduction),
            "loan_deduction": float(self.loan_deduction),
            "gosi_employee": float(self.gosi_employee),
            "gosi_employer": float(self.gosi_employer),
            "other_allowances": float(self.other_allowances),
            "other_deductions": float(self.other_deductions),
            "gross_salary": float(self.gross_salary),
            "total_deductions": float(self.total_deductions),
            "net_salary": float(self.net_salary),
            "errors": self.errors,
            "warnings": self.warnings,
            "success": self.success
        }


class PayrollEngineService:
    """
    Automated payroll processing engine that handles monthly salary calculations
    for all employees/couriers with attendance, loans, and GOSI integration.
    """

    # Configuration
    PERFECT_ATTENDANCE_BONUS = Decimal("200")  # Bonus for perfect attendance
    ABSENCE_DEDUCTION_PER_DAY = Decimal("100")  # Deduction per absence
    LATE_DEDUCTION_PER_INSTANCE = Decimal("50")  # Deduction per late arrival

    def __init__(self):
        self.gosi_calculator = gosi_calculator_service

    def process_monthly_payroll(
        self,
        db: Session,
        month: int,
        year: int,
        courier_ids: Optional[List[int]] = None,
        dry_run: bool = False
    ) -> Dict:
        """
        Process monthly payroll for all active couriers

        Args:
            db: Database session
            month: Month to process (1-12)
            year: Year to process
            courier_ids: Optional list of specific courier IDs to process
            dry_run: If True, calculate but don't save to database

        Returns:
            Dictionary with processing summary and results
        """
        # Validate month and year
        if not (1 <= month <= 12):
            raise ValueError("Month must be between 1 and 12")
        if year < 2020 or year > 2100:
            raise ValueError("Invalid year")

        # Get active couriers
        query = db.query(Courier).filter(Courier.status == CourierStatus.ACTIVE)
        if courier_ids:
            query = query.filter(Courier.id.in_(courier_ids))

        couriers = query.all()

        results = []
        successful = 0
        failed = 0
        total_payroll = Decimal("0")

        for courier in couriers:
            try:
                result = self._process_courier_payroll(
                    db=db,
                    courier=courier,
                    month=month,
                    year=year,
                    dry_run=dry_run
                )
                results.append(result)

                if result.success:
                    successful += 1
                    total_payroll += result.net_salary
                else:
                    failed += 1

            except Exception as e:
                failed += 1
                error_result = PayrollResult(
                    courier_id=courier.id,
                    courier_name=courier.name,
                    month=month,
                    year=year
                )
                error_result.errors.append(f"Unexpected error: {str(e)}")
                results.append(error_result)

        return {
            "month": month,
            "year": year,
            "total_couriers": len(couriers),
            "successful": successful,
            "failed": failed,
            "total_payroll_amount": float(total_payroll),
            "dry_run": dry_run,
            "results": [r.to_dict() for r in results]
        }

    def _process_courier_payroll(
        self,
        db: Session,
        courier: Courier,
        month: int,
        year: int,
        dry_run: bool = False
    ) -> PayrollResult:
        """
        Process payroll for a single courier

        Args:
            db: Database session
            courier: Courier object
            month: Month to process
            year: Year to process
            dry_run: If True, calculate but don't save

        Returns:
            PayrollResult object
        """
        result = PayrollResult(
            courier_id=courier.id,
            courier_name=courier.name,
            month=month,
            year=year
        )

        # Get base salary (assuming courier has a base_salary field or from contract)
        # For now, using a default - in production, fetch from courier contract/record
        result.base_salary = getattr(courier, 'base_salary', Decimal("5000"))

        if result.base_salary <= 0:
            result.errors.append("Base salary not configured or invalid")
            return result

        # Calculate attendance bonuses and deductions
        attendance_data = self._calculate_attendance_adjustments(
            db, courier.id, month, year
        )
        result.attendance_bonus = attendance_data["bonus"]
        result.attendance_deduction = attendance_data["deduction"]
        if attendance_data["warnings"]:
            result.warnings.extend(attendance_data["warnings"])

        # Calculate loan deductions
        loan_data = self._calculate_loan_deduction(db, courier.id, month, year)
        result.loan_deduction = loan_data["deduction"]
        if loan_data["warnings"]:
            result.warnings.extend(loan_data["warnings"])

        # Calculate GOSI contributions
        gosi_result = self.gosi_calculator.calculate(result.base_salary)
        result.gosi_employee = gosi_result.employee_contribution
        result.gosi_employer = gosi_result.employer_contribution

        # Calculate gross and net salary
        result.gross_salary = (
            result.base_salary +
            result.attendance_bonus +
            result.other_allowances
        )

        result.total_deductions = (
            result.attendance_deduction +
            result.loan_deduction +
            result.gosi_employee +
            result.other_deductions
        )

        result.net_salary = result.gross_salary - result.total_deductions

        # Save to database if not dry run
        if not dry_run:
            try:
                salary_service.calculate_salary(
                    db,
                    courier_id=courier.id,
                    month=month,
                    year=year,
                    base_salary=result.base_salary,
                    allowances=result.attendance_bonus + result.other_allowances,
                    deductions=result.attendance_deduction + result.other_deductions,
                    loan_deduction=result.loan_deduction,
                    gosi_employee=result.gosi_employee
                )
                result.success = True
            except Exception as e:
                result.errors.append(f"Failed to save salary record: {str(e)}")
        else:
            result.success = True

        return result

    def _calculate_attendance_adjustments(
        self,
        db: Session,
        courier_id: int,
        month: int,
        year: int
    ) -> Dict:
        """
        Calculate attendance-based bonuses and deductions

        Args:
            db: Database session
            courier_id: Courier ID
            month: Month
            year: Year

        Returns:
            Dictionary with bonus, deduction, and warnings
        """
        bonus = Decimal("0")
        deduction = Decimal("0")
        warnings = []

        # Get attendance records for the month
        attendances = attendance_service.get_by_month(
            db, courier_id=courier_id, month=month, year=year
        )

        if not attendances:
            warnings.append("No attendance records found for this month")
            return {"bonus": bonus, "deduction": deduction, "warnings": warnings}

        # Count statuses
        present_count = sum(1 for a in attendances if a.status == AttendanceStatus.PRESENT)
        absent_count = sum(1 for a in attendances if a.status == AttendanceStatus.ABSENT)
        late_count = sum(1 for a in attendances if a.status == AttendanceStatus.LATE)

        # Perfect attendance bonus
        if absent_count == 0 and late_count == 0 and present_count >= 20:
            bonus = self.PERFECT_ATTENDANCE_BONUS

        # Absence deductions
        if absent_count > 0:
            deduction += self.ABSENCE_DEDUCTION_PER_DAY * absent_count
            warnings.append(f"{absent_count} absence(s) detected")

        # Late deductions
        if late_count > 0:
            deduction += self.LATE_DEDUCTION_PER_INSTANCE * late_count
            warnings.append(f"{late_count} late arrival(s) detected")

        return {
            "bonus": bonus,
            "deduction": deduction,
            "warnings": warnings,
            "stats": {
                "present": present_count,
                "absent": absent_count,
                "late": late_count
            }
        }

    def _calculate_loan_deduction(
        self,
        db: Session,
        courier_id: int,
        month: int,
        year: int
    ) -> Dict:
        """
        Calculate loan deduction for the month

        Args:
            db: Database session
            courier_id: Courier ID
            month: Month
            year: Year

        Returns:
            Dictionary with deduction and warnings
        """
        deduction = Decimal("0")
        warnings = []

        # Get active loans for the courier
        active_loans = loan_service.get_active_loans(db, courier_id=courier_id)

        if not active_loans:
            return {"deduction": deduction, "warnings": warnings}

        # Sum monthly deductions from all active loans
        for loan in active_loans:
            deduction += loan.monthly_deduction

        if len(active_loans) > 1:
            warnings.append(f"Multiple active loans ({len(active_loans)}) - total deduction: {float(deduction)}")

        return {
            "deduction": deduction,
            "warnings": warnings,
            "loans_count": len(active_loans)
        }

    def get_payroll_report(
        self,
        db: Session,
        month: int,
        year: int
    ) -> Dict:
        """
        Get comprehensive payroll report for a month

        Args:
            db: Database session
            month: Month
            year: Year

        Returns:
            Dictionary with payroll report
        """
        # Get all salary records for the month
        salaries = salary_service.get_by_month(db, month=month, year=year)

        total_gross = sum(s.gross_salary for s in salaries)
        total_net = sum(s.net_salary for s in salaries)
        total_gosi_employee = sum(s.gosi_employee for s in salaries)
        total_gosi_employer = sum(
            self.gosi_calculator.calculate(s.base_salary).employer_contribution
            for s in salaries
        )
        total_deductions = sum(s.deductions + s.loan_deduction + s.gosi_employee for s in salaries)

        paid = sum(1 for s in salaries if s.payment_date)
        unpaid = len(salaries) - paid

        return {
            "month": month,
            "year": year,
            "total_employees": len(salaries),
            "paid": paid,
            "unpaid": unpaid,
            "total_gross_salary": float(total_gross),
            "total_net_salary": float(total_net),
            "total_deductions": float(total_deductions),
            "total_gosi_employee": float(total_gosi_employee),
            "total_gosi_employer": float(total_gosi_employer),
            "total_gosi_contributions": float(total_gosi_employee + total_gosi_employer),
            "company_cost": float(total_gross + total_gosi_employer),
        }


# Singleton instance
payroll_engine_service = PayrollEngineService()
