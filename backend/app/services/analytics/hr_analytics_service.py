"""HR Analytics Service

Provides analytics and insights for HR operations:
- Leave patterns and trends
- Attendance statistics
- Salary distribution
- Turnover rates
- Employee demographics
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, extract, func, or_
from sqlalchemy.orm import Session

from app.models.fleet.courier import Courier, CourierStatus
from app.models.hr.attendance import Attendance, AttendanceStatus
from app.models.hr.leave import Leave, LeaveStatus, LeaveType
from app.models.hr.loan import Loan, LoanStatus
from app.models.hr.salary import Salary


class HRAnalyticsService:
    """
    Service for HR analytics and reporting

    Provides insights into:
    - Leave patterns
    - Attendance trends
    - Salary analysis
    - Employee demographics
    - Turnover metrics
    """

    def get_leave_analytics(
        self, db: Session, start_date: date, end_date: date, leave_type: Optional[LeaveType] = None
    ) -> Dict[str, Any]:
        """
        Analyze leave patterns and trends

        Args:
            db: Database session
            start_date: Start date for analysis
            end_date: End date for analysis
            leave_type: Optional filter by leave type

        Returns:
            Dictionary with leave analytics
        """
        query = db.query(Leave).filter(
            and_(Leave.start_date >= start_date, Leave.end_date <= end_date)
        )

        if leave_type:
            query = query.filter(Leave.leave_type == leave_type)

        leaves = query.all()

        # Group by status
        by_status = {}
        for leave in leaves:
            status = leave.status.value
            if status not in by_status:
                by_status[status] = {"count": 0, "total_days": 0}

            by_status[status]["count"] += 1
            by_status[status]["total_days"] += leave.days

        # Group by type
        by_type = {}
        for leave in leaves:
            l_type = leave.leave_type.value
            if l_type not in by_type:
                by_type[l_type] = {"count": 0, "total_days": 0}

            by_type[l_type]["count"] += 1
            by_type[l_type]["total_days"] += leave.days

        # Calculate approval rate
        total_requests = len(leaves)
        approved = sum(1 for l in leaves if l.status == LeaveStatus.APPROVED)
        rejected = sum(1 for l in leaves if l.status == LeaveStatus.REJECTED)
        pending = sum(1 for l in leaves if l.status == LeaveStatus.PENDING)

        approval_rate = (approved / total_requests * 100) if total_requests > 0 else 0

        # Average days per leave
        total_days = sum(l.days for l in leaves)
        avg_days = total_days / total_requests if total_requests > 0 else 0

        return {
            "period": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
            "summary": {
                "total_requests": total_requests,
                "approved": approved,
                "rejected": rejected,
                "pending": pending,
                "approval_rate": round(approval_rate, 2),
                "total_days": total_days,
                "average_days_per_leave": round(avg_days, 2),
            },
            "by_status": by_status,
            "by_type": by_type,
        }

    def get_attendance_analytics(
        self, db: Session, month: int, year: int, courier_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyze attendance patterns for a month

        Args:
            db: Database session
            month: Month (1-12)
            year: Year
            courier_id: Optional filter by courier

        Returns:
            Dictionary with attendance analytics
        """
        query = db.query(Attendance).filter(
            and_(Attendance.month == month, Attendance.year == year)
        )

        if courier_id:
            query = query.filter(Attendance.courier_id == courier_id)

        attendances = query.all()

        # Group by status
        by_status = {}
        for attendance in attendances:
            status = attendance.status.value
            by_status[status] = by_status.get(status, 0) + 1

        # Calculate rates
        total_records = len(attendances)
        present = by_status.get(AttendanceStatus.PRESENT.value, 0)
        absent = by_status.get(AttendanceStatus.ABSENT.value, 0)
        late = by_status.get(AttendanceStatus.LATE.value, 0)

        presence_rate = (present / total_records * 100) if total_records > 0 else 0
        absence_rate = (absent / total_records * 100) if total_records > 0 else 0
        late_rate = (late / total_records * 100) if total_records > 0 else 0

        # Count perfect attendance (all present, no absent/late)
        if not courier_id:
            # Fleet-wide: count employees with perfect attendance
            courier_attendance = {}
            for attendance in attendances:
                cid = attendance.courier_id
                if cid not in courier_attendance:
                    courier_attendance[cid] = {"present": 0, "absent": 0, "late": 0}

                courier_attendance[cid][attendance.status.value] += 1

            perfect_attendance_count = sum(
                1
                for stats in courier_attendance.values()
                if stats["absent"] == 0 and stats["late"] == 0 and stats["present"] > 0
            )
        else:
            perfect_attendance_count = 1 if absent == 0 and late == 0 and present > 0 else 0

        return {
            "period": {"month": month, "year": year},
            "courier_id": courier_id,
            "summary": {
                "total_records": total_records,
                "present": present,
                "absent": absent,
                "late": late,
                "presence_rate": round(presence_rate, 2),
                "absence_rate": round(absence_rate, 2),
                "late_rate": round(late_rate, 2),
                "perfect_attendance_count": perfect_attendance_count,
            },
        }

    def get_salary_distribution(self, db: Session, month: int, year: int) -> Dict[str, Any]:
        """
        Analyze salary distribution

        Args:
            db: Database session
            month: Month
            year: Year

        Returns:
            Dictionary with salary distribution metrics
        """
        salaries = db.query(Salary).filter(and_(Salary.month == month, Salary.year == year)).all()

        if not salaries:
            return {
                "period": {"month": month, "year": year},
                "message": "No salary data available for this period",
            }

        # Calculate statistics
        base_salaries = [float(s.base_salary) for s in salaries]
        gross_salaries = [float(s.gross_salary) for s in salaries]
        net_salaries = [float(s.net_salary) for s in salaries]

        total_count = len(salaries)

        return {
            "period": {"month": month, "year": year},
            "employee_count": total_count,
            "base_salary": {
                "total": sum(base_salaries),
                "average": sum(base_salaries) / total_count,
                "min": min(base_salaries),
                "max": max(base_salaries),
                "median": sorted(base_salaries)[total_count // 2],
            },
            "gross_salary": {
                "total": sum(gross_salaries),
                "average": sum(gross_salaries) / total_count,
                "min": min(gross_salaries),
                "max": max(gross_salaries),
                "median": sorted(gross_salaries)[total_count // 2],
            },
            "net_salary": {
                "total": sum(net_salaries),
                "average": sum(net_salaries) / total_count,
                "min": min(net_salaries),
                "max": max(net_salaries),
                "median": sorted(net_salaries)[total_count // 2],
            },
            "deductions": {
                "total_gosi": sum(float(s.gosi_employee) for s in salaries),
                "total_loans": sum(float(s.loan_deduction) for s in salaries),
                "total_other": sum(float(s.deductions) for s in salaries),
            },
        }

    def get_employee_demographics(self, db: Session) -> Dict[str, Any]:
        """
        Get employee demographics overview

        Args:
            db: Database session

        Returns:
            Dictionary with demographic breakdown
        """
        # Total employees by status
        status_breakdown = (
            db.query(Courier.status, func.count(Courier.id)).group_by(Courier.status).all()
        )

        by_status = {}
        total_employees = 0
        for status, count in status_breakdown:
            by_status[status.value] = count
            total_employees += count

        # Active loans
        active_loans = (
            db.query(func.count(Loan.id)).filter(Loan.status == LoanStatus.ACTIVE).scalar()
        )

        # Employees with loans
        employees_with_loans = (
            db.query(func.count(func.distinct(Loan.courier_id)))
            .filter(Loan.status == LoanStatus.ACTIVE)
            .scalar()
        )

        return {
            "total_employees": total_employees,
            "by_status": by_status,
            "loans": {
                "active_loans": active_loans,
                "employees_with_loans": employees_with_loans,
                "loan_penetration_rate": round(
                    (employees_with_loans / total_employees * 100) if total_employees > 0 else 0, 2
                ),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_turnover_metrics(self, db: Session, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Calculate employee turnover metrics

        Args:
            db: Database session
            start_date: Start date for analysis
            end_date: End date for analysis

        Returns:
            Dictionary with turnover metrics
        """
        # Employees who left during the period (status changed to inactive/terminated)
        # Note: This requires tracking status changes, which would be in audit logs
        # For now, we'll use current inactive employees as a proxy

        total_employees_start = (
            db.query(func.count(Courier.id))
            .filter(Courier.created_at < datetime.combine(start_date, datetime.min.time()))
            .scalar()
        )

        total_employees_end = (
            db.query(func.count(Courier.id))
            .filter(Courier.created_at <= datetime.combine(end_date, datetime.max.time()))
            .scalar()
        )

        # New hires during period
        new_hires = (
            db.query(func.count(Courier.id))
            .filter(
                and_(
                    Courier.created_at >= datetime.combine(start_date, datetime.min.time()),
                    Courier.created_at <= datetime.combine(end_date, datetime.max.time()),
                )
            )
            .scalar()
        )

        # Inactive employees (proxy for terminations)
        terminated = (
            db.query(func.count(Courier.id))
            .filter(Courier.status == CourierStatus.INACTIVE)
            .scalar()
        )

        # Calculate turnover rate
        avg_employees = (total_employees_start + total_employees_end) / 2
        turnover_rate = (terminated / avg_employees * 100) if avg_employees > 0 else 0

        return {
            "period": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
            "employees_at_start": total_employees_start,
            "employees_at_end": total_employees_end,
            "new_hires": new_hires,
            "terminations": terminated,
            "turnover_rate": round(turnover_rate, 2),
            "net_change": total_employees_end - total_employees_start,
        }


# Singleton instance
hr_analytics_service = HRAnalyticsService()
