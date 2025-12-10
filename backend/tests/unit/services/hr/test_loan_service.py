"""
Unit Tests for Loan Service

Tests cover:
- Loan request CRUD operations
- Loan approval/rejection workflow
- Loan repayment tracking
- Statistics

Author: BARQ QA Team
Last Updated: 2025-12-10
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

from app.services.hr.loan_service import LoanService
from app.models.hr.loan import Loan, LoanStatus


class TestLoanService:
    """Test Loan Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create LoanService instance"""
        return LoanService(Loan)

    # ==================== CRUD TESTS ====================

    def test_create_loan_request(self, service, db_session, courier_factory, test_organization):
        """Test creating a loan request"""
        from app.schemas.hr.loan import LoanCreate

        courier = courier_factory()
        loan_data = LoanCreate(
            courier_id=courier.id,
            amount=Decimal("5000.00"),
            installment_amount=Decimal("500.00"),
            reason="Personal expenses",
            organization_id=test_organization.id
        )

        loan = service.create(db_session, obj_in=loan_data)

        assert loan is not None
        assert loan.courier_id == courier.id
        assert loan.amount == Decimal("5000.00")
        assert loan.status == LoanStatus.PENDING

    def test_get_loan_by_id(self, service, db_session, loan_factory, courier_factory):
        """Test getting loan by ID"""
        courier = courier_factory()
        loan = loan_factory(courier)

        result = service.get(db_session, loan.id)

        assert result is not None
        assert result.id == loan.id

    def test_get_multi_loans(self, service, db_session, loan_factory, courier_factory):
        """Test getting multiple loans"""
        courier = courier_factory()
        loan1 = loan_factory(courier)
        loan2 = loan_factory(courier)

        result = service.get_multi(db_session)

        assert len(result) >= 2

    # ==================== COURIER FILTER TESTS ====================

    def test_get_by_courier(self, service, db_session, loan_factory, courier_factory):
        """Test getting loans by courier"""
        courier1 = courier_factory()
        courier2 = courier_factory()
        loan1 = loan_factory(courier1)
        loan2 = loan_factory(courier1)
        loan3 = loan_factory(courier2)

        result = service.get_by_courier(db_session, courier_id=courier1.id)

        assert len(result) >= 2
        assert all(l.courier_id == courier1.id for l in result)

    def test_get_by_courier_empty(self, service, db_session, courier_factory):
        """Test getting loans for courier with no loans"""
        courier = courier_factory()

        result = service.get_by_courier(db_session, courier_id=courier.id)

        assert len(result) == 0

    # ==================== STATUS FILTER TESTS ====================

    def test_get_by_status_pending(self, service, db_session, loan_factory, courier_factory):
        """Test getting pending loans"""
        courier = courier_factory()
        pending = loan_factory(courier, status=LoanStatus.PENDING)

        result = service.get_by_status(db_session, status=LoanStatus.PENDING)

        assert len(result) >= 1
        assert all(l.status == LoanStatus.PENDING for l in result)

    def test_get_by_status_approved(self, service, db_session, loan_factory, courier_factory):
        """Test getting approved loans"""
        courier = courier_factory()
        approved = loan_factory(courier, status=LoanStatus.APPROVED)

        result = service.get_by_status(db_session, status=LoanStatus.APPROVED)

        assert len(result) >= 1
        assert all(l.status == LoanStatus.APPROVED for l in result)

    def test_get_by_status_active(self, service, db_session, loan_factory, courier_factory):
        """Test getting active loans"""
        courier = courier_factory()
        active = loan_factory(courier, status=LoanStatus.ACTIVE)

        result = service.get_by_status(db_session, status=LoanStatus.ACTIVE)

        assert len(result) >= 1
        assert all(l.status == LoanStatus.ACTIVE for l in result)

    def test_get_by_status_completed(self, service, db_session, loan_factory, courier_factory):
        """Test getting completed loans"""
        courier = courier_factory()
        completed = loan_factory(courier, status=LoanStatus.COMPLETED)

        result = service.get_by_status(db_session, status=LoanStatus.COMPLETED)

        assert len(result) >= 1
        assert all(l.status == LoanStatus.COMPLETED for l in result)

    # ==================== APPROVAL WORKFLOW TESTS ====================

    def test_approve_loan_success(self, service, db_session, loan_factory, courier_factory, admin_user):
        """Test approving a loan request"""
        courier = courier_factory()
        loan = loan_factory(courier, status=LoanStatus.PENDING)

        result = service.approve_loan(
            db_session,
            loan_id=loan.id,
            approved_by=admin_user.id
        )

        assert result is not None
        assert result.status == LoanStatus.APPROVED
        assert result.approved_by == admin_user.id

    def test_approve_loan_not_found(self, service, db_session, admin_user):
        """Test approving non-existent loan"""
        result = service.approve_loan(
            db_session,
            loan_id=99999,
            approved_by=admin_user.id
        )

        assert result is None

    def test_reject_loan_success(self, service, db_session, loan_factory, courier_factory, admin_user):
        """Test rejecting a loan request"""
        courier = courier_factory()
        loan = loan_factory(courier, status=LoanStatus.PENDING)

        result = service.reject_loan(
            db_session,
            loan_id=loan.id,
            rejected_by=admin_user.id,
            reason="Exceeds monthly income limit"
        )

        assert result is not None
        assert result.status == LoanStatus.REJECTED

    def test_reject_loan_not_found(self, service, db_session, admin_user):
        """Test rejecting non-existent loan"""
        result = service.reject_loan(
            db_session,
            loan_id=99999,
            rejected_by=admin_user.id
        )

        assert result is None

    # ==================== LOAN DISBURSEMENT TESTS ====================

    def test_disburse_loan(self, service, db_session, loan_factory, courier_factory):
        """Test disbursing an approved loan"""
        courier = courier_factory()
        loan = loan_factory(courier, status=LoanStatus.APPROVED)

        result = service.disburse_loan(db_session, loan_id=loan.id)

        assert result is not None
        assert result.status == LoanStatus.ACTIVE
        assert result.disbursed_at is not None

    def test_disburse_loan_sets_remaining_amount(self, service, db_session, loan_factory, courier_factory):
        """Test that disbursing sets remaining amount to full amount"""
        courier = courier_factory()
        loan = loan_factory(
            courier,
            status=LoanStatus.APPROVED,
            amount=Decimal("5000.00"),
            remaining_amount=Decimal("0.00")
        )

        result = service.disburse_loan(db_session, loan_id=loan.id)

        assert result.remaining_amount == result.amount

    # ==================== REPAYMENT TESTS ====================

    def test_record_repayment(self, service, db_session, loan_factory, courier_factory):
        """Test recording a loan repayment"""
        courier = courier_factory()
        loan = loan_factory(
            courier,
            status=LoanStatus.ACTIVE,
            amount=Decimal("5000.00"),
            remaining_amount=Decimal("5000.00"),
            installment_amount=Decimal("500.00")
        )

        result = service.record_repayment(
            db_session,
            loan_id=loan.id,
            amount=Decimal("500.00")
        )

        assert result is not None
        assert result.remaining_amount == Decimal("4500.00")

    def test_record_repayment_completes_loan(self, service, db_session, loan_factory, courier_factory):
        """Test that final repayment completes loan"""
        courier = courier_factory()
        loan = loan_factory(
            courier,
            status=LoanStatus.ACTIVE,
            amount=Decimal("5000.00"),
            remaining_amount=Decimal("500.00"),
            installment_amount=Decimal("500.00")
        )

        result = service.record_repayment(
            db_session,
            loan_id=loan.id,
            amount=Decimal("500.00")
        )

        assert result is not None
        assert result.remaining_amount == Decimal("0.00")
        assert result.status == LoanStatus.COMPLETED

    def test_record_repayment_partial_payment(self, service, db_session, loan_factory, courier_factory):
        """Test recording a partial repayment"""
        courier = courier_factory()
        loan = loan_factory(
            courier,
            status=LoanStatus.ACTIVE,
            amount=Decimal("5000.00"),
            remaining_amount=Decimal("5000.00"),
            installment_amount=Decimal("500.00")
        )

        result = service.record_repayment(
            db_session,
            loan_id=loan.id,
            amount=Decimal("250.00")
        )

        assert result is not None
        assert result.remaining_amount == Decimal("4750.00")
        assert result.status == LoanStatus.ACTIVE

    def test_record_repayment_overpayment(self, service, db_session, loan_factory, courier_factory):
        """Test recording an overpayment"""
        courier = courier_factory()
        loan = loan_factory(
            courier,
            status=LoanStatus.ACTIVE,
            amount=Decimal("5000.00"),
            remaining_amount=Decimal("1000.00"),
            installment_amount=Decimal("500.00")
        )

        # Pay more than remaining
        result = service.record_repayment(
            db_session,
            loan_id=loan.id,
            amount=Decimal("1500.00")
        )

        # Should complete the loan, remaining becomes 0
        assert result.remaining_amount == Decimal("0.00")
        assert result.status == LoanStatus.COMPLETED

    # ==================== ACTIVE LOANS TESTS ====================

    def test_get_active_loans_by_courier(self, service, db_session, loan_factory, courier_factory):
        """Test getting active loans for a courier"""
        courier = courier_factory()
        active = loan_factory(courier, status=LoanStatus.ACTIVE)
        completed = loan_factory(courier, status=LoanStatus.COMPLETED)

        result = service.get_active_loans(db_session, courier_id=courier.id)

        assert len(result) >= 1
        assert all(l.status == LoanStatus.ACTIVE for l in result)

    def test_get_total_active_loan_amount(self, service, db_session, loan_factory, courier_factory):
        """Test getting total active loan amount for courier"""
        courier = courier_factory()
        loan1 = loan_factory(
            courier,
            status=LoanStatus.ACTIVE,
            remaining_amount=Decimal("3000.00")
        )
        loan2 = loan_factory(
            courier,
            status=LoanStatus.ACTIVE,
            remaining_amount=Decimal("2000.00")
        )

        total = service.get_total_outstanding(db_session, courier_id=courier.id)

        assert total >= Decimal("5000.00")

    # ==================== STATISTICS TESTS ====================

    def test_get_statistics(self, service, db_session, loan_factory, courier_factory):
        """Test getting loan statistics"""
        courier = courier_factory()
        loan_factory(courier, status=LoanStatus.PENDING, amount=Decimal("1000.00"))
        loan_factory(courier, status=LoanStatus.ACTIVE, amount=Decimal("2000.00"))
        loan_factory(courier, status=LoanStatus.COMPLETED, amount=Decimal("3000.00"))

        stats = service.get_statistics(db_session)

        assert "total_loans" in stats
        assert "pending_loans" in stats
        assert "active_loans" in stats
        assert "total_amount_disbursed" in stats
        assert "total_amount_outstanding" in stats

    def test_get_statistics_by_organization(self, service, db_session, loan_factory, courier_factory, test_organization):
        """Test getting loan statistics filtered by organization"""
        courier = courier_factory(organization_id=test_organization.id)
        loan_factory(courier, status=LoanStatus.ACTIVE, organization_id=test_organization.id)

        stats = service.get_statistics(db_session, organization_id=test_organization.id)

        assert stats["active_loans"] >= 1

    # ==================== PAGINATION TESTS ====================

    def test_get_multi_pagination(self, service, db_session, loan_factory, courier_factory):
        """Test pagination for loans"""
        courier = courier_factory()
        for _ in range(5):
            loan_factory(courier)

        first_page = service.get_multi(db_session, skip=0, limit=2)
        second_page = service.get_multi(db_session, skip=2, limit=2)

        assert len(first_page) == 2
        assert len(second_page) == 2

    def test_get_by_courier_pagination(self, service, db_session, loan_factory, courier_factory):
        """Test pagination for courier loans"""
        courier = courier_factory()
        for _ in range(5):
            loan_factory(courier)

        first_page = service.get_by_courier(db_session, courier_id=courier.id, skip=0, limit=2)
        second_page = service.get_by_courier(db_session, courier_id=courier.id, skip=2, limit=2)

        assert len(first_page) == 2
        assert len(second_page) == 2

    # ==================== ELIGIBILITY TESTS ====================

    def test_check_loan_eligibility_no_active_loans(self, service, db_session, courier_factory):
        """Test loan eligibility with no active loans"""
        courier = courier_factory()

        eligible = service.check_eligibility(db_session, courier_id=courier.id)

        assert eligible is True

    def test_check_loan_eligibility_with_active_loan(self, service, db_session, loan_factory, courier_factory):
        """Test loan eligibility with existing active loan"""
        courier = courier_factory()
        active_loan = loan_factory(courier, status=LoanStatus.ACTIVE)

        eligible = service.check_eligibility(
            db_session,
            courier_id=courier.id,
            max_active_loans=1
        )

        assert eligible is False

    def test_check_loan_eligibility_amount_limit(self, service, db_session, loan_factory, courier_factory):
        """Test loan eligibility with amount limit"""
        courier = courier_factory()
        # Courier has active loan of 4000
        active_loan = loan_factory(
            courier,
            status=LoanStatus.ACTIVE,
            remaining_amount=Decimal("4000.00")
        )

        # Try to get another 3000 (total would be 7000, exceeding 6000 limit)
        eligible = service.check_eligibility(
            db_session,
            courier_id=courier.id,
            requested_amount=Decimal("3000.00"),
            max_total_amount=Decimal("6000.00")
        )

        assert eligible is False
