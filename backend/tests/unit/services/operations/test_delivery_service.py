"""
Unit Tests for Delivery Service

Tests cover:
- Delivery CRUD operations
- Status management
- Courier assignment
- COD tracking
- Statistics

Author: BARQ QA Team
Last Updated: 2025-12-10
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

from app.services.operations.delivery_service import DeliveryService, delivery_service
from app.models.operations.delivery import Delivery, DeliveryStatus


class TestDeliveryService:
    """Test Delivery Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create DeliveryService instance"""
        return DeliveryService(Delivery)

    # ==================== CRUD TESTS ====================

    def test_create_delivery(self, service, db_session, courier_factory, test_organization):
        """Test creating a delivery"""
        from app.schemas.operations.delivery import DeliveryCreate

        courier = courier_factory()
        delivery_data = DeliveryCreate(
            tracking_number="TRK-NEW-001",
            courier_id=courier.id,
            pickup_address="123 Pickup St, Riyadh",
            delivery_address="456 Delivery Ave, Riyadh",
            customer_name="Test Customer",
            customer_phone="+966501234567",
            organization_id=test_organization.id
        )

        delivery = service.create(db_session, obj_in=delivery_data)

        assert delivery is not None
        assert delivery.tracking_number == "TRK-NEW-001"
        assert delivery.status == DeliveryStatus.PENDING

    def test_get_delivery_by_id(self, service, db_session, delivery_factory, courier_factory):
        """Test getting delivery by ID"""
        courier = courier_factory()
        delivery = delivery_factory(courier)

        result = service.get(db_session, id=delivery.id)

        assert result is not None
        assert result.id == delivery.id

    def test_get_by_tracking_number_exists(self, service, db_session, delivery_factory, courier_factory):
        """Test getting delivery by tracking number when exists"""
        courier = courier_factory()
        delivery = delivery_factory(courier, tracking_number="TRK-FIND-001")

        result = service.get_by_tracking_number(db_session, tracking_number="TRK-FIND-001")

        assert result is not None
        assert result.tracking_number == "TRK-FIND-001"

    def test_get_by_tracking_number_not_exists(self, service, db_session):
        """Test getting delivery by tracking number when not exists"""
        result = service.get_by_tracking_number(db_session, tracking_number="TRK-NONEXISTENT")

        assert result is None

    # ==================== COURIER FILTER TESTS ====================

    def test_get_by_courier(self, service, db_session, delivery_factory, courier_factory):
        """Test getting deliveries by courier"""
        courier1 = courier_factory()
        courier2 = courier_factory()
        delivery1 = delivery_factory(courier1)
        delivery2 = delivery_factory(courier1)
        delivery3 = delivery_factory(courier2)

        result = service.get_by_courier(db_session, courier_id=courier1.id)

        assert len(result) >= 2
        assert all(d.courier_id == courier1.id for d in result)

    def test_get_by_courier_empty(self, service, db_session, courier_factory):
        """Test getting deliveries for courier with no deliveries"""
        courier = courier_factory()

        result = service.get_by_courier(db_session, courier_id=courier.id)

        assert len(result) == 0

    # ==================== STATUS FILTER TESTS ====================

    def test_get_by_status_pending(self, service, db_session, delivery_factory, courier_factory):
        """Test getting pending deliveries"""
        courier = courier_factory()
        pending = delivery_factory(courier, status=DeliveryStatus.PENDING)

        result = service.get_by_status(db_session, status=DeliveryStatus.PENDING)

        assert len(result) >= 1
        assert all(d.status == DeliveryStatus.PENDING for d in result)

    def test_get_by_status_in_transit(self, service, db_session, delivery_factory, courier_factory):
        """Test getting in-transit deliveries"""
        courier = courier_factory()
        in_transit = delivery_factory(courier, status=DeliveryStatus.IN_TRANSIT)

        result = service.get_by_status(db_session, status=DeliveryStatus.IN_TRANSIT)

        assert len(result) >= 1
        assert all(d.status == DeliveryStatus.IN_TRANSIT for d in result)

    def test_get_by_status_delivered(self, service, db_session, delivery_factory, courier_factory):
        """Test getting delivered deliveries"""
        courier = courier_factory()
        delivered = delivery_factory(courier, status=DeliveryStatus.DELIVERED)

        result = service.get_by_status(db_session, status=DeliveryStatus.DELIVERED)

        assert len(result) >= 1
        assert all(d.status == DeliveryStatus.DELIVERED for d in result)

    def test_get_pending_deliveries(self, service, db_session, delivery_factory, courier_factory):
        """Test getting pending deliveries"""
        courier = courier_factory()
        pending1 = delivery_factory(courier, status=DeliveryStatus.PENDING)
        pending2 = delivery_factory(courier, status=DeliveryStatus.PENDING)
        delivered = delivery_factory(courier, status=DeliveryStatus.DELIVERED)

        result = service.get_pending_deliveries(db_session)

        assert len(result) >= 2
        assert all(d.status == DeliveryStatus.PENDING for d in result)

    def test_get_pending_deliveries_by_courier(self, service, db_session, delivery_factory, courier_factory):
        """Test getting pending deliveries for specific courier"""
        courier1 = courier_factory()
        courier2 = courier_factory()
        pending1 = delivery_factory(courier1, status=DeliveryStatus.PENDING)
        pending2 = delivery_factory(courier2, status=DeliveryStatus.PENDING)

        result = service.get_pending_deliveries(db_session, courier_id=courier1.id)

        assert all(d.courier_id == courier1.id for d in result)

    # ==================== STATUS UPDATE TESTS ====================

    def test_update_status_to_in_transit(self, service, db_session, delivery_factory, courier_factory):
        """Test updating delivery status to in-transit"""
        courier = courier_factory()
        delivery = delivery_factory(courier, status=DeliveryStatus.PENDING)

        result = service.update_status(
            db_session,
            delivery_id=delivery.id,
            status=DeliveryStatus.IN_TRANSIT
        )

        assert result is not None
        assert result.status == DeliveryStatus.IN_TRANSIT

    def test_update_status_to_delivered(self, service, db_session, delivery_factory, courier_factory):
        """Test updating delivery status to delivered sets delivery time"""
        courier = courier_factory()
        delivery = delivery_factory(courier, status=DeliveryStatus.IN_TRANSIT)

        result = service.update_status(
            db_session,
            delivery_id=delivery.id,
            status=DeliveryStatus.DELIVERED
        )

        assert result is not None
        assert result.status == DeliveryStatus.DELIVERED
        assert result.delivery_time is not None

    def test_update_status_to_failed(self, service, db_session, delivery_factory, courier_factory):
        """Test updating delivery status to failed with notes"""
        courier = courier_factory()
        delivery = delivery_factory(courier, status=DeliveryStatus.IN_TRANSIT)

        result = service.update_status(
            db_session,
            delivery_id=delivery.id,
            status=DeliveryStatus.FAILED,
            notes="Customer not available"
        )

        assert result is not None
        assert result.status == DeliveryStatus.FAILED
        assert result.notes == "Customer not available"

    def test_update_status_not_found(self, service, db_session):
        """Test updating status of non-existent delivery"""
        result = service.update_status(
            db_session,
            delivery_id=99999,
            status=DeliveryStatus.DELIVERED
        )

        assert result is None

    # ==================== COURIER ASSIGNMENT TESTS ====================

    def test_assign_to_courier(self, service, db_session, delivery_factory, courier_factory):
        """Test assigning delivery to courier"""
        courier1 = courier_factory()
        courier2 = courier_factory()
        delivery = delivery_factory(courier1, status=DeliveryStatus.PENDING)

        result = service.assign_to_courier(
            db_session,
            delivery_id=delivery.id,
            courier_id=courier2.id
        )

        assert result is not None
        assert result.courier_id == courier2.id
        assert result.status == DeliveryStatus.IN_TRANSIT
        assert result.pickup_time is not None

    def test_assign_to_courier_not_found(self, service, db_session, courier_factory):
        """Test assigning non-existent delivery"""
        courier = courier_factory()

        result = service.assign_to_courier(
            db_session,
            delivery_id=99999,
            courier_id=courier.id
        )

        assert result is None

    # ==================== DATE RANGE QUERIES ====================

    def test_get_deliveries_by_date_range(self, service, db_session, delivery_factory, courier_factory):
        """Test getting deliveries within date range"""
        courier = courier_factory()
        delivery = delivery_factory(courier)

        result = service.get_deliveries_by_date_range(
            db_session,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=1)
        )

        assert len(result) >= 1

    def test_get_deliveries_by_date_range_filtered_by_courier(self, service, db_session, delivery_factory, courier_factory):
        """Test getting deliveries in date range filtered by courier"""
        courier1 = courier_factory()
        courier2 = courier_factory()
        delivery1 = delivery_factory(courier1)
        delivery2 = delivery_factory(courier2)

        result = service.get_deliveries_by_date_range(
            db_session,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=1),
            courier_id=courier1.id
        )

        assert all(d.courier_id == courier1.id for d in result)

    # ==================== COD TESTS ====================

    def test_get_cod_deliveries(self, service, db_session, delivery_factory, courier_factory):
        """Test getting COD deliveries"""
        courier = courier_factory()
        cod_delivery = delivery_factory(courier, cod_amount=Decimal("100.00"))
        no_cod = delivery_factory(courier, cod_amount=None)

        result = service.get_cod_deliveries(db_session)

        assert len(result) >= 1
        assert all(d.cod_amount is not None and d.cod_amount > 0 for d in result)

    def test_get_cod_deliveries_by_status(self, service, db_session, delivery_factory, courier_factory):
        """Test getting COD deliveries filtered by status"""
        courier = courier_factory()
        pending_cod = delivery_factory(
            courier,
            status=DeliveryStatus.PENDING,
            cod_amount=Decimal("100.00")
        )
        delivered_cod = delivery_factory(
            courier,
            status=DeliveryStatus.DELIVERED,
            cod_amount=Decimal("150.00")
        )

        result = service.get_cod_deliveries(
            db_session,
            status=DeliveryStatus.PENDING
        )

        assert all(d.status == DeliveryStatus.PENDING for d in result)

    def test_get_cod_deliveries_by_courier(self, service, db_session, delivery_factory, courier_factory):
        """Test getting COD deliveries for specific courier"""
        courier1 = courier_factory()
        courier2 = courier_factory()
        cod1 = delivery_factory(courier1, cod_amount=Decimal("100.00"))
        cod2 = delivery_factory(courier2, cod_amount=Decimal("150.00"))

        result = service.get_cod_deliveries(db_session, courier_id=courier1.id)

        assert all(d.courier_id == courier1.id for d in result)

    # ==================== STATISTICS TESTS ====================

    def test_get_statistics_basic(self, service, db_session, delivery_factory, courier_factory):
        """Test getting basic delivery statistics"""
        courier = courier_factory()
        delivery_factory(courier, status=DeliveryStatus.PENDING)
        delivery_factory(courier, status=DeliveryStatus.IN_TRANSIT)
        delivery_factory(courier, status=DeliveryStatus.DELIVERED)
        delivery_factory(courier, status=DeliveryStatus.FAILED)

        stats = service.get_statistics(db_session)

        assert "total_deliveries" in stats
        assert "pending" in stats
        assert "in_transit" in stats
        assert "delivered" in stats
        assert "failed" in stats
        assert "success_rate" in stats

    def test_get_statistics_by_courier(self, service, db_session, delivery_factory, courier_factory):
        """Test getting statistics for specific courier"""
        courier1 = courier_factory()
        courier2 = courier_factory()
        delivery_factory(courier1, status=DeliveryStatus.DELIVERED)
        delivery_factory(courier1, status=DeliveryStatus.DELIVERED)
        delivery_factory(courier2, status=DeliveryStatus.DELIVERED)

        stats = service.get_statistics(db_session, courier_id=courier1.id)

        assert stats["delivered"] >= 2

    def test_get_statistics_by_date_range(self, service, db_session, delivery_factory, courier_factory):
        """Test getting statistics for date range"""
        courier = courier_factory()
        delivery_factory(courier, status=DeliveryStatus.DELIVERED)
        delivery_factory(courier, status=DeliveryStatus.DELIVERED)

        stats = service.get_statistics(
            db_session,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=1)
        )

        assert stats["total_deliveries"] >= 2

    def test_get_statistics_cod_amounts(self, service, db_session, delivery_factory, courier_factory):
        """Test COD amounts in statistics"""
        courier = courier_factory()
        delivery_factory(
            courier,
            status=DeliveryStatus.DELIVERED,
            cod_amount=Decimal("100.00")
        )
        delivery_factory(
            courier,
            status=DeliveryStatus.PENDING,
            cod_amount=Decimal("50.00")
        )

        stats = service.get_statistics(db_session)

        assert "total_cod_amount" in stats
        assert "collected_cod_amount" in stats
        assert "pending_cod_amount" in stats

    def test_get_statistics_success_rate(self, service, db_session, delivery_factory, courier_factory):
        """Test success rate calculation"""
        courier = courier_factory()
        # 8 delivered, 2 failed = 80% success rate
        for _ in range(8):
            delivery_factory(courier, status=DeliveryStatus.DELIVERED)
        for _ in range(2):
            delivery_factory(courier, status=DeliveryStatus.FAILED)

        stats = service.get_statistics(db_session)

        assert stats["success_rate"] == 80.0

    def test_get_statistics_zero_deliveries(self, service, db_session, courier_factory):
        """Test statistics with no deliveries"""
        courier = courier_factory()

        stats = service.get_statistics(db_session, courier_id=courier.id)

        assert stats["total_deliveries"] == 0
        assert stats["success_rate"] == 0

    # ==================== PAGINATION TESTS ====================

    def test_get_by_courier_pagination(self, service, db_session, delivery_factory, courier_factory):
        """Test pagination for courier deliveries"""
        courier = courier_factory()
        for _ in range(5):
            delivery_factory(courier)

        first_page = service.get_by_courier(db_session, courier_id=courier.id, skip=0, limit=2)
        second_page = service.get_by_courier(db_session, courier_id=courier.id, skip=2, limit=2)

        assert len(first_page) == 2
        assert len(second_page) == 2
        first_ids = {d.id for d in first_page}
        second_ids = {d.id for d in second_page}
        assert first_ids.isdisjoint(second_ids)

    def test_get_by_status_pagination(self, service, db_session, delivery_factory, courier_factory):
        """Test pagination for status-filtered deliveries"""
        courier = courier_factory()
        for _ in range(5):
            delivery_factory(courier, status=DeliveryStatus.PENDING)

        first_page = service.get_by_status(db_session, status=DeliveryStatus.PENDING, skip=0, limit=2)
        second_page = service.get_by_status(db_session, status=DeliveryStatus.PENDING, skip=2, limit=2)

        assert len(first_page) == 2
        assert len(second_page) == 2

    def test_get_cod_deliveries_pagination(self, service, db_session, delivery_factory, courier_factory):
        """Test pagination for COD deliveries"""
        courier = courier_factory()
        for _ in range(5):
            delivery_factory(courier, cod_amount=Decimal("100.00"))

        first_page = service.get_cod_deliveries(db_session, skip=0, limit=2)
        second_page = service.get_cod_deliveries(db_session, skip=2, limit=2)

        assert len(first_page) == 2
        assert len(second_page) == 2
