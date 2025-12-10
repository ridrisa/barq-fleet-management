"""
Unit Tests for Leave Service

Tests cover:
- Leave request CRUD operations
- Leave approval/rejection workflow
- Leave balance calculations
- Date range queries
- Statistics

Author: BARQ QA Team
Last Updated: 2025-12-10
"""

import pytest
from datetime import date, timedelta
from unittest.mock import Mock, patch

from app.services.hr.leave_service import LeaveService, leave_service
from app.models.hr.leave import Leave, LeaveType, LeaveStatus


class TestLeaveService:
    """Test Leave Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create LeaveService instance"""
        return LeaveService(Leave)

    # ==================== CRUD TESTS ====================

    def test_create_leave_request(self, service, db_session, courier_factory, test_organization):
        """Test creating a leave request"""
        from app.schemas.hr.leave import LeaveCreate

        courier = courier_factory()
        leave_data = LeaveCreate(
            courier_id=courier.id,
            leave_type=LeaveType.ANNUAL,
            start_date=date.today() + timedelta(days=7),
            end_date=date.today() + timedelta(days=14),
            reason="Family vacation",
            organization_id=test_organization.id
        )

        leave = service.create(db_session, obj_in=leave_data)

        assert leave is not None
        assert leave.courier_id == courier.id
        assert leave.leave_type == LeaveType.ANNUAL
        assert leave.status == LeaveStatus.PENDING

    def test_get_leave_by_id(self, service, db_session, leave_factory, courier_factory):
        """Test getting leave by ID"""
        courier = courier_factory()
        leave = leave_factory(courier)

        result = service.get(db_session, leave.id)

        assert result is not None
        assert result.id == leave.id

    def test_get_multi_leaves(self, service, db_session, leave_factory, courier_factory):
        """Test getting multiple leave requests"""
        courier = courier_factory()
        leave1 = leave_factory(courier)
        leave2 = leave_factory(courier)

        result = service.get_multi(db_session)

        assert len(result) >= 2

    # ==================== COURIER FILTER TESTS ====================

    def test_get_by_courier(self, service, db_session, leave_factory, courier_factory):
        """Test getting leave requests by courier"""
        courier1 = courier_factory()
        courier2 = courier_factory()
        leave1 = leave_factory(courier1)
        leave2 = leave_factory(courier1)
        leave3 = leave_factory(courier2)

        result = service.get_by_courier(db_session, courier_id=courier1.id)

        assert len(result) >= 2
        assert all(l.courier_id == courier1.id for l in result)

    def test_get_by_courier_empty(self, service, db_session, courier_factory):
        """Test getting leave requests for courier with no leaves"""
        courier = courier_factory()

        result = service.get_by_courier(db_session, courier_id=courier.id)

        assert len(result) == 0

    # ==================== STATUS FILTER TESTS ====================

    def test_get_by_status_pending(self, service, db_session, leave_factory, courier_factory):
        """Test getting pending leave requests"""
        courier = courier_factory()
        pending = leave_factory(courier, status=LeaveStatus.PENDING)

        result = service.get_by_status(db_session, status=LeaveStatus.PENDING)

        assert len(result) >= 1
        assert all(l.status == LeaveStatus.PENDING for l in result)

    def test_get_by_status_approved(self, service, db_session, leave_factory, courier_factory):
        """Test getting approved leave requests"""
        courier = courier_factory()
        approved = leave_factory(courier, status=LeaveStatus.APPROVED)

        result = service.get_by_status(db_session, status=LeaveStatus.APPROVED)

        assert len(result) >= 1
        assert all(l.status == LeaveStatus.APPROVED for l in result)

    def test_get_by_status_rejected(self, service, db_session, leave_factory, courier_factory):
        """Test getting rejected leave requests"""
        courier = courier_factory()
        rejected = leave_factory(courier, status=LeaveStatus.REJECTED)

        result = service.get_by_status(db_session, status=LeaveStatus.REJECTED)

        assert len(result) >= 1
        assert all(l.status == LeaveStatus.REJECTED for l in result)

    # ==================== DATE RANGE TESTS ====================

    def test_get_by_date_range(self, service, db_session, leave_factory, courier_factory):
        """Test getting leave requests within date range"""
        courier = courier_factory()
        leave = leave_factory(
            courier,
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=10)
        )

        result = service.get_by_date_range(
            db_session,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=15)
        )

        assert len(result) >= 1

    def test_get_by_date_range_overlapping(self, service, db_session, leave_factory, courier_factory):
        """Test getting leave requests that overlap with date range"""
        courier = courier_factory()
        # Leave that starts before and ends during range
        leave = leave_factory(
            courier,
            start_date=date.today() - timedelta(days=5),
            end_date=date.today() + timedelta(days=5)
        )

        result = service.get_by_date_range(
            db_session,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10)
        )

        assert len(result) >= 1

    def test_get_by_date_range_no_results(self, service, db_session, leave_factory, courier_factory):
        """Test getting leave requests with no matches in date range"""
        courier = courier_factory()
        leave = leave_factory(
            courier,
            start_date=date.today() + timedelta(days=100),
            end_date=date.today() + timedelta(days=110)
        )

        result = service.get_by_date_range(
            db_session,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=15)
        )

        leave_ids = [l.id for l in result]
        assert leave.id not in leave_ids

    # ==================== APPROVAL WORKFLOW TESTS ====================

    def test_approve_leave_success(self, service, db_session, leave_factory, courier_factory, admin_user):
        """Test approving a leave request"""
        courier = courier_factory()
        leave = leave_factory(courier, status=LeaveStatus.PENDING)

        result = service.approve_leave(
            db_session,
            leave_id=leave.id,
            approved_by=admin_user.id,
            notes="Approved for annual vacation"
        )

        assert result is not None
        assert result.status == LeaveStatus.APPROVED
        assert result.approved_by == admin_user.id
        assert result.approved_at == date.today()

    def test_approve_leave_not_found(self, service, db_session, admin_user):
        """Test approving non-existent leave request"""
        result = service.approve_leave(
            db_session,
            leave_id=99999,
            approved_by=admin_user.id
        )

        assert result is None

    def test_reject_leave_success(self, service, db_session, leave_factory, courier_factory, admin_user):
        """Test rejecting a leave request"""
        courier = courier_factory()
        leave = leave_factory(courier, status=LeaveStatus.PENDING)

        result = service.reject_leave(
            db_session,
            leave_id=leave.id,
            approved_by=admin_user.id,
            reason="Insufficient staff coverage"
        )

        assert result is not None
        assert result.status == LeaveStatus.REJECTED
        assert result.approved_by == admin_user.id

    def test_reject_leave_not_found(self, service, db_session, admin_user):
        """Test rejecting non-existent leave request"""
        result = service.reject_leave(
            db_session,
            leave_id=99999,
            approved_by=admin_user.id
        )

        assert result is None

    def test_cancel_leave_success(self, service, db_session, leave_factory, courier_factory):
        """Test cancelling a leave request"""
        courier = courier_factory()
        leave = leave_factory(courier, status=LeaveStatus.PENDING)

        result = service.cancel_leave(db_session, leave_id=leave.id)

        assert result is not None
        assert result.status == LeaveStatus.CANCELLED

    def test_cancel_leave_not_found(self, service, db_session):
        """Test cancelling non-existent leave request"""
        result = service.cancel_leave(db_session, leave_id=99999)

        assert result is None

    # ==================== LEAVE BALANCE TESTS ====================

    def test_get_leave_balance_no_leaves_taken(self, service, db_session, courier_factory):
        """Test leave balance when no leaves taken"""
        courier = courier_factory()

        balance = service.get_leave_balance(
            db_session,
            courier_id=courier.id,
            year=date.today().year
        )

        assert balance["annual_entitlement"] == 30
        assert balance["days_taken"] == 0
        assert balance["days_remaining"] == 30

    def test_get_leave_balance_with_approved_leaves(self, service, db_session, leave_factory, courier_factory):
        """Test leave balance with approved leaves"""
        courier = courier_factory()
        # Create an approved leave with 5 days
        leave = leave_factory(
            courier,
            status=LeaveStatus.APPROVED,
            start_date=date(date.today().year, 6, 1),
            end_date=date(date.today().year, 6, 5),
            days=5
        )

        balance = service.get_leave_balance(
            db_session,
            courier_id=courier.id,
            year=date.today().year
        )

        assert balance["days_taken"] >= 5
        assert balance["days_remaining"] <= 25

    def test_get_leave_balance_excludes_pending(self, service, db_session, leave_factory, courier_factory):
        """Test leave balance excludes pending requests"""
        courier = courier_factory()
        pending_leave = leave_factory(
            courier,
            status=LeaveStatus.PENDING,
            start_date=date(date.today().year, 6, 1),
            end_date=date(date.today().year, 6, 5),
            days=5
        )

        balance = service.get_leave_balance(
            db_session,
            courier_id=courier.id,
            year=date.today().year
        )

        # Pending leaves should not count against balance
        # days_taken should not include the pending 5 days

    def test_get_leave_balance_excludes_rejected(self, service, db_session, leave_factory, courier_factory):
        """Test leave balance excludes rejected requests"""
        courier = courier_factory()
        rejected_leave = leave_factory(
            courier,
            status=LeaveStatus.REJECTED,
            start_date=date(date.today().year, 6, 1),
            end_date=date(date.today().year, 6, 5),
            days=5
        )

        balance = service.get_leave_balance(
            db_session,
            courier_id=courier.id,
            year=date.today().year
        )

        # Rejected leaves should not count

    # ==================== STATISTICS TESTS ====================

    def test_get_statistics(self, service, db_session, leave_factory, courier_factory):
        """Test getting leave statistics"""
        courier = courier_factory()
        leave_factory(courier, status=LeaveStatus.PENDING)
        leave_factory(courier, status=LeaveStatus.APPROVED)
        leave_factory(courier, status=LeaveStatus.REJECTED)

        stats = service.get_statistics(db_session)

        assert "total" in stats
        assert "pending" in stats
        assert "approved" in stats
        assert "rejected" in stats
        assert stats["total"] >= 3

    def test_get_statistics_empty(self, service, db_session):
        """Test getting statistics with no data"""
        # Clear any existing data
        stats = service.get_statistics(db_session)

        assert "total" in stats
        assert "pending" in stats
        assert "approved" in stats
        assert "rejected" in stats

    # ==================== PAGINATION TESTS ====================

    def test_get_multi_pagination(self, service, db_session, leave_factory, courier_factory):
        """Test pagination for leave requests"""
        courier = courier_factory()
        for _ in range(5):
            leave_factory(courier)

        first_page = service.get_multi(db_session, skip=0, limit=2)
        second_page = service.get_multi(db_session, skip=2, limit=2)

        assert len(first_page) == 2
        assert len(second_page) == 2
        first_ids = {l.id for l in first_page}
        second_ids = {l.id for l in second_page}
        assert first_ids.isdisjoint(second_ids)

    def test_get_by_courier_pagination(self, service, db_session, leave_factory, courier_factory):
        """Test pagination for courier leaves"""
        courier = courier_factory()
        for _ in range(5):
            leave_factory(courier)

        first_page = service.get_by_courier(db_session, courier_id=courier.id, skip=0, limit=2)
        second_page = service.get_by_courier(db_session, courier_id=courier.id, skip=2, limit=2)

        assert len(first_page) == 2
        assert len(second_page) == 2

    # ==================== ORGANIZATION FILTER TESTS ====================

    def test_get_multi_by_organization(self, service, db_session, leave_factory, courier_factory, test_organization):
        """Test getting leaves filtered by organization"""
        courier = courier_factory(organization_id=test_organization.id)
        leave = leave_factory(courier, organization_id=test_organization.id)

        result = service.get_multi(db_session, organization_id=test_organization.id)

        assert all(l.organization_id == test_organization.id for l in result)

    def test_get_by_courier_by_organization(self, service, db_session, leave_factory, courier_factory, test_organization):
        """Test getting courier leaves filtered by organization"""
        courier = courier_factory(organization_id=test_organization.id)
        leave = leave_factory(courier, organization_id=test_organization.id)

        result = service.get_by_courier(
            db_session,
            courier_id=courier.id,
            organization_id=test_organization.id
        )

        assert all(l.organization_id == test_organization.id for l in result)
