"""
Unit Tests for Bonus Service

Tests bonus management functionality:
- CRUD operations
- Filtering by courier, type, status, date range
- Bonus approval and payment tracking
- Statistics calculation
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

from app.services.hr.bonus_service import BonusService, bonus_service
from app.models.hr.bonus import Bonus, BonusType, PaymentStatus


# ==================== Fixtures ====================

@pytest.fixture
def mock_db():
    """Create a mock database session"""
    return MagicMock()


@pytest.fixture
def service():
    """Create BonusService instance"""
    return BonusService(Bonus)


@pytest.fixture
def sample_bonus():
    """Create a sample bonus object"""
    bonus = MagicMock(spec=Bonus)
    bonus.id = 1
    bonus.courier_id = 100
    bonus.amount = Decimal("500.00")
    bonus.bonus_type = BonusType.PERFORMANCE
    bonus.payment_status = PaymentStatus.PENDING
    bonus.bonus_date = date.today()
    return bonus


# ==================== Get by Courier Tests ====================

class TestGetByCourier:
    """Tests for get_by_courier method"""

    def test_get_by_courier_returns_bonuses(self, service, mock_db, sample_bonus):
        """Should return bonuses for specific courier"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_bonus]

        result = service.get_by_courier(mock_db, courier_id=100)

        assert len(result) == 1
        assert result[0].courier_id == 100

    def test_get_by_courier_empty_result(self, service, mock_db):
        """Should return empty list when no bonuses found"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        result = service.get_by_courier(mock_db, courier_id=999)

        assert result == []

    def test_get_by_courier_pagination(self, service, mock_db, sample_bonus):
        """Should respect skip and limit parameters"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_bonus]

        service.get_by_courier(mock_db, courier_id=100, skip=10, limit=5)

        # Verify offset and limit were called
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.assert_called_once_with(10)
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.assert_called_once_with(5)


# ==================== Get by Type Tests ====================

class TestGetByType:
    """Tests for get_by_type method"""

    def test_get_by_type_performance(self, service, mock_db, sample_bonus):
        """Should filter by performance bonus type"""
        sample_bonus.bonus_type = BonusType.PERFORMANCE
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_bonus]

        result = service.get_by_type(mock_db, bonus_type=BonusType.PERFORMANCE)

        assert len(result) == 1
        assert result[0].bonus_type == BonusType.PERFORMANCE

    def test_get_by_type_empty(self, service, mock_db):
        """Should return empty list when no bonuses of type found"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        result = service.get_by_type(mock_db, bonus_type=BonusType.PERFORMANCE)

        assert result == []


# ==================== Get by Status Tests ====================

class TestGetByStatus:
    """Tests for get_by_status method"""

    def test_get_by_status_pending(self, service, mock_db, sample_bonus):
        """Should filter by pending status"""
        sample_bonus.payment_status = PaymentStatus.PENDING
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_bonus]

        result = service.get_by_status(mock_db, payment_status=PaymentStatus.PENDING)

        assert len(result) == 1
        assert result[0].payment_status == PaymentStatus.PENDING

    def test_get_by_status_approved(self, service, mock_db, sample_bonus):
        """Should filter by approved status"""
        sample_bonus.payment_status = PaymentStatus.APPROVED
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_bonus]

        result = service.get_by_status(mock_db, payment_status=PaymentStatus.APPROVED)

        assert len(result) == 1

    def test_get_by_status_paid(self, service, mock_db, sample_bonus):
        """Should filter by paid status"""
        sample_bonus.payment_status = PaymentStatus.PAID
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_bonus]

        result = service.get_by_status(mock_db, payment_status=PaymentStatus.PAID)

        assert len(result) == 1


# ==================== Get by Date Range Tests ====================

class TestGetByDateRange:
    """Tests for get_by_date_range method"""

    def test_get_by_date_range(self, service, mock_db, sample_bonus):
        """Should filter by date range"""
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_bonus]

        result = service.get_by_date_range(
            mock_db,
            start_date=start_date,
            end_date=end_date
        )

        assert len(result) == 1

    def test_get_by_date_range_empty(self, service, mock_db):
        """Should return empty when no bonuses in range"""
        start_date = date.today() - timedelta(days=365)
        end_date = date.today() - timedelta(days=300)
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        result = service.get_by_date_range(
            mock_db,
            start_date=start_date,
            end_date=end_date
        )

        assert result == []


# ==================== Approve Bonus Tests ====================

class TestApproveBonus:
    """Tests for approve_bonus method"""

    def test_approve_bonus_success(self, service, mock_db, sample_bonus):
        """Should approve bonus successfully"""
        with patch.object(service, 'get', return_value=sample_bonus):
            result = service.approve_bonus(
                mock_db,
                bonus_id=1,
                approved_by=10
            )

            assert result.payment_status == PaymentStatus.APPROVED
            assert result.approved_by == 10
            mock_db.commit.assert_called_once()

    def test_approve_bonus_not_found(self, service, mock_db):
        """Should return None when bonus not found"""
        with patch.object(service, 'get', return_value=None):
            result = service.approve_bonus(
                mock_db,
                bonus_id=999,
                approved_by=10
            )

            assert result is None

    def test_approve_bonus_with_custom_date(self, service, mock_db, sample_bonus):
        """Should set custom approval date"""
        custom_date = date.today() - timedelta(days=1)
        with patch.object(service, 'get', return_value=sample_bonus):
            result = service.approve_bonus(
                mock_db,
                bonus_id=1,
                approved_by=10,
                approval_date=custom_date
            )

            assert result.approval_date == custom_date


# ==================== Mark as Paid Tests ====================

class TestMarkAsPaid:
    """Tests for mark_as_paid method"""

    def test_mark_as_paid_success(self, service, mock_db, sample_bonus):
        """Should mark bonus as paid"""
        with patch.object(service, 'get', return_value=sample_bonus):
            result = service.mark_as_paid(mock_db, bonus_id=1)

            assert result.payment_status == PaymentStatus.PAID
            mock_db.commit.assert_called_once()

    def test_mark_as_paid_not_found(self, service, mock_db):
        """Should return None when bonus not found"""
        with patch.object(service, 'get', return_value=None):
            result = service.mark_as_paid(mock_db, bonus_id=999)

            assert result is None


# ==================== Get Courier Total Bonuses Tests ====================

class TestGetCourierTotalBonuses:
    """Tests for get_courier_total_bonuses method"""

    def test_get_total_bonuses(self, service, mock_db):
        """Should calculate total bonus amount"""
        bonus1 = MagicMock(amount=Decimal("500.00"))
        bonus2 = MagicMock(amount=Decimal("300.00"))
        mock_db.query.return_value.filter.return_value.all.return_value = [bonus1, bonus2]

        result = service.get_courier_total_bonuses(mock_db, courier_id=100)

        assert result == Decimal("800.00")

    def test_get_total_bonuses_empty(self, service, mock_db):
        """Should return zero when no bonuses"""
        mock_db.query.return_value.filter.return_value.all.return_value = []

        result = service.get_courier_total_bonuses(mock_db, courier_id=100)

        assert result == Decimal("0")

    def test_get_total_bonuses_by_year(self, service, mock_db):
        """Should filter by year"""
        bonus1 = MagicMock(amount=Decimal("500.00"))
        mock_db.query.return_value.filter.return_value.filter.return_value.all.return_value = [bonus1]

        result = service.get_courier_total_bonuses(mock_db, courier_id=100, year=2025)

        assert result == Decimal("500.00")


# ==================== Statistics Tests ====================

class TestGetStatistics:
    """Tests for get_statistics method"""

    def test_get_statistics_empty(self, service, mock_db):
        """Should return zero stats when no bonuses"""
        mock_db.query.return_value.filter.return_value.all.return_value = []

        # Mock BonusType iteration
        with patch('app.services.hr.bonus_service.BonusType', []):
            result = service.get_statistics(mock_db)

        assert result["total_records"] == 0
        assert result["total_amount"] == 0.0
        assert result["average_amount"] == 0

    def test_get_statistics_with_bonuses(self, service, mock_db):
        """Should calculate statistics correctly"""
        bonus1 = MagicMock(
            amount=Decimal("500.00"),
            payment_status=PaymentStatus.PENDING,
            bonus_type=BonusType.PERFORMANCE
        )
        bonus2 = MagicMock(
            amount=Decimal("300.00"),
            payment_status=PaymentStatus.APPROVED,
            bonus_type=BonusType.PERFORMANCE
        )
        mock_db.query.return_value.filter.return_value.all.return_value = [bonus1, bonus2]
        mock_db.query.return_value.all.return_value = [bonus1, bonus2]

        result = service.get_statistics(mock_db)

        assert result["total_records"] == 2
        assert result["total_amount"] == 800.0
        assert result["pending_count"] == 1
        assert result["approved_count"] == 1
        assert result["paid_count"] == 0
        assert result["average_amount"] == 400.0


# ==================== Singleton Tests ====================

class TestSingleton:
    """Tests for singleton instance"""

    def test_bonus_service_singleton_exists(self):
        """Should have a singleton instance"""
        assert bonus_service is not None

    def test_bonus_service_is_instance(self):
        """Should be a BonusService instance"""
        assert isinstance(bonus_service, BonusService)
