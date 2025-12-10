"""
Unit Tests for COD Service

Tests COD (Cash On Delivery) management functionality:
- Getting COD by courier
- Getting COD by status
- Getting pending COD
- Date range queries
- Status transitions (collected, deposited, reconciled)
- Bulk operations
- Statistics
- Courier balance
- Settlement
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch, PropertyMock

from app.services.operations.cod_service import CODService, cod_service
from app.models.operations.cod import COD, CODStatus


# ==================== Fixtures ====================

@pytest.fixture
def service():
    """Create CODService instance"""
    return CODService(COD)


@pytest.fixture
def mock_db():
    """Create mock database session"""
    return MagicMock()


@pytest.fixture
def sample_cod():
    """Create sample COD object"""
    cod = MagicMock(spec=COD)
    cod.id = 1
    cod.courier_id = 100
    cod.amount = Decimal("500.00")
    cod.status = CODStatus.PENDING
    cod.collection_date = date.today()
    cod.deposit_date = None
    cod.reference_number = None
    cod.notes = None
    return cod


@pytest.fixture
def multiple_cods():
    """Create multiple COD objects with different statuses"""
    cods = []
    statuses = [CODStatus.PENDING, CODStatus.COLLECTED, CODStatus.DEPOSITED, CODStatus.RECONCILED]

    for i, status in enumerate(statuses):
        cod = MagicMock(spec=COD)
        cod.id = i + 1
        cod.courier_id = 100
        cod.amount = Decimal("100.00")
        cod.status = status
        cod.collection_date = date.today() - timedelta(days=i)
        cods.append(cod)

    return cods


# ==================== Get By Courier Tests ====================

class TestGetByCourier:
    """Tests for get_by_courier method"""

    def test_get_by_courier_returns_list(self, service, mock_db, sample_cod):
        """Should return list of COD records for courier"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_cod]

        result = service.get_by_courier(mock_db, courier_id=100)

        assert len(result) == 1
        assert result[0].courier_id == 100

    def test_get_by_courier_respects_pagination(self, service, mock_db):
        """Should respect skip and limit parameters"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        service.get_by_courier(mock_db, courier_id=100, skip=10, limit=20)

        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.assert_called_with(10)
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.assert_called_with(20)

    def test_get_by_courier_empty(self, service, mock_db):
        """Should return empty list when no records"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        result = service.get_by_courier(mock_db, courier_id=999)

        assert result == []


# ==================== Get By Status Tests ====================

class TestGetByStatus:
    """Tests for get_by_status method"""

    def test_get_pending_status(self, service, mock_db, sample_cod):
        """Should get COD records with pending status"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_cod]

        result = service.get_by_status(mock_db, status=CODStatus.PENDING)

        assert len(result) == 1

    def test_get_collected_status(self, service, mock_db):
        """Should get COD records with collected status"""
        collected_cod = MagicMock(spec=COD)
        collected_cod.status = CODStatus.COLLECTED
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [collected_cod]

        result = service.get_by_status(mock_db, status=CODStatus.COLLECTED)

        assert len(result) == 1

    def test_get_by_status_pagination(self, service, mock_db):
        """Should respect pagination parameters"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        service.get_by_status(mock_db, status=CODStatus.DEPOSITED, skip=5, limit=10)

        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.assert_called_with(5)


# ==================== Get Pending Tests ====================

class TestGetPending:
    """Tests for get_pending method"""

    def test_get_pending_all(self, service, mock_db, sample_cod):
        """Should get all pending COD records"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_cod]

        result = service.get_pending(mock_db)

        assert len(result) == 1

    def test_get_pending_for_courier(self, service, mock_db, sample_cod):
        """Should filter pending by courier ID"""
        mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_cod]

        result = service.get_pending(mock_db, courier_id=100)

        assert len(result) == 1

    def test_get_pending_empty(self, service, mock_db):
        """Should return empty list when no pending"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        result = service.get_pending(mock_db)

        assert result == []


# ==================== Get By Date Range Tests ====================

class TestGetByDateRange:
    """Tests for get_by_date_range method"""

    def test_get_by_date_range(self, service, mock_db, sample_cod):
        """Should get COD records within date range"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_cod]

        start_date = date.today() - timedelta(days=7)
        end_date = date.today()

        result = service.get_by_date_range(mock_db, start_date=start_date, end_date=end_date)

        assert len(result) == 1

    def test_get_by_date_range_with_courier(self, service, mock_db, sample_cod):
        """Should filter by courier within date range"""
        mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_cod]

        result = service.get_by_date_range(
            mock_db,
            start_date=date.today() - timedelta(days=7),
            end_date=date.today(),
            courier_id=100
        )

        assert len(result) == 1

    def test_get_by_date_range_pagination(self, service, mock_db):
        """Should respect pagination parameters"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        service.get_by_date_range(
            mock_db,
            start_date=date.today(),
            end_date=date.today(),
            skip=10,
            limit=50
        )

        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.assert_called_with(10)


# ==================== Mark As Collected Tests ====================

class TestMarkAsCollected:
    """Tests for mark_as_collected method"""

    def test_mark_as_collected_success(self, service, mock_db, sample_cod):
        """Should mark COD as collected"""
        with patch.object(service, 'get', return_value=sample_cod):
            with patch.object(service, 'update', return_value=sample_cod) as mock_update:
                result = service.mark_as_collected(mock_db, cod_id=1)

        assert result is not None
        mock_update.assert_called_once()
        call_args = mock_update.call_args[1]
        assert call_args["obj_in"]["status"] == CODStatus.COLLECTED

    def test_mark_as_collected_with_reference(self, service, mock_db, sample_cod):
        """Should include reference number when provided"""
        with patch.object(service, 'get', return_value=sample_cod):
            with patch.object(service, 'update', return_value=sample_cod) as mock_update:
                service.mark_as_collected(mock_db, cod_id=1, reference_number="REF123")

        call_args = mock_update.call_args[1]
        assert call_args["obj_in"]["reference_number"] == "REF123"

    def test_mark_as_collected_with_notes(self, service, mock_db, sample_cod):
        """Should include notes when provided"""
        with patch.object(service, 'get', return_value=sample_cod):
            with patch.object(service, 'update', return_value=sample_cod) as mock_update:
                service.mark_as_collected(mock_db, cod_id=1, notes="Test notes")

        call_args = mock_update.call_args[1]
        assert call_args["obj_in"]["notes"] == "Test notes"

    def test_mark_as_collected_not_found(self, service, mock_db):
        """Should return None when COD not found"""
        with patch.object(service, 'get', return_value=None):
            result = service.mark_as_collected(mock_db, cod_id=999)

        assert result is None


# ==================== Mark As Deposited Tests ====================

class TestMarkAsDeposited:
    """Tests for mark_as_deposited method"""

    def test_mark_as_deposited_success(self, service, mock_db, sample_cod):
        """Should mark COD as deposited"""
        with patch.object(service, 'get', return_value=sample_cod):
            with patch.object(service, 'update', return_value=sample_cod) as mock_update:
                result = service.mark_as_deposited(mock_db, cod_id=1)

        assert result is not None
        call_args = mock_update.call_args[1]
        assert call_args["obj_in"]["status"] == CODStatus.DEPOSITED
        assert "deposit_date" in call_args["obj_in"]

    def test_mark_as_deposited_with_date(self, service, mock_db, sample_cod):
        """Should use provided deposit date"""
        deposit_date = date(2025, 1, 15)
        with patch.object(service, 'get', return_value=sample_cod):
            with patch.object(service, 'update', return_value=sample_cod) as mock_update:
                service.mark_as_deposited(mock_db, cod_id=1, deposit_date=deposit_date)

        call_args = mock_update.call_args[1]
        assert call_args["obj_in"]["deposit_date"] == deposit_date

    def test_mark_as_deposited_default_date(self, service, mock_db, sample_cod):
        """Should default to today's date"""
        with patch.object(service, 'get', return_value=sample_cod):
            with patch.object(service, 'update', return_value=sample_cod) as mock_update:
                service.mark_as_deposited(mock_db, cod_id=1)

        call_args = mock_update.call_args[1]
        assert call_args["obj_in"]["deposit_date"] == date.today()

    def test_mark_as_deposited_not_found(self, service, mock_db):
        """Should return None when COD not found"""
        with patch.object(service, 'get', return_value=None):
            result = service.mark_as_deposited(mock_db, cod_id=999)

        assert result is None


# ==================== Mark As Reconciled Tests ====================

class TestMarkAsReconciled:
    """Tests for mark_as_reconciled method"""

    def test_mark_as_reconciled_success(self, service, mock_db, sample_cod):
        """Should mark COD as reconciled"""
        with patch.object(service, 'get', return_value=sample_cod):
            with patch.object(service, 'update', return_value=sample_cod) as mock_update:
                result = service.mark_as_reconciled(mock_db, cod_id=1)

        assert result is not None
        call_args = mock_update.call_args[1]
        assert call_args["obj_in"]["status"] == CODStatus.RECONCILED

    def test_mark_as_reconciled_with_notes(self, service, mock_db, sample_cod):
        """Should include notes when provided"""
        with patch.object(service, 'get', return_value=sample_cod):
            with patch.object(service, 'update', return_value=sample_cod) as mock_update:
                service.mark_as_reconciled(mock_db, cod_id=1, notes="Reconciliation notes")

        call_args = mock_update.call_args[1]
        assert call_args["obj_in"]["notes"] == "Reconciliation notes"

    def test_mark_as_reconciled_not_found(self, service, mock_db):
        """Should return None when COD not found"""
        with patch.object(service, 'get', return_value=None):
            result = service.mark_as_reconciled(mock_db, cod_id=999)

        assert result is None


# ==================== Bulk Deposit Tests ====================

class TestBulkDeposit:
    """Tests for bulk_deposit method"""

    def test_bulk_deposit_success(self, service, mock_db):
        """Should deposit multiple COD records"""
        with patch.object(service, 'bulk_update', return_value=5) as mock_bulk:
            result = service.bulk_deposit(mock_db, cod_ids=[1, 2, 3, 4, 5])

        assert result == 5
        mock_bulk.assert_called_once()

    def test_bulk_deposit_with_date(self, service, mock_db):
        """Should use provided deposit date"""
        deposit_date = date(2025, 1, 20)
        with patch.object(service, 'bulk_update', return_value=3) as mock_bulk:
            service.bulk_deposit(mock_db, cod_ids=[1, 2, 3], deposit_date=deposit_date)

        call_args = mock_bulk.call_args[1]
        assert call_args["update_data"]["deposit_date"] == deposit_date

    def test_bulk_deposit_with_reference(self, service, mock_db):
        """Should include reference number"""
        with patch.object(service, 'bulk_update', return_value=2) as mock_bulk:
            service.bulk_deposit(mock_db, cod_ids=[1, 2], reference_number="BULK-REF-001")

        call_args = mock_bulk.call_args[1]
        assert call_args["update_data"]["reference_number"] == "BULK-REF-001"


# ==================== Statistics Tests ====================

class TestGetStatistics:
    """Tests for get_statistics method"""

    def test_get_statistics_all(self, service, mock_db, multiple_cods):
        """Should return complete statistics"""
        mock_db.query.return_value.all.return_value = multiple_cods

        result = service.get_statistics(mock_db)

        assert result["total_transactions"] == 4
        assert result["pending_count"] == 1
        assert result["collected_count"] == 1
        assert result["deposited_count"] == 1
        assert result["reconciled_count"] == 1

    def test_get_statistics_amounts(self, service, mock_db, multiple_cods):
        """Should calculate amounts correctly"""
        mock_db.query.return_value.all.return_value = multiple_cods

        result = service.get_statistics(mock_db)

        assert result["total_amount"] == 400.0  # 4 * 100
        assert result["pending_amount"] == 100.0
        assert result["collected_amount"] == 100.0
        assert result["deposited_amount"] == 100.0
        assert result["reconciled_amount"] == 100.0

    def test_get_statistics_average(self, service, mock_db, multiple_cods):
        """Should calculate average transaction amount"""
        mock_db.query.return_value.all.return_value = multiple_cods

        result = service.get_statistics(mock_db)

        assert result["average_transaction_amount"] == 100.0

    def test_get_statistics_with_courier_filter(self, service, mock_db, sample_cod):
        """Should filter by courier ID"""
        mock_db.query.return_value.filter.return_value.all.return_value = [sample_cod]

        result = service.get_statistics(mock_db, courier_id=100)

        assert result["total_transactions"] == 1

    def test_get_statistics_with_date_filter(self, service, mock_db, sample_cod):
        """Should filter by date range"""
        mock_db.query.return_value.filter.return_value.filter.return_value.all.return_value = [sample_cod]

        result = service.get_statistics(
            mock_db,
            start_date=date.today() - timedelta(days=7),
            end_date=date.today()
        )

        assert result["total_transactions"] == 1

    def test_get_statistics_empty(self, service, mock_db):
        """Should handle empty results"""
        mock_db.query.return_value.all.return_value = []

        result = service.get_statistics(mock_db)

        assert result["total_transactions"] == 0
        assert result["average_transaction_amount"] == 0


# ==================== Courier Balance Tests ====================

class TestGetCourierBalance:
    """Tests for get_courier_balance method"""

    def test_get_courier_balance(self, service, mock_db):
        """Should return courier balance"""
        pending_cod = MagicMock(spec=COD)
        pending_cod.amount = Decimal("300.00")
        pending_cod.status = CODStatus.PENDING

        collected_cod = MagicMock(spec=COD)
        collected_cod.amount = Decimal("200.00")
        collected_cod.status = CODStatus.COLLECTED

        mock_db.query.return_value.filter.return_value.all.return_value = [pending_cod, collected_cod]

        result = service.get_courier_balance(mock_db, courier_id=100)

        assert result["courier_id"] == 100
        assert result["pending_amount"] == 300.0
        assert result["collected_amount"] == 200.0
        assert result["total_balance"] == 500.0
        assert result["transaction_count"] == 2

    def test_get_courier_balance_empty(self, service, mock_db):
        """Should handle no pending/collected COD"""
        mock_db.query.return_value.filter.return_value.all.return_value = []

        result = service.get_courier_balance(mock_db, courier_id=100)

        assert result["pending_amount"] == 0.0
        assert result["collected_amount"] == 0.0
        assert result["total_balance"] == 0.0
        assert result["transaction_count"] == 0


# ==================== Settle Courier COD Tests ====================

class TestSettleCourierCod:
    """Tests for settle_courier_cod method"""

    def test_settle_courier_cod_success(self, service, mock_db):
        """Should settle all pending/collected COD"""
        pending_cod = MagicMock(spec=COD)
        pending_cod.id = 1
        pending_cod.amount = Decimal("300.00")
        pending_cod.status = CODStatus.PENDING

        collected_cod = MagicMock(spec=COD)
        collected_cod.id = 2
        collected_cod.amount = Decimal("200.00")
        collected_cod.status = CODStatus.COLLECTED

        mock_db.query.return_value.filter.return_value.all.return_value = [pending_cod, collected_cod]

        with patch.object(service, 'bulk_deposit', return_value=2) as mock_bulk:
            result = service.settle_courier_cod(mock_db, courier_id=100)

        assert result["courier_id"] == 100
        assert result["transactions_settled"] == 2
        assert result["total_amount"] == 500.0
        mock_bulk.assert_called_once_with(
            mock_db,
            cod_ids=[1, 2],
            deposit_date=date.today(),
            reference_number=None
        )

    def test_settle_courier_cod_with_options(self, service, mock_db):
        """Should use provided deposit date and reference"""
        pending_cod = MagicMock(spec=COD)
        pending_cod.id = 1
        pending_cod.amount = Decimal("100.00")
        pending_cod.status = CODStatus.PENDING

        mock_db.query.return_value.filter.return_value.all.return_value = [pending_cod]
        deposit_date = date(2025, 1, 25)

        with patch.object(service, 'bulk_deposit', return_value=1) as mock_bulk:
            result = service.settle_courier_cod(
                mock_db,
                courier_id=100,
                deposit_date=deposit_date,
                reference_number="SETTLE-001"
            )

        assert result["deposit_date"] == deposit_date.isoformat()
        assert result["reference_number"] == "SETTLE-001"
        mock_bulk.assert_called_once_with(
            mock_db,
            cod_ids=[1],
            deposit_date=deposit_date,
            reference_number="SETTLE-001"
        )

    def test_settle_courier_cod_empty(self, service, mock_db):
        """Should handle no pending/collected COD"""
        mock_db.query.return_value.filter.return_value.all.return_value = []

        result = service.settle_courier_cod(mock_db, courier_id=100)

        assert result["transactions_settled"] == 0
        assert result["total_amount"] == 0.0
        assert "No pending or collected" in result["message"]


# ==================== Status Workflow Tests ====================

class TestStatusWorkflow:
    """Tests for COD status workflow"""

    def test_pending_to_collected(self, service, mock_db, sample_cod):
        """Should transition from pending to collected"""
        sample_cod.status = CODStatus.PENDING

        with patch.object(service, 'get', return_value=sample_cod):
            with patch.object(service, 'update', return_value=sample_cod) as mock_update:
                service.mark_as_collected(mock_db, cod_id=1)

        call_args = mock_update.call_args[1]
        assert call_args["obj_in"]["status"] == CODStatus.COLLECTED

    def test_collected_to_deposited(self, service, mock_db, sample_cod):
        """Should transition from collected to deposited"""
        sample_cod.status = CODStatus.COLLECTED

        with patch.object(service, 'get', return_value=sample_cod):
            with patch.object(service, 'update', return_value=sample_cod) as mock_update:
                service.mark_as_deposited(mock_db, cod_id=1)

        call_args = mock_update.call_args[1]
        assert call_args["obj_in"]["status"] == CODStatus.DEPOSITED

    def test_deposited_to_reconciled(self, service, mock_db, sample_cod):
        """Should transition from deposited to reconciled"""
        sample_cod.status = CODStatus.DEPOSITED

        with patch.object(service, 'get', return_value=sample_cod):
            with patch.object(service, 'update', return_value=sample_cod) as mock_update:
                service.mark_as_reconciled(mock_db, cod_id=1)

        call_args = mock_update.call_args[1]
        assert call_args["obj_in"]["status"] == CODStatus.RECONCILED


# ==================== Singleton Tests ====================

class TestSingleton:
    """Tests for singleton instance"""

    def test_singleton_exists(self):
        """Should have a singleton instance"""
        assert cod_service is not None

    def test_singleton_is_instance(self):
        """Should be a CODService instance"""
        assert isinstance(cod_service, CODService)

    def test_singleton_model(self):
        """Singleton should use COD model"""
        assert cod_service.model == COD
