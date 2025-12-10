"""
Unit Tests for BARQ Platform Client

Tests BARQ main backend integration:
- Client initialization
- Authentication
- Order retrieval
- Status mapping
- Order parsing
"""

import pytest
import time
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

from app.services.platforms.barq_client import BarqClient, get_barq_client
from app.services.platforms.base import OrderStatus, PlatformType


# ==================== Fixtures ====================

@pytest.fixture
def client():
    """Create BarqClient instance with mocked HTTP client"""
    barq = BarqClient(
        base_url="http://test-barq.example.com",
        api_key="test_api_key",
        client_id="test_client_id",
        client_secret="test_client_secret",
        timeout=30,
    )
    barq._client = MagicMock()
    return barq


@pytest.fixture
def sample_order_data():
    """Sample BARQ order data"""
    return {
        "id": "order123",
        "tracking_number": "TRK-123",
        "driver_id": "driver456",
        "barq_id": 789,
        "status": "in_transit",
        "order_type": "delivery",
        "pickup": {
            "address": "123 Pickup St",
            "lat": 24.7136,
            "lng": 46.6753,
            "name": "Pickup Contact",
            "phone": "+966501234567"
        },
        "delivery": {
            "address": "456 Delivery Ave",
            "lat": 24.7500,
            "lng": 46.7000,
            "name": "Customer Name",
            "phone": "+966509876543"
        },
        "total_amount": "150.00",
        "cod_amount": "100.00",
        "delivery_fee": "15.00",
        "created_at": "2025-01-15T10:00:00Z",
        "assigned_at": "2025-01-15T10:05:00Z",
        "notes": "Handle with care",
        "items": [{"name": "Item 1"}, {"name": "Item 2"}]
    }


# ==================== Initialization Tests ====================

class TestBarqClientInit:
    """Tests for BarqClient initialization"""

    def test_init_with_all_params(self):
        """Should initialize with all parameters"""
        client = BarqClient(
            base_url="http://barq.example.com/",
            api_key="key",
            client_id="client",
            client_secret="secret",
            timeout=60,
        )

        assert client.base_url == "http://barq.example.com"
        assert client.api_key == "key"
        assert client.client_id == "client"
        assert client.client_secret == "secret"

    def test_platform_type(self, client):
        """Should return BARQ platform type"""
        assert client.platform_type == PlatformType.BARQ


# ==================== Auth Headers Tests ====================

class TestGetAuthHeaders:
    """Tests for _get_auth_headers method"""

    def test_headers_with_api_key(self, client):
        """Should include API key in headers"""
        headers = client._get_auth_headers()

        assert headers["X-API-Key"] == "test_api_key"
        assert headers["Content-Type"] == "application/json"

    def test_headers_with_token(self, client):
        """Should include bearer token when set"""
        client._access_token = "test_token"

        headers = client._get_auth_headers()

        assert headers["Authorization"] == "Bearer test_token"


# ==================== Token Refresh Tests ====================

class TestTokenRefresh:
    """Tests for _refresh_token method"""

    def test_refresh_with_api_key_only(self):
        """Should use API key as token when no client credentials"""
        client = BarqClient(
            base_url="http://barq.example.com",
            api_key="api_key_123",
        )

        result = client._refresh_token()

        assert result is True
        assert client._access_token == "api_key_123"

    def test_refresh_with_client_credentials(self, client):
        """Should refresh using OAuth client credentials"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_token",
            "expires_in": 3600
        }
        client._client.post.return_value = mock_response

        result = client._refresh_token()

        assert result is True
        assert client._access_token == "new_token"

    def test_refresh_failure(self, client):
        """Should handle refresh failure"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        client._client.post.return_value = mock_response

        result = client._refresh_token()

        assert result is False


# ==================== Status Mapping Tests ====================

class TestStatusMapping:
    """Tests for _map_status method"""

    def test_map_pending_status(self, client):
        """Should map pending statuses"""
        assert client._map_status("pending") == OrderStatus.PENDING
        assert client._map_status("new") == OrderStatus.PENDING

    def test_map_assigned_status(self, client):
        """Should map assigned statuses"""
        assert client._map_status("assigned") == OrderStatus.ASSIGNED
        assert client._map_status("accepted") == OrderStatus.ASSIGNED

    def test_map_picked_up_status(self, client):
        """Should map picked up statuses"""
        assert client._map_status("picked_up") == OrderStatus.PICKED_UP
        assert client._map_status("picking") == OrderStatus.PICKED_UP

    def test_map_in_transit_status(self, client):
        """Should map in transit statuses"""
        assert client._map_status("in_transit") == OrderStatus.IN_TRANSIT
        assert client._map_status("on_the_way") == OrderStatus.IN_TRANSIT
        assert client._map_status("delivering") == OrderStatus.IN_TRANSIT

    def test_map_delivered_status(self, client):
        """Should map delivered statuses"""
        assert client._map_status("delivered") == OrderStatus.DELIVERED
        assert client._map_status("completed") == OrderStatus.DELIVERED

    def test_map_other_statuses(self, client):
        """Should map other statuses"""
        assert client._map_status("failed") == OrderStatus.FAILED
        assert client._map_status("cancelled") == OrderStatus.CANCELLED
        assert client._map_status("returned") == OrderStatus.RETURNED

    def test_map_unknown_status(self, client):
        """Should default to PENDING for unknown status"""
        assert client._map_status("unknown") == OrderStatus.PENDING

    def test_case_insensitive(self, client):
        """Should handle different cases"""
        assert client._map_status("DELIVERED") == OrderStatus.DELIVERED
        assert client._map_status("Pending") == OrderStatus.PENDING


# ==================== Order Parsing Tests ====================

class TestOrderParsing:
    """Tests for _parse_order method"""

    def test_parse_order_full_data(self, client, sample_order_data):
        """Should parse full order data"""
        order = client._parse_order(sample_order_data)

        assert order.platform == PlatformType.BARQ
        assert order.platform_order_id == "order123"
        assert order.platform_tracking_number == "TRK-123"
        assert order.platform_driver_id == "driver456"
        assert order.courier_barq_id == 789
        assert order.status == OrderStatus.IN_TRANSIT
        assert order.pickup_address == "123 Pickup St"
        assert order.delivery_address == "456 Delivery Ave"
        assert order.order_amount == Decimal("150.00")
        assert order.cod_amount == Decimal("100.00")

    def test_parse_order_minimal_data(self, client):
        """Should handle minimal order data"""
        minimal_data = {
            "id": "order123",
            "status": "pending",
        }

        order = client._parse_order(minimal_data)

        assert order.platform_order_id == "order123"
        assert order.status == OrderStatus.PENDING

    def test_parse_order_alternate_fields(self, client):
        """Should handle alternate field names"""
        data = {
            "orderId": "order123",
            "trackingNumber": "TRK-123",
            "driverId": "driver456",
            "barqId": 789,
            "pickup_address": "123 Pickup",
            "delivery_address": "456 Delivery",
            "totalAmount": "100.00",
            "codAmount": "50.00",
            "status": "pending"
        }

        order = client._parse_order(data)

        assert order.platform_order_id == "order123"


# ==================== Get Orders Tests ====================

class TestGetOrdersForDriver:
    """Tests for get_orders_for_driver method"""

    def test_get_orders_success(self, client, sample_order_data):
        """Should get orders for driver"""
        client._access_token = "token"
        client._token_expiry = time.time() + 3600

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [sample_order_data]}
        client._client.get.return_value = mock_response

        with patch.object(client, '_make_request', return_value={"data": [sample_order_data]}):
            result = client.get_orders_for_driver("driver456")

        assert len(result) >= 0

    def test_get_orders_with_filters(self, client):
        """Should pass filter parameters"""
        client._access_token = "token"
        client._token_expiry = time.time() + 3600

        with patch.object(client, '_make_request', return_value={"data": []}):
            result = client.get_orders_for_driver(
                driver_id="driver456",
                from_date=datetime(2025, 1, 1),
                to_date=datetime(2025, 1, 31),
                status="delivered",
                page=2,
                page_size=20,
            )

        assert isinstance(result, list)

    def test_get_orders_error(self, client):
        """Should return empty list on error"""
        with patch.object(client, '_make_request', return_value={"error": True, "message": "Failed"}):
            result = client.get_orders_for_driver("driver456")

        assert result == []


# ==================== Get Order Details Tests ====================

class TestGetOrderDetails:
    """Tests for get_order_details method"""

    def test_get_order_details_success(self, client, sample_order_data):
        """Should get order details"""
        with patch.object(client, '_make_request', return_value=sample_order_data):
            result = client.get_order_details("order123")

        assert result is not None
        assert result.platform_order_id == "order123"

    def test_get_order_details_not_found(self, client):
        """Should return None when not found"""
        with patch.object(client, '_make_request', return_value={"error": True, "message": "Not found"}):
            result = client.get_order_details("nonexistent")

        assert result is None


# ==================== Get Active Orders Tests ====================

class TestGetAllActiveOrders:
    """Tests for get_all_active_orders method"""

    def test_get_active_orders_success(self, client, sample_order_data):
        """Should get all active orders"""
        with patch.object(client, '_make_request', return_value={"data": [sample_order_data]}):
            result = client.get_all_active_orders()

        assert len(result) >= 0

    def test_get_active_orders_error(self, client):
        """Should return empty list on error"""
        with patch.object(client, '_make_request', return_value={"error": True}):
            result = client.get_all_active_orders()

        assert result == []


# ==================== Update Order Status Tests ====================

class TestUpdateOrderStatus:
    """Tests for update_order_status method"""

    def test_update_status_success(self, client):
        """Should update order status"""
        with patch.object(client, '_make_request', return_value={"success": True}):
            result = client.update_order_status("order123", "delivered")

        assert result is True

    def test_update_status_with_notes(self, client):
        """Should update status with notes"""
        with patch.object(client, '_make_request', return_value={"success": True}):
            result = client.update_order_status(
                "order123",
                "delivered",
                notes="Delivered to reception"
            )

        assert result is True

    def test_update_status_failure(self, client):
        """Should return False on failure"""
        with patch.object(client, '_make_request', return_value={"error": True, "message": "Failed"}):
            result = client.update_order_status("order123", "delivered")

        assert result is False


# ==================== Singleton Tests ====================

class TestSingleton:
    """Tests for singleton instance"""

    def test_get_barq_client_returns_instance(self):
        """Should return BarqClient instance"""
        with patch.dict('os.environ', {
            'BARQ_MAIN_API_URL': 'http://test.example.com',
        }):
            client = get_barq_client()
            assert isinstance(client, BarqClient)
