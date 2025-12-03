"""Attendance Service"""

from datetime import date, datetime, time, timedelta
from typing import Dict, List, Optional

from sqlalchemy import and_, extract, func
from sqlalchemy.orm import Session

from app.models.hr.attendance import Attendance, AttendanceStatus
from app.schemas.hr.attendance import AttendanceCreate, AttendanceUpdate
from app.services.base import CRUDBase


class AttendanceService(CRUDBase[Attendance, AttendanceCreate, AttendanceUpdate]):
    """Service for attendance management operations"""

    def get_by_courier(
        self,
        db: Session,
        *,
        courier_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Attendance]:
        """
        Get attendance records for a courier within optional date range

        Args:
            db: Database session
            courier_id: ID of the courier
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of attendance records
        """
        query = db.query(self.model).filter(self.model.courier_id == courier_id)

        if start_date:
            query = query.filter(self.model.date >= start_date)
        if end_date:
            query = query.filter(self.model.date <= end_date)

        return query.order_by(self.model.date.desc()).offset(skip).limit(limit).all()

    def get_by_date_range(
        self, db: Session, *, start_date: date, end_date: date, skip: int = 0, limit: int = 100
    ) -> List[Attendance]:
        """
        Get all attendance records within a date range

        Args:
            db: Database session
            start_date: Start date for filtering
            end_date: End date for filtering
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of attendance records
        """
        return (
            db.query(self.model)
            .filter(and_(self.model.date >= start_date, self.model.date <= end_date))
            .order_by(self.model.date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def check_in(
        self,
        db: Session,
        *,
        courier_id: int,
        check_in_time: time,
        attendance_date: Optional[date] = None,
    ) -> Attendance:
        """
        Record check-in for a courier

        Args:
            db: Database session
            courier_id: ID of the courier
            check_in_time: Check-in time
            attendance_date: Date of attendance (defaults to today)

        Returns:
            Created or updated attendance record
        """
        if attendance_date is None:
            attendance_date = date.today()

        # Check if attendance record exists for this date
        existing = (
            db.query(self.model)
            .filter(and_(self.model.courier_id == courier_id, self.model.date == attendance_date))
            .first()
        )

        if existing:
            existing.check_in = check_in_time
            existing.status = AttendanceStatus.PRESENT
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new attendance record
            attendance_data = AttendanceCreate(
                courier_id=courier_id,
                date=attendance_date,
                check_in=check_in_time,
                status=AttendanceStatus.PRESENT,
            )
            return self.create(db, obj_in=attendance_data)

    def check_out(
        self, db: Session, *, attendance_id: int, check_out_time: time
    ) -> Optional[Attendance]:
        """
        Record check-out for an attendance record

        Args:
            db: Database session
            attendance_id: ID of the attendance record
            check_out_time: Check-out time

        Returns:
            Updated attendance record or None if not found
        """
        attendance = db.query(self.model).filter(self.model.id == attendance_id).first()
        if not attendance:
            return None

        attendance.check_out = check_out_time

        # Calculate hours worked if both check_in and check_out are present
        if attendance.check_in:
            attendance.hours_worked = self._calculate_hours(attendance.check_in, check_out_time)

        db.commit()
        db.refresh(attendance)
        return attendance

    def calculate_hours(self, db: Session, *, attendance_id: int) -> Optional[Attendance]:
        """
        Calculate hours worked for an attendance record

        Args:
            db: Database session
            attendance_id: ID of the attendance record

        Returns:
            Updated attendance record or None if not found
        """
        attendance = db.query(self.model).filter(self.model.id == attendance_id).first()
        if not attendance or not attendance.check_in or not attendance.check_out:
            return None

        attendance.hours_worked = self._calculate_hours(attendance.check_in, attendance.check_out)

        db.commit()
        db.refresh(attendance)
        return attendance

    def get_statistics(
        self,
        db: Session,
        *,
        courier_id: Optional[int] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
    ) -> Dict:
        """
        Get attendance statistics for a courier or overall

        Args:
            db: Database session
            courier_id: Optional courier ID to filter by
            month: Optional month to filter by (1-12)
            year: Optional year to filter by

        Returns:
            Dictionary with attendance statistics
        """
        query = db.query(self.model)

        # Apply filters
        if courier_id:
            query = query.filter(self.model.courier_id == courier_id)
        if month and year:
            query = query.filter(
                and_(
                    extract("month", self.model.date) == month,
                    extract("year", self.model.date) == year,
                )
            )
        elif year:
            query = query.filter(extract("year", self.model.date) == year)

        # Get all records for calculations
        records = query.all()

        # Calculate statistics
        total_days = len(records)
        present_days = sum(1 for r in records if r.status == AttendanceStatus.PRESENT)
        absent_days = sum(1 for r in records if r.status == AttendanceStatus.ABSENT)
        late_days = sum(1 for r in records if r.status == AttendanceStatus.LATE)
        half_days = sum(1 for r in records if r.status == AttendanceStatus.HALF_DAY)
        on_leave_days = sum(1 for r in records if r.status == AttendanceStatus.ON_LEAVE)
        total_hours = sum(r.hours_worked for r in records if r.hours_worked)

        return {
            "total_days": total_days,
            "present_days": present_days,
            "absent_days": absent_days,
            "late_days": late_days,
            "half_days": half_days,
            "on_leave_days": on_leave_days,
            "total_hours_worked": total_hours,
            "average_hours_per_day": round(total_hours / total_days, 2) if total_days > 0 else 0,
            "attendance_rate": round((present_days / total_days * 100), 2) if total_days > 0 else 0,
        }

    def _calculate_hours(self, check_in: time, check_out: time) -> int:
        """
        Calculate hours worked between check-in and check-out times

        Args:
            check_in: Check-in time
            check_out: Check-out time

        Returns:
            Hours worked (rounded to nearest hour)
        """
        # Convert time to datetime for calculation
        today = date.today()
        check_in_dt = datetime.combine(today, check_in)
        check_out_dt = datetime.combine(today, check_out)

        # Handle overnight shifts
        if check_out_dt < check_in_dt:
            check_out_dt += timedelta(days=1)

        # Calculate hours
        time_diff = check_out_dt - check_in_dt
        hours = time_diff.total_seconds() / 3600

        return round(hours)


attendance_service = AttendanceService(Attendance)
