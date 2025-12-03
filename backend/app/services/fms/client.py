"""
FMS Client - Integration with machinettalk Fleet Management System
Handles authentication, caching, and API calls to the FMS backend.
"""

import logging
import os
import time
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class FMSClient:
    """
    Client for machinettalk FMS API.
    Handles OAuth authentication, token caching, and API requests.
    """

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
    ):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.api_key = api_key
        self.timeout = timeout

        # Token management
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[float] = None
        self._token_lock = False

        # HTTP client
        self._client = httpx.Client(timeout=timeout)

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests."""
        headers = {"Content-Type": "application/json"}

        if self.api_key:
            headers["x-api-key"] = self.api_key

        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"

        return headers

    def _ensure_token(self) -> bool:
        """Ensure we have a valid access token, refreshing if necessary."""
        # Check if token is still valid (with 60 second buffer)
        if self._access_token and self._token_expiry:
            if time.time() < (self._token_expiry - 60):
                return True

        # Need to refresh token
        return self._refresh_token()

    def _refresh_token(self) -> bool:
        """Refresh the OAuth access token."""
        if self._token_lock:
            # Wait for other refresh to complete
            time.sleep(0.5)
            return self._access_token is not None

        self._token_lock = True
        try:
            # OAuth 2.0 Password Grant - token endpoint is at /token (not /oauth/token)
            auth_url = f"{self.base_url}/token"

            # URL-encoded form data
            import urllib.parse

            data = urllib.parse.urlencode(
                {
                    "grant_type": "password",
                    "username": self.username,
                    "password": self.password,
                }
            )
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            response = self._client.post(auth_url, content=data, headers=headers)

            if response.status_code == 200:
                token_data = response.json()
                self._access_token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", 3600)
                self._token_expiry = time.time() + expires_in
                logger.info("FMS token refreshed successfully")
                return True
            else:
                logger.error(f"FMS token refresh failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"FMS token refresh error: {e}")
            return False
        finally:
            self._token_lock = False

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        require_auth: bool = True,
    ) -> Dict[str, Any]:
        """Make an authenticated request to the FMS API."""
        if require_auth and not self._ensure_token():
            return {"error": True, "message": "Authentication failed"}

        url = f"{self.base_url}{endpoint}"
        headers = self._get_auth_headers()

        try:
            if method.upper() == "GET":
                response = self._client.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = self._client.post(url, headers=headers, params=params, json=json_data)
            elif method.upper() == "PUT":
                response = self._client.put(url, headers=headers, params=params, json=json_data)
            elif method.upper() == "DELETE":
                response = self._client.delete(url, headers=headers, params=params)
            else:
                return {"error": True, "message": f"Unsupported method: {method}"}

            if response.status_code == 401:
                # Token expired, retry once
                self._access_token = None
                if self._refresh_token():
                    return self._make_request(method, endpoint, params, json_data, require_auth)
                return {"error": True, "message": "Authentication failed"}

            if response.status_code >= 400:
                return {
                    "error": True,
                    "message": f"FMS API error: {response.status_code}",
                    "details": response.text,
                }

            return response.json()

        except httpx.TimeoutException:
            logger.error(f"FMS request timeout: {endpoint}")
            return {"error": True, "message": "Request timeout"}
        except Exception as e:
            logger.error(f"FMS request error: {e}")
            return {"error": True, "message": str(e)}

    # ==================== Asset/Vehicle APIs ====================

    def get_assets(
        self,
        page_size: int = 100,
        page_index: int = 1,  # FMS API uses 1-based pagination
    ) -> Dict[str, Any]:
        """Get all tracked assets/vehicles."""
        params = {
            "pageSize": page_size,
            "pageIndex": page_index,
        }
        return self._make_request("GET", "/api/v1/assets", params=params)

    def get_asset_by_id(self, asset_id: int) -> Dict[str, Any]:
        """Get asset details by ID."""
        return self._make_request("GET", f"/api/v1/assets/{asset_id}")

    def get_asset_by_plate(self, plate_number: str) -> Dict[str, Any]:
        """Get asset details by plate number."""
        return self._make_request("GET", f"/api/v1/assets/{plate_number}/platenumber")

    def get_location_history(
        self,
        asset_id: int,
        from_time: str,
        to_time: str,
    ) -> Dict[str, Any]:
        """
        Get location history for an asset.

        Args:
            asset_id: The asset ID
            from_time: Start time (MMddYYYY HH:mm:ss format)
            to_time: End time (MMddYYYY HH:mm:ss format)
        """
        params = {
            "from": from_time,
            "to": to_time,
        }
        return self._make_request(
            "GET", f"/api/v1/assets/{asset_id}/locationhistory", params=params
        )

    # ==================== Geofence APIs ====================

    def get_geofences(
        self,
        page_size: int = 100,
        page_index: int = 1,  # FMS API uses 1-based pagination
    ) -> Dict[str, Any]:
        """Get all geofences/zones."""
        params = {
            "pageSize": page_size,
            "pageIndex": page_index,
        }
        return self._make_request("GET", "/api/v1/geofences", params=params)

    def get_geofence_by_id(self, zone_id: int) -> Dict[str, Any]:
        """Get geofence details by ID."""
        return self._make_request("GET", f"/api/v1/geofences/{zone_id}")

    # ==================== Placemark APIs ====================

    def get_placemarks(
        self,
        page_size: int = 100,
        page_index: int = 1,  # FMS API uses 1-based pagination
    ) -> Dict[str, Any]:
        """Get all placemarks."""
        params = {
            "pageSize": page_size,
            "pageIndex": page_index,
        }
        return self._make_request("GET", "/api/v1/placemarks", params=params)

    def get_placemark_by_id(self, placemark_id: int) -> Dict[str, Any]:
        """Get placemark details by ID."""
        return self._make_request("GET", f"/api/v1/placemarks/{placemark_id}")

    def create_placemark(self, placemark_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new placemark."""
        return self._make_request("POST", "/api/v1/placemarks", json_data=placemark_data)

    def update_placemark(self, placemark_id: int, placemark_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a placemark."""
        return self._make_request(
            "PUT", f"/api/v1/placemarks/{placemark_id}", json_data=placemark_data
        )

    def delete_placemark(self, placemark_id: int) -> Dict[str, Any]:
        """Delete a placemark."""
        return self._make_request("DELETE", f"/api/v1/placemarks/{placemark_id}")

    # ==================== Status APIs ====================

    def get_status(self) -> Dict[str, Any]:
        """Get FMS system status."""
        return self._make_request("GET", "/api/status", require_auth=False)

    def get_health(self) -> Dict[str, Any]:
        """Get FMS health check."""
        return self._make_request("GET", "/api/health", require_auth=False)

    # ==================== Stream URL ====================

    def get_stream_url(self) -> str:
        """Get the SSE stream URL for real-time updates."""
        if self.api_key:
            return f"{self.base_url}/api/stream/assets?api_key={self.api_key}"
        return f"{self.base_url}/api/stream/assets"

    def close(self):
        """Close the HTTP client."""
        self._client.close()


# Singleton instance
_fms_client: Optional[FMSClient] = None
_fms_client_url: Optional[str] = None


def get_fms_client() -> FMSClient:
    """Get or create the FMS client singleton."""
    global _fms_client, _fms_client_url

    current_url = os.getenv("FMS_BASE_URL", "http://localhost:3003")

    # Recreate client if URL changed (allows hot-reload of config)
    if _fms_client is None or _fms_client_url != current_url:
        if _fms_client:
            _fms_client.close()
        _fms_client = FMSClient(
            base_url=current_url,
            username=os.getenv("FMS_USERNAME", ""),
            password=os.getenv("FMS_PASSWORD", ""),
            api_key=os.getenv("FMS_API_KEY", ""),
            timeout=int(os.getenv("FMS_TIMEOUT", "30")),
        )
        _fms_client_url = current_url

    return _fms_client
