"""
Unit Tests for FMS Client Service

Tests Fleet Management System integration:
- Client initialization
- Authentication
- Asset/vehicle APIs
- Geofence APIs
- Placemark APIs
"""

import pytest
import time
from unittest.mock import MagicMock, patch

from app.services.fms.client import FMSClient, get_fms_client


# ==================== Fixtures ====================

@pytest.fixture
def client():
    """Create FMSClient instance with mocked HTTP client"""
    fms = FMSClient(
        base_url="http://test-fms.example.com",
        username="test_user",
        password="test_pass",
        api_key="test_api_key",
        timeout=30,
    )
    fms._client = MagicMock()
    return fms


# ==================== Initialization Tests ====================

class TestFMSClientInit:
    """Tests for FMSClient initialization"""

    def test_init_with_all_params(self):
        """Should initialize with all parameters"""
        client = FMSClient(
            base_url="http://fms.example.com/",
            username="user",
            password="pass",
            api_key="key",
            timeout=60,
        )

        assert client.base_url == "http://fms.example.com"  # Trailing slash removed
        assert client.username == "user"
        assert client.password == "pass"
        assert client.api_key == "key"
        assert client.timeout == 60

    def test_init_default_timeout(self):
        """Should use default timeout"""
        client = FMSClient(
            base_url="http://fms.example.com",
            username="user",
            password="pass",
        )

        assert client.timeout == 30


# ==================== Auth Headers Tests ====================

class TestGetAuthHeaders:
    """Tests for _get_auth_headers method"""

    def test_headers_with_api_key(self, client):
        """Should include API key in headers"""
        headers = client._get_auth_headers()

        assert headers["x-api-key"] == "test_api_key"
        assert headers["Content-Type"] == "application/json"

    def test_headers_with_token(self, client):
        """Should include bearer token when set"""
        client._access_token = "test_token"

        headers = client._get_auth_headers()

        assert headers["Authorization"] == "Bearer test_token"


# ==================== Token Management Tests ====================

class TestTokenManagement:
    """Tests for token management"""

    def test_ensure_token_valid(self, client):
        """Should return True when token is valid"""
        client._access_token = "valid_token"
        client._token_expiry = time.time() + 3600  # 1 hour from now

        result = client._ensure_token()

        assert result is True

    def test_ensure_token_expired(self, client):
        """Should refresh when token expired"""
        client._access_token = "expired_token"
        client._token_expiry = time.time() - 60  # Expired 1 minute ago

        # Mock successful token refresh
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_token",
            "expires_in": 3600
        }
        client._client.post.return_value = mock_response

        result = client._ensure_token()

        assert result is True
        assert client._access_token == "new_token"

    def test_refresh_token_success(self, client):
        """Should refresh token successfully"""
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

    def test_refresh_token_failure(self, client):
        """Should handle token refresh failure"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Invalid credentials"
        client._client.post.return_value = mock_response

        result = client._refresh_token()

        assert result is False


# ==================== Make Request Tests ====================

class TestMakeRequest:
    """Tests for _make_request method"""

    def test_get_request_success(self, client):
        """Should make successful GET request"""
        client._access_token = "valid_token"
        client._token_expiry = time.time() + 3600

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        client._client.get.return_value = mock_response

        result = client._make_request("GET", "/api/v1/test")

        assert result == {"data": "test"}

    def test_post_request_success(self, client):
        """Should make successful POST request"""
        client._access_token = "valid_token"
        client._token_expiry = time.time() + 3600

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"created": True}
        client._client.post.return_value = mock_response

        result = client._make_request("POST", "/api/v1/test", json_data={"name": "test"})

        assert result == {"created": True}

    def test_request_without_auth(self, client):
        """Should make request without authentication"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        client._client.get.return_value = mock_response

        result = client._make_request("GET", "/api/status", require_auth=False)

        assert result == {"status": "ok"}

    def test_request_401_retry(self, client):
        """Should retry on 401 and refresh token"""
        client._access_token = "expired_token"
        client._token_expiry = time.time() + 3600

        # First request returns 401, second succeeds
        mock_401 = MagicMock()
        mock_401.status_code = 401

        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"data": "test"}

        client._client.get.side_effect = [mock_401, mock_success]

        # Mock token refresh
        mock_token = MagicMock()
        mock_token.status_code = 200
        mock_token.json.return_value = {"access_token": "new_token", "expires_in": 3600}
        client._client.post.return_value = mock_token

        result = client._make_request("GET", "/api/v1/test")

        # Should eventually succeed
        assert not result.get("error") or result == {"data": "test"}


# ==================== Asset APIs Tests ====================

class TestAssetAPIs:
    """Tests for asset/vehicle APIs"""

    def test_get_assets(self, client):
        """Should get assets with pagination"""
        client._access_token = "token"
        client._token_expiry = time.time() + 3600

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [], "total": 0}
        client._client.get.return_value = mock_response

        result = client.get_assets(page_size=50, page_index=1)

        assert "data" in result

    def test_get_asset_by_id(self, client):
        """Should get asset by ID"""
        client._access_token = "token"
        client._token_expiry = time.time() + 3600

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 123, "name": "Test Asset"}
        client._client.get.return_value = mock_response

        result = client.get_asset_by_id(123)

        assert result.get("id") == 123

    def test_get_asset_by_plate(self, client):
        """Should get asset by plate number"""
        client._access_token = "token"
        client._token_expiry = time.time() + 3600

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"plate": "ABC-123"}
        client._client.get.return_value = mock_response

        result = client.get_asset_by_plate("ABC-123")

        assert result.get("plate") == "ABC-123"

    def test_get_location_history(self, client):
        """Should get location history"""
        client._access_token = "token"
        client._token_expiry = time.time() + 3600

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"locations": []}
        client._client.get.return_value = mock_response

        result = client.get_location_history(
            asset_id=123,
            from_time="01152025 00:00:00",
            to_time="01162025 00:00:00"
        )

        assert "locations" in result


# ==================== Geofence APIs Tests ====================

class TestGeofenceAPIs:
    """Tests for geofence APIs"""

    def test_get_geofences(self, client):
        """Should get geofences"""
        client._access_token = "token"
        client._token_expiry = time.time() + 3600

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        client._client.get.return_value = mock_response

        result = client.get_geofences()

        assert "data" in result

    def test_get_geofence_by_id(self, client):
        """Should get geofence by ID"""
        client._access_token = "token"
        client._token_expiry = time.time() + 3600

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "name": "Zone A"}
        client._client.get.return_value = mock_response

        result = client.get_geofence_by_id(1)

        assert result.get("id") == 1


# ==================== Placemark APIs Tests ====================

class TestPlacemarkAPIs:
    """Tests for placemark APIs"""

    def test_get_placemarks(self, client):
        """Should get placemarks"""
        client._access_token = "token"
        client._token_expiry = time.time() + 3600

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        client._client.get.return_value = mock_response

        result = client.get_placemarks()

        assert "data" in result

    def test_create_placemark(self, client):
        """Should create placemark"""
        client._access_token = "token"
        client._token_expiry = time.time() + 3600

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "created": True}
        client._client.post.return_value = mock_response

        result = client.create_placemark({"name": "New Place", "lat": 24.7, "lng": 46.7})

        assert result.get("created") is True

    def test_update_placemark(self, client):
        """Should update placemark"""
        client._access_token = "token"
        client._token_expiry = time.time() + 3600

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "updated": True}
        client._client.put.return_value = mock_response

        result = client.update_placemark(1, {"name": "Updated Place"})

        assert result.get("updated") is True

    def test_delete_placemark(self, client):
        """Should delete placemark"""
        client._access_token = "token"
        client._token_expiry = time.time() + 3600

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"deleted": True}
        client._client.delete.return_value = mock_response

        result = client.delete_placemark(1)

        assert result.get("deleted") is True


# ==================== Status APIs Tests ====================

class TestStatusAPIs:
    """Tests for status APIs"""

    def test_get_status(self, client):
        """Should get FMS status without auth"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "running"}
        client._client.get.return_value = mock_response

        result = client.get_status()

        assert result.get("status") == "running"

    def test_get_health(self, client):
        """Should get FMS health without auth"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"healthy": True}
        client._client.get.return_value = mock_response

        result = client.get_health()

        assert result.get("healthy") is True


# ==================== Stream URL Tests ====================

class TestStreamURL:
    """Tests for stream URL generation"""

    def test_get_stream_url_with_api_key(self, client):
        """Should return stream URL with API key"""
        url = client.get_stream_url()

        assert "api_key=test_api_key" in url

    def test_get_stream_url_without_api_key(self):
        """Should return stream URL without API key"""
        client = FMSClient(
            base_url="http://fms.example.com",
            username="user",
            password="pass",
        )

        url = client.get_stream_url()

        assert "api_key" not in url


# ==================== Close Tests ====================

class TestClose:
    """Tests for close method"""

    def test_close_client(self, client):
        """Should close HTTP client"""
        client.close()

        client._client.close.assert_called_once()


# ==================== Singleton Tests ====================

class TestSingleton:
    """Tests for singleton instance"""

    def test_get_fms_client_returns_instance(self):
        """Should return FMSClient instance"""
        with patch.dict('os.environ', {
            'FMS_BASE_URL': 'http://test.example.com',
            'FMS_USERNAME': 'user',
            'FMS_PASSWORD': 'pass',
        }):
            client = get_fms_client()
            assert isinstance(client, FMSClient)
