"""
Integration Tests for Operations Delivery API

Tests delivery management endpoints including creation, tracking, and status updates.

Author: BARQ QA Team
Last Updated: 2025-12-02
"""

import pytest
from datetime import datetime, timedelta

from app.models.operations.delivery import DeliveryStatus
from tests.utils.factories import (
    CourierFactory,
    DeliveryFactory,
    AdminUserFactory,
    UserFactory
)
from tests.utils.api_helpers import (
    make_get_request,
    make_post_request,
    make_put_request,
    make_patch_request,
    assert_success_response,
    assert_not_found,
    assert_validation_error,
    create_test_token
)


@pytest.mark.integration
@pytest.mark.operations
class TestDeliveryAPI:
    """Test Delivery Management API endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self, db_session, client):
        """Setup test data"""
        self.db = db_session
        self.client = client

        # Create test users
        self.admin_user = AdminUserFactory.create()
        self.regular_user = UserFactory.create()

        # Create test courier
        self.courier = CourierFactory.create()

        # Create tokens
        self.admin_token = create_test_token(
            self.admin_user.id,
            self.admin_user.email,
            "admin"
        )
        self.user_token = create_test_token(
            self.regular_user.id,
            self.regular_user.email,
            "user"
        )

        self.db.commit()

    def test_list_deliveries(self):
        """Test listing all deliveries"""
        DeliveryFactory.create(courier_id=self.courier.id)
        DeliveryFactory.create(courier_id=self.courier.id)
        DeliveryFactory.create(courier_id=self.courier.id)
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/operations/deliveries",
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()

        assert len(data.get("items", data)) >= 3

    def test_list_deliveries_filter_by_status(self):
        """Test filtering deliveries by status"""
        DeliveryFactory.create(courier_id=self.courier.id, status=DeliveryStatus.PENDING)
        DeliveryFactory.create(courier_id=self.courier.id, status=DeliveryStatus.DELIVERED)
        DeliveryFactory.create(courier_id=self.courier.id, status=DeliveryStatus.PENDING)
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/operations/deliveries",
            self.admin_token,
            params={"status": "pending"}
        )

        assert_success_response(response)
        data = response.json()
        items = data.get("items", data)

        assert len(items) == 2
        assert all(item["status"] == "pending" for item in items)

    def test_list_deliveries_filter_by_courier(self):
        """Test filtering deliveries by courier"""
        courier2 = CourierFactory.create()
        self.db.commit()

        DeliveryFactory.create(courier_id=self.courier.id)
        DeliveryFactory.create(courier_id=self.courier.id)
        DeliveryFactory.create(courier_id=courier2.id)
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/operations/deliveries",
            self.admin_token,
            params={"courier_id": self.courier.id}
        )

        assert_success_response(response)
        data = response.json()
        items = data.get("items", data)

        assert len(items) == 2

    def test_create_delivery_success(self):
        """Test creating a new delivery"""
        delivery_data = {
            "courier_id": self.courier.id,
            "tracking_number": "TRK-TEST-001",
            "pickup_address": "123 Pickup St, Riyadh",
            "delivery_address": "456 Delivery Ave, Riyadh",
            "customer_name": "Ahmad Hassan",
            "customer_phone": "+966501234567",
            "cod_amount": 250.00
        }

        response = make_post_request(
            self.client,
            "/api/v1/operations/deliveries",
            delivery_data,
            self.admin_token
        )

        assert response.status_code == 201
        data = response.json()

        assert data["tracking_number"] == "TRK-TEST-001"
        assert data["status"] == "pending"
        assert "id" in data

    def test_create_delivery_duplicate_tracking_number(self):
        """Test creating delivery with duplicate tracking number"""
        DeliveryFactory.create(tracking_number="TRK-DUPLICATE")
        self.db.commit()

        delivery_data = {
            "courier_id": self.courier.id,
            "tracking_number": "TRK-DUPLICATE",
            "pickup_address": "Test",
            "delivery_address": "Test",
            "customer_name": "Test",
            "customer_phone": "+966501234567"
        }

        response = make_post_request(
            self.client,
            "/api/v1/operations/deliveries",
            delivery_data,
            self.admin_token
        )

        assert response.status_code in [400, 409]

    def test_create_delivery_missing_required_fields(self):
        """Test creating delivery with missing required fields"""
        incomplete_data = {
            "tracking_number": "TRK-TEST-002"
        }

        response = make_post_request(
            self.client,
            "/api/v1/operations/deliveries",
            incomplete_data,
            self.admin_token
        )

        assert_validation_error(response)

    def test_get_delivery_by_id(self):
        """Test retrieving a delivery by ID"""
        delivery = DeliveryFactory.create(
            courier_id=self.courier.id,
            tracking_number="TRK-GET-001"
        )
        self.db.commit()

        response = make_get_request(
            self.client,
            f"/api/v1/operations/deliveries/{delivery.id}",
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()

        assert data["id"] == delivery.id
        assert data["tracking_number"] == "TRK-GET-001"

    def test_get_delivery_by_tracking_number(self):
        """Test retrieving delivery by tracking number"""
        delivery = DeliveryFactory.create(
            courier_id=self.courier.id,
            tracking_number="TRK-TRACK-001"
        )
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/operations/deliveries/track/TRK-TRACK-001",
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()

        assert data["tracking_number"] == "TRK-TRACK-001"

    def test_get_delivery_not_found(self):
        """Test retrieving non-existent delivery"""
        response = make_get_request(
            self.client,
            "/api/v1/operations/deliveries/99999",
            self.admin_token
        )

        assert_not_found(response)

    def test_update_delivery_status_to_picked_up(self):
        """Test updating delivery status to picked up"""
        delivery = DeliveryFactory.create(
            courier_id=self.courier.id,
            status=DeliveryStatus.PENDING
        )
        self.db.commit()

        response = make_patch_request(
            self.client,
            f"/api/v1/operations/deliveries/{delivery.id}/status",
            {"status": "picked_up"},
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()

        assert data["status"] == "picked_up"

    def test_update_delivery_status_to_in_transit(self):
        """Test updating delivery status to in transit"""
        delivery = DeliveryFactory.create(
            courier_id=self.courier.id,
            status=DeliveryStatus.PICKED_UP
        )
        self.db.commit()

        response = make_patch_request(
            self.client,
            f"/api/v1/operations/deliveries/{delivery.id}/status",
            {"status": "in_transit"},
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()

        assert data["status"] == "in_transit"

    def test_update_delivery_status_to_delivered(self):
        """Test updating delivery status to delivered"""
        delivery = DeliveryFactory.create(
            courier_id=self.courier.id,
            status=DeliveryStatus.IN_TRANSIT
        )
        self.db.commit()

        response = make_patch_request(
            self.client,
            f"/api/v1/operations/deliveries/{delivery.id}/status",
            {
                "status": "delivered",
                "delivery_notes": "Delivered successfully"
            },
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()

        assert data["status"] == "delivered"

    def test_update_delivery_status_to_failed(self):
        """Test updating delivery status to failed"""
        delivery = DeliveryFactory.create(
            courier_id=self.courier.id,
            status=DeliveryStatus.IN_TRANSIT
        )
        self.db.commit()

        response = make_patch_request(
            self.client,
            f"/api/v1/operations/deliveries/{delivery.id}/status",
            {
                "status": "failed",
                "failure_reason": "Customer not available"
            },
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()

        assert data["status"] == "failed"

    def test_assign_delivery_to_courier(self):
        """Test assigning delivery to a courier"""
        delivery = DeliveryFactory.create(courier_id=None)
        self.db.commit()

        response = make_patch_request(
            self.client,
            f"/api/v1/operations/deliveries/{delivery.id}/assign",
            {"courier_id": self.courier.id},
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()

        assert data["courier_id"] == self.courier.id

    def test_reassign_delivery_to_different_courier(self):
        """Test reassigning delivery to different courier"""
        courier2 = CourierFactory.create()
        self.db.commit()

        delivery = DeliveryFactory.create(courier_id=self.courier.id)
        self.db.commit()

        response = make_patch_request(
            self.client,
            f"/api/v1/operations/deliveries/{delivery.id}/assign",
            {"courier_id": courier2.id},
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()

        assert data["courier_id"] == courier2.id

    def test_get_delivery_statistics(self):
        """Test getting delivery statistics"""
        DeliveryFactory.create(courier_id=self.courier.id, status=DeliveryStatus.PENDING)
        DeliveryFactory.create(courier_id=self.courier.id, status=DeliveryStatus.DELIVERED)
        DeliveryFactory.create(courier_id=self.courier.id, status=DeliveryStatus.FAILED)
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/operations/deliveries/statistics",
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()

        assert "total_deliveries" in data
        assert "pending_deliveries" in data
        assert "delivered_deliveries" in data

    def test_get_courier_deliveries(self):
        """Test getting deliveries for a specific courier"""
        DeliveryFactory.create(courier_id=self.courier.id)
        DeliveryFactory.create(courier_id=self.courier.id)
        self.db.commit()

        response = make_get_request(
            self.client,
            f"/api/v1/operations/couriers/{self.courier.id}/deliveries",
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()

        assert len(data.get("items", data)) >= 2

    def test_search_deliveries_by_tracking_number(self):
        """Test searching deliveries by tracking number"""
        DeliveryFactory.create(courier_id=self.courier.id, tracking_number="TRK-SEARCH-001")
        DeliveryFactory.create(courier_id=self.courier.id, tracking_number="TRK-SEARCH-002")
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/operations/deliveries",
            self.admin_token,
            params={"search": "TRK-SEARCH"}
        )

        assert_success_response(response)
        data = response.json()
        items = data.get("items", data)

        assert len(items) == 2

    def test_get_pending_deliveries(self):
        """Test getting pending deliveries"""
        DeliveryFactory.create(courier_id=self.courier.id, status=DeliveryStatus.PENDING)
        DeliveryFactory.create(courier_id=self.courier.id, status=DeliveryStatus.DELIVERED)
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/operations/deliveries/pending",
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()

        assert len(data) >= 1

    def test_bulk_update_delivery_status(self):
        """Test bulk updating delivery statuses"""
        delivery1 = DeliveryFactory.create(courier_id=self.courier.id, status=DeliveryStatus.PENDING)
        delivery2 = DeliveryFactory.create(courier_id=self.courier.id, status=DeliveryStatus.PENDING)
        self.db.commit()

        bulk_update_data = {
            "delivery_ids": [delivery1.id, delivery2.id],
            "status": "picked_up"
        }

        response = make_post_request(
            self.client,
            "/api/v1/operations/deliveries/bulk-update-status",
            bulk_update_data,
            self.admin_token
        )

        assert_success_response(response)

    def test_export_deliveries_csv(self):
        """Test exporting deliveries to CSV"""
        DeliveryFactory.create(courier_id=self.courier.id)
        DeliveryFactory.create(courier_id=self.courier.id)
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/operations/deliveries/export",
            self.admin_token,
            params={"format": "csv"}
        )

        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
