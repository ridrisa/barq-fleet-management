"""
Base Platform Client
Abstract base class for all delivery platform integrations.
"""

import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class PlatformType(str, Enum):
    """Supported delivery platforms"""
    BARQ = "barq"
    JAHEZ = "jahez"
    SANED = "saned"
    HUNGER = "hunger"
    MRSOOL = "mrsool"


class OrderStatus(str, Enum):
    """Unified order status across platforms"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETURNED = "returned"


class PlatformOrder(BaseModel):
    """Unified order model across all platforms"""

    # Platform identification
    platform: PlatformType
    platform_order_id: str = Field(..., description="Order ID from the platform")
    platform_tracking_number: Optional[str] = None

    # Courier assignment
    platform_driver_id: Optional[str] = Field(None, description="Driver ID on the platform")
    courier_barq_id: Optional[str] = Field(None, description="Mapped BARQ courier ID")

    # Order details
    status: OrderStatus = OrderStatus.PENDING
    order_type: Optional[str] = None  # food, ecommerce, express, etc.

    # Addresses
    pickup_address: str
    pickup_lat: Optional[float] = None
    pickup_lng: Optional[float] = None
    pickup_contact_name: Optional[str] = None
    pickup_contact_phone: Optional[str] = None

    delivery_address: str
    delivery_lat: Optional[float] = None
    delivery_lng: Optional[float] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None

    # Financial
    order_amount: Decimal = Decimal("0")
    cod_amount: Decimal = Decimal("0")
    delivery_fee: Decimal = Decimal("0")

    # Timestamps
    created_at: datetime
    assigned_at: Optional[datetime] = None
    picked_up_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

    # Additional data
    notes: Optional[str] = None
    items_count: int = 0
    raw_data: Optional[Dict[str, Any]] = None  # Original platform response

    class Config:
        use_enum_values = True


class BasePlatformClient(ABC):
    """
    Abstract base class for platform API clients.
    All platform integrations should inherit from this class.
    """

    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        # Token management
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[float] = None
        self._token_lock = False

        # HTTP client
        self._client = httpx.Client(timeout=timeout)

        # Statistics
        self.request_count = 0
        self.error_count = 0
        self.last_request_time: Optional[datetime] = None

    @property
    @abstractmethod
    def platform_type(self) -> PlatformType:
        """Return the platform type identifier."""
        pass

    @abstractmethod
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests."""
        pass

    @abstractmethod
    def _refresh_token(self) -> bool:
        """Refresh the authentication token."""
        pass

    @abstractmethod
    def get_orders_for_driver(
        self,
        driver_id: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        status: Optional[str] = None,
    ) -> List[PlatformOrder]:
        """
        Fetch orders for a specific driver from the platform.

        Args:
            driver_id: Platform-specific driver ID
            from_date: Start date filter
            to_date: End date filter
            status: Order status filter

        Returns:
            List of PlatformOrder objects
        """
        pass

    @abstractmethod
    def get_order_details(self, order_id: str) -> Optional[PlatformOrder]:
        """
        Get detailed information for a specific order.

        Args:
            order_id: Platform-specific order ID

        Returns:
            PlatformOrder object or None if not found
        """
        pass

    def _ensure_token(self) -> bool:
        """Ensure we have a valid access token, refreshing if necessary."""
        if self._access_token and self._token_expiry:
            if time.time() < (self._token_expiry - 60):
                return True
        return self._refresh_token()

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        require_auth: bool = True,
    ) -> Dict[str, Any]:
        """Make an authenticated request to the platform API."""
        if require_auth and not self._ensure_token():
            return {"error": True, "message": "Authentication failed"}

        url = f"{self.base_url}{endpoint}"
        headers = self._get_auth_headers()

        self.request_count += 1
        self.last_request_time = datetime.utcnow()

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
                self.error_count += 1
                return {"error": True, "message": "Authentication failed"}

            if response.status_code >= 400:
                self.error_count += 1
                return {
                    "error": True,
                    "message": f"API error: {response.status_code}",
                    "details": response.text,
                }

            return response.json()

        except httpx.TimeoutException:
            self.error_count += 1
            logger.error(f"{self.platform_type.value} request timeout: {endpoint}")
            return {"error": True, "message": "Request timeout"}
        except Exception as e:
            self.error_count += 1
            logger.error(f"{self.platform_type.value} request error: {e}")
            return {"error": True, "message": str(e)}

    def get_health(self) -> Dict[str, Any]:
        """Get client health status."""
        return {
            "platform": self.platform_type.value,
            "base_url": self.base_url,
            "authenticated": self._access_token is not None,
            "token_valid": (
                self._token_expiry is not None
                and time.time() < self._token_expiry
            ),
            "request_count": self.request_count,
            "error_count": self.error_count,
            "last_request": self.last_request_time.isoformat() if self.last_request_time else None,
        }

    def close(self):
        """Close the HTTP client."""
        self._client.close()
