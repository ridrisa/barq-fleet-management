"""
Unit Tests for Attendance Service

Tests cover:
- Attendance record CRUD operations
- Check-in/check-out tracking
- Late arrival detection
- Statistics and reports

Author: BARQ QA Team
Last Updated: 2025-12-10
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch

from app.services.hr.attendance_service import AttendanceService
from app.models.hr.attendance import Attendance, AttendanceStatus


class TestAttendanceService:
    """Test Attendance Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create AttendanceService instance"""
        return AttendanceService(Attendance)

    # ==================== CHECK-IN TESTS ====================

    def test_check_in_success(self, service, db_session, courier_factory, test_organization):
        """Test successful check-in"""
        courier = courier_factory()
        check_in_time = datetime.now().replace(hour=8, minute=0)

        result = service.check_in(
            db_session,
            courier_id=courier.id,
            check_in_time=check_in_time,
            organization_id=test_organization.id
        )

        assert result is not None
        assert result.courier_id == courier.id
        assert result.check_in_time is not None
        assert result.status == AttendanceStatus.PRESENT

    def test_check_in_late(self, service, db_session, courier_factory, test_organization):
        """Test check-in marked as late"""
        courier = courier_factory()
        # Check in at 9:30 when expected at 8:00
        check_in_time = datetime.now().replace(hour=9, minute=30)

        result = service.check_in(
            db_session,
            courier_id=courier.id,
            check_in_time=check_in_time,
            expected_time=datetime.now().replace(hour=8, minute=0),
            organization_id=test_organization.id
        )

        assert result is not None
        assert result.status == AttendanceStatus.LATE

    def test_check_in_duplicate_same_day(self, service, db_session, courier_factory, test_organization):
        """Test duplicate check-in on same day"""
        courier = courier_factory()
        today = date.today()

        # First check-in
        first = service.check_in(
            db_session,
            courier_id=courier.id,
            check_in_time=datetime.now().replace(hour=8, minute=0),
            organization_id=test_organization.id
        )

        # Second check-in same day should update existing
        second = service.check_in(
            db_session,
            courier_id=courier.id,
            check_in_time=datetime.now().replace(hour=8, minute=30),
            organization_id=test_organization.id
        )

        # Should return existing record or update
        assert first.id == second.id or second is None

    # ==================== CHECK-OUT TESTS ====================

    def test_check_out_success(self, service, db_session, courier_factory, test_organization):
        """Test successful check-out"""
        courier = courier_factory()

        # First check-in
        service.check_in(
            db_session,
            courier_id=courier.id,
            check_in_time=datetime.now().replace(hour=8, minute=0),
            organization_id=test_organization.id
        )

        # Then check-out
        result = service.check_out(
            db_session,
            courier_id=courier.id,
            check_out_time=datetime.now().replace(hour=17, minute=0)
        )

        assert result is not None
        assert result.check_out_time is not None

    def test_check_out_early_departure(self, service, db_session, courier_factory, test_organization):
        """Test early departure check-out"""
        courier = courier_factory()

        service.check_in(
            db_session,
            courier_id=courier.id,
            check_in_time=datetime.now().replace(hour=8, minute=0),
            organization_id=test_organization.id
        )

        # Check out at 14:00 when expected at 17:00
        result = service.check_out(
            db_session,
            courier_id=courier.id,
            check_out_time=datetime.now().replace(hour=14, minute=0),
            expected_time=datetime.now().replace(hour=17, minute=0)
        )

        assert result is not None
        assert result.early_departure is True

    def test_check_out_without_check_in(self, service, db_session, courier_factory):
        """Test check-out without prior check-in"""
        courier = courier_factory()

        result = service.check_out(
            db_session,
            courier_id=courier.id,
            check_out_time=datetime.now().replace(hour=17, minute=0)
        )

        # Should return None or create special record
        # Depends on business logic

    # ==================== DATE RANGE QUERIES ====================

    def test_get_by_courier_and_date_range(self, service, db_session, courier_factory, test_organization):
        """Test getting attendance by courier and date range"""
        courier = courier_factory()

        # Create attendance records
        for i in range(5):
            service.check_in(
                db_session,
                courier_id=courier.id,
                check_in_time=(datetime.now() - timedelta(days=i)).replace(hour=8, minute=0),
                date=(date.today() - timedelta(days=i)),
                organization_id=test_organization.id
            )

        result = service.get_by_courier_and_date_range(
            db_session,
            courier_id=courier.id,
            start_date=date.today() - timedelta(days=10),
            end_date=date.today()
        )

        assert len(result) >= 5

    def test_get_by_date(self, service, db_session, courier_factory, test_organization):
        """Test getting all attendance for a specific date"""
        courier1 = courier_factory()
        courier2 = courier_factory()
        today = date.today()

        service.check_in(
            db_session,
            courier_id=courier1.id,
            check_in_time=datetime.now().replace(hour=8, minute=0),
            date=today,
            organization_id=test_organization.id
        )
        service.check_in(
            db_session,
            courier_id=courier2.id,
            check_in_time=datetime.now().replace(hour=8, minute=30),
            date=today,
            organization_id=test_organization.id
        )

        result = service.get_by_date(db_session, date=today)

        assert len(result) >= 2

    # ==================== STATUS QUERIES ====================

    def test_get_late_arrivals(self, service, db_session, courier_factory, test_organization):
        """Test getting late arrivals"""
        courier = courier_factory()

        # Create late attendance
        service.check_in(
            db_session,
            courier_id=courier.id,
            check_in_time=datetime.now().replace(hour=9, minute=30),
            expected_time=datetime.now().replace(hour=8, minute=0),
            organization_id=test_organization.id
        )

        result = service.get_late_arrivals(db_session, date=date.today())

        assert len(result) >= 1

    def test_get_absences(self, service, db_session, courier_factory, test_organization):
        """Test getting absences for a date"""
        courier = courier_factory()

        # Mark as absent
        attendance = Attendance(
            courier_id=courier.id,
            date=date.today(),
            status=AttendanceStatus.ABSENT,
            organization_id=test_organization.id
        )
        db_session.add(attendance)
        db_session.commit()

        result = service.get_absences(db_session, date=date.today())

        assert len(result) >= 1

    def test_get_on_leave(self, service, db_session, courier_factory, test_organization):
        """Test getting couriers on leave"""
        courier = courier_factory()

        attendance = Attendance(
            courier_id=courier.id,
            date=date.today(),
            status=AttendanceStatus.ON_LEAVE,
            organization_id=test_organization.id
        )
        db_session.add(attendance)
        db_session.commit()

        result = service.get_on_leave(db_session, date=date.today())

        assert len(result) >= 1

    # ==================== WORKING HOURS CALCULATION ====================

    def test_calculate_working_hours(self, service, db_session, courier_factory, test_organization):
        """Test calculating working hours"""
        courier = courier_factory()

        # Check in at 8:00
        service.check_in(
            db_session,
            courier_id=courier.id,
            check_in_time=datetime.now().replace(hour=8, minute=0),
            organization_id=test_organization.id
        )

        # Check out at 17:00
        service.check_out(
            db_session,
            courier_id=courier.id,
            check_out_time=datetime.now().replace(hour=17, minute=0)
        )

        hours = service.calculate_working_hours(
            db_session,
            courier_id=courier.id,
            date=date.today()
        )

        assert hours == 9.0  # 9 hours

    def test_calculate_working_hours_with_break(self, service, db_session, courier_factory, test_organization):
        """Test calculating working hours with break deduction"""
        courier = courier_factory()

        service.check_in(
            db_session,
            courier_id=courier.id,
            check_in_time=datetime.now().replace(hour=8, minute=0),
            organization_id=test_organization.id
        )

        service.check_out(
            db_session,
            courier_id=courier.id,
            check_out_time=datetime.now().replace(hour=17, minute=0)
        )

        hours = service.calculate_working_hours(
            db_session,
            courier_id=courier.id,
            date=date.today(),
            break_duration=1.0  # 1 hour break
        )

        assert hours == 8.0  # 9 hours - 1 hour break

    # ==================== STATISTICS TESTS ====================

    def test_get_daily_statistics(self, service, db_session, courier_factory, test_organization):
        """Test getting daily attendance statistics"""
        for i in range(5):
            courier = courier_factory()
            service.check_in(
                db_session,
                courier_id=courier.id,
                check_in_time=datetime.now().replace(hour=8, minute=0),
                organization_id=test_organization.id
            )

        stats = service.get_daily_statistics(db_session, date=date.today())

        assert "total_present" in stats
        assert "total_late" in stats
        assert "total_absent" in stats
        assert "total_on_leave" in stats

    def test_get_monthly_statistics(self, service, db_session, courier_factory, test_organization):
        """Test getting monthly attendance statistics for courier"""
        courier = courier_factory()

        # Create attendance for multiple days
        for i in range(10):
            attendance = Attendance(
                courier_id=courier.id,
                date=date.today() - timedelta(days=i),
                status=AttendanceStatus.PRESENT,
                check_in_time=datetime.now().replace(hour=8, minute=0),
                organization_id=test_organization.id
            )
            db_session.add(attendance)
        db_session.commit()

        stats = service.get_monthly_statistics(
            db_session,
            courier_id=courier.id,
            month=date.today().month,
            year=date.today().year
        )

        assert "total_days" in stats
        assert "days_present" in stats
        assert "days_late" in stats
        assert "days_absent" in stats

    def test_get_attendance_rate(self, service, db_session, courier_factory, test_organization):
        """Test getting attendance rate for courier"""
        courier = courier_factory()

        # 8 present, 2 absent out of 10 days
        for i in range(8):
            attendance = Attendance(
                courier_id=courier.id,
                date=date.today() - timedelta(days=i),
                status=AttendanceStatus.PRESENT,
                organization_id=test_organization.id
            )
            db_session.add(attendance)

        for i in range(8, 10):
            attendance = Attendance(
                courier_id=courier.id,
                date=date.today() - timedelta(days=i),
                status=AttendanceStatus.ABSENT,
                organization_id=test_organization.id
            )
            db_session.add(attendance)

        db_session.commit()

        rate = service.get_attendance_rate(
            db_session,
            courier_id=courier.id,
            start_date=date.today() - timedelta(days=10),
            end_date=date.today()
        )

        assert rate == 80.0  # 8 out of 10

    # ==================== BULK OPERATIONS ====================

    def test_mark_bulk_absent(self, service, db_session, courier_factory, test_organization):
        """Test marking multiple couriers as absent"""
        couriers = [courier_factory() for _ in range(3)]
        courier_ids = [c.id for c in couriers]

        result = service.mark_bulk_absent(
            db_session,
            courier_ids=courier_ids,
            date=date.today(),
            organization_id=test_organization.id
        )

        assert len(result) == 3
        assert all(a.status == AttendanceStatus.ABSENT for a in result)

    def test_generate_attendance_report(self, service, db_session, courier_factory, test_organization):
        """Test generating attendance report"""
        courier = courier_factory()

        for i in range(5):
            attendance = Attendance(
                courier_id=courier.id,
                date=date.today() - timedelta(days=i),
                status=AttendanceStatus.PRESENT,
                check_in_time=(datetime.now() - timedelta(days=i)).replace(hour=8, minute=0),
                check_out_time=(datetime.now() - timedelta(days=i)).replace(hour=17, minute=0),
                organization_id=test_organization.id
            )
            db_session.add(attendance)
        db_session.commit()

        report = service.generate_report(
            db_session,
            courier_id=courier.id,
            start_date=date.today() - timedelta(days=10),
            end_date=date.today()
        )

        assert "courier_id" in report
        assert "total_days" in report
        assert "attendance_rate" in report
        assert "total_hours" in report

    # ==================== ORGANIZATION FILTER TESTS ====================

    def test_get_by_date_filtered_by_organization(self, service, db_session, courier_factory, test_organization, second_organization):
        """Test getting attendance filtered by organization"""
        courier1 = courier_factory(organization_id=test_organization.id)
        courier2 = courier_factory(organization_id=second_organization.id)

        service.check_in(
            db_session,
            courier_id=courier1.id,
            check_in_time=datetime.now().replace(hour=8, minute=0),
            organization_id=test_organization.id
        )
        service.check_in(
            db_session,
            courier_id=courier2.id,
            check_in_time=datetime.now().replace(hour=8, minute=0),
            organization_id=second_organization.id
        )

        result = service.get_by_date(
            db_session,
            date=date.today(),
            organization_id=test_organization.id
        )

        assert all(a.organization_id == test_organization.id for a in result)

    # ==================== PAGINATION TESTS ====================

    def test_get_by_date_pagination(self, service, db_session, courier_factory, test_organization):
        """Test pagination for daily attendance"""
        for _ in range(5):
            courier = courier_factory()
            service.check_in(
                db_session,
                courier_id=courier.id,
                check_in_time=datetime.now().replace(hour=8, minute=0),
                organization_id=test_organization.id
            )

        first_page = service.get_by_date(db_session, date=date.today(), skip=0, limit=2)
        second_page = service.get_by_date(db_session, date=date.today(), skip=2, limit=2)

        assert len(first_page) == 2
        assert len(second_page) == 2
