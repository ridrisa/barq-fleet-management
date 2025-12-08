"""
Jahez/Saned Platform Client
Integration with Jahez and Saned delivery platforms.
"""

import logging
import os
import time
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from app.services.platforms.base import (
    BasePlatformClient,
    OrderStatus,
    PlatformOrder,
    PlatformType,
)

logger = logging.getLogger(__name__)


class JahezClient(BasePlatformClient):
    """
    Client for Jahez/Saned Platform API.
    Fetches orders assigned to drivers from Jahez/Saned system.
    """

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        partner_id: Optional[str] = None,
        partner_secret: Optional[str] = None,
        platform: str = "jahez",  # or "saned"
        timeout: int = 30,
    ):
        super().__init__(base_url, timeout)
        self.api_key = api_key
        self.partner_id = partner_id
        self.partner_secret = partner_secret
        self._platform = platform.lower()

    @property
    def platform_type(self) -> PlatformType:
        if self._platform == "saned":
            return PlatformType.SANED
        return PlatformType.JAHEZ

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for Jahez API requests."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if self.api_key:
            headers["X-API-Key"] = self.api_key
            headers["Authorization"] = f"ApiKey {self.api_key}"

        if self.partner_id:
            headers["X-Partner-ID"] = self.partner_id

        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"

        return headers

    def _refresh_token(self) -> bool:
        """Refresh OAuth token for Jahez API."""
        if not self.partner_id or not self.partner_secret:
            # Use API key auth
            if self.api_key:
                self._access_token = self.api_key
                self._token_expiry = time.time() + 86400
                return True
            return False

        if self._token_lock:
            time.sleep(0.5)
            return self._access_token is not None

        self._token_lock = True
        try:
            auth_url = f"{self.base_url}/auth/token"

            response = self._client.post(
                auth_url,
                json={
                    "partner_id": self.partner_id,
                    "partner_secret": self.partner_secret,
                },
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                token_data = response.json()
                self._access_token = token_data.get("access_token") or token_data.get("token")
                expires_in = token_data.get("expires_in", 3600)
                self._token_expiry = time.time() + expires_in
                logger.info(f"{self._platform.upper()} token refreshed successfully")
                return True
            else:
                logger.error(f"{self._platform.upper()} token refresh failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"{self._platform.upper()} token refresh error: {e}")
            return False
        finally:
            self._token_lock = False

    def _map_status(self, jahez_status: str) -> OrderStatus:
        """Map Jahez order status to unified status."""
        status_map = {
            # Jahez statuses
            "pending": OrderStatus.PENDING,
            "new": OrderStatus.PENDING,
            "waiting": OrderStatus.PENDING,
            "accepted": OrderStatus.ASSIGNED,
            "assigned": OrderStatus.ASSIGNED,
            "driver_assigned": OrderStatus.ASSIGNED,
            "preparing": OrderStatus.ASSIGNED,
            "ready": OrderStatus.ASSIGNED,
            "picked": OrderStatus.PICKED_UP,
            "picked_up": OrderStatus.PICKED_UP,
            "collecting": OrderStatus.PICKED_UP,
            "on_way": OrderStatus.IN_TRANSIT,
            "in_transit": OrderStatus.IN_TRANSIT,
            "delivering": OrderStatus.IN_TRANSIT,
            "near_customer": OrderStatus.IN_TRANSIT,
            "delivered": OrderStatus.DELIVERED,
            "completed": OrderStatus.DELIVERED,
            "done": OrderStatus.DELIVERED,
            "failed": OrderStatus.FAILED,
            "undelivered": OrderStatus.FAILED,
            "cancelled": OrderStatus.CANCELLED,
            "rejected": OrderStatus.CANCELLED,
            "returned": OrderStatus.RETURNED,
            # Saned specific
            "at_pickup": OrderStatus.PICKED_UP,
            "at_dropoff": OrderStatus.IN_TRANSIT,
        }
        return status_map.get(jahez_status.lower(), OrderStatus.PENDING)

    def _parse_order(self, data: Dict[str, Any]) -> PlatformOrder:
        """Parse Jahez/Saned API response into PlatformOrder."""
        # Parse timestamps
        created_at = data.get("created_at") or data.get("createdAt") or data.get("order_time")
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except:
                created_at = datetime.utcnow()
        elif isinstance(created_at, (int, float)):
            created_at = datetime.fromtimestamp(created_at)
        elif not created_at:
            created_at = datetime.utcnow()

        assigned_at = data.get("assigned_at") or data.get("driver_assigned_at")
        if isinstance(assigned_at, str):
            try:
                assigned_at = datetime.fromisoformat(assigned_at.replace("Z", "+00:00"))
            except:
                assigned_at = None
        elif isinstance(assigned_at, (int, float)):
            assigned_at = datetime.fromtimestamp(assigned_at)

        picked_up_at = data.get("picked_at") or data.get("pickup_time")
        if isinstance(picked_up_at, str):
            try:
                picked_up_at = datetime.fromisoformat(picked_up_at.replace("Z", "+00:00"))
            except:
                picked_up_at = None
        elif isinstance(picked_up_at, (int, float)):
            picked_up_at = datetime.fromtimestamp(picked_up_at)

        delivered_at = data.get("delivered_at") or data.get("delivery_time")
        if isinstance(delivered_at, str):
            try:
                delivered_at = datetime.fromisoformat(delivered_at.replace("Z", "+00:00"))
            except:
                delivered_at = None
        elif isinstance(delivered_at, (int, float)):
            delivered_at = datetime.fromtimestamp(delivered_at)

        # Extract pickup info (restaurant/merchant)
        pickup = data.get("pickup", {}) or data.get("restaurant", {}) or data.get("merchant", {}) or {}
        pickup_address = (
            pickup.get("address")
            or pickup.get("full_address")
            or data.get("pickup_address")
            or data.get("restaurant_address")
            or "Unknown"
        )

        # Extract delivery info (customer)
        delivery = data.get("delivery", {}) or data.get("customer", {}) or data.get("dropoff", {}) or {}
        delivery_address = (
            delivery.get("address")
            or delivery.get("full_address")
            or data.get("delivery_address")
            or data.get("customer_address")
            or "Unknown"
        )

        # Extract driver info
        driver = data.get("driver", {}) or {}
        driver_id = (
            driver.get("id")
            or driver.get("driver_id")
            or data.get("driver_id")
            or data.get("rider_id")
            or ""
        )

        # Get order amounts
        total_amount = (
            data.get("total")
            or data.get("total_amount")
            or data.get("order_total")
            or 0
        )
        cod_amount = (
            data.get("cod_amount")
            or data.get("cash_amount")
            or (total_amount if data.get("payment_method") == "cash" else 0)
        )

        return PlatformOrder(
            platform=self.platform_type,
            platform_order_id=str(data.get("id") or data.get("order_id") or data.get("orderId")),
            platform_tracking_number=data.get("tracking_id") or data.get("order_number"),
            platform_driver_id=str(driver_id) if driver_id else None,
            courier_barq_id=data.get("barq_id"),
            status=self._map_status(data.get("status", "pending")),
            order_type=data.get("order_type") or "food",
            pickup_address=pickup_address,
            pickup_lat=pickup.get("lat") or pickup.get("latitude"),
            pickup_lng=pickup.get("lng") or pickup.get("longitude"),
            pickup_contact_name=pickup.get("name") or pickup.get("restaurant_name"),
            pickup_contact_phone=pickup.get("phone"),
            delivery_address=delivery_address,
            delivery_lat=delivery.get("lat") or delivery.get("latitude"),
            delivery_lng=delivery.get("lng") or delivery.get("longitude"),
            customer_name=delivery.get("name") or data.get("customer_name"),
            customer_phone=delivery.get("phone") or data.get("customer_phone"),
            order_amount=Decimal(str(total_amount)),
            cod_amount=Decimal(str(cod_amount)),
            delivery_fee=Decimal(str(data.get("delivery_fee") or 0)),
            created_at=created_at,
            assigned_at=assigned_at,
            picked_up_at=picked_up_at,
            delivered_at=delivered_at,
            notes=data.get("notes") or data.get("special_instructions"),
            items_count=data.get("items_count") or len(data.get("items", [])),
            raw_data=data,
        )

    def get_orders_for_driver(
        self,
        driver_id: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> List[PlatformOrder]:
        """
        Fetch orders for a specific driver from Jahez/Saned.

        Args:
            driver_id: Jahez driver ID
            from_date: Start date filter
            to_date: End date filter
            status: Order status filter
            page: Page number
            page_size: Number of orders per page

        Returns:
            List of PlatformOrder objects
        """
        params = {
            "driver_id": driver_id,
            "page": page,
            "limit": page_size,
        }

        if from_date:
            params["from"] = from_date.strftime("%Y-%m-%d")
        if to_date:
            params["to"] = to_date.strftime("%Y-%m-%d")
        if status:
            params["status"] = status

        # Try multiple possible endpoint patterns
        endpoints = [
            "/api/v1/partner/orders",
            "/api/v1/driver/orders",
            "/partner/orders",
            "/v1/orders",
        ]

        result = None
        for endpoint in endpoints:
            result = self._make_request("GET", endpoint, params=params)
            if not result.get("error"):
                break

        if result.get("error"):
            logger.error(f"{self._platform.upper()} get_orders_for_driver error: {result.get('message')}")
            return []

        # Parse response
        orders_data = result.get("data") or result.get("orders") or result.get("items") or []
        if isinstance(result, list):
            orders_data = result

        orders = []
        for order_data in orders_data:
            try:
                order = self._parse_order(order_data)
                orders.append(order)
            except Exception as e:
                logger.error(f"Error parsing {self._platform} order: {e}")
                continue

        logger.info(f"Fetched {len(orders)} orders for {self._platform.upper()} driver {driver_id}")
        return orders

    def get_order_details(self, order_id: str) -> Optional[PlatformOrder]:
        """
        Get detailed information for a specific order.

        Args:
            order_id: Jahez order ID

        Returns:
            PlatformOrder object or None if not found
        """
        endpoints = [
            f"/api/v1/partner/orders/{order_id}",
            f"/api/v1/orders/{order_id}",
            f"/partner/orders/{order_id}",
        ]

        result = None
        for endpoint in endpoints:
            result = self._make_request("GET", endpoint)
            if not result.get("error"):
                break

        if result.get("error"):
            logger.error(f"{self._platform.upper()} get_order_details error: {result.get('message')}")
            return None

        order_data = result.get("data") or result
        try:
            return self._parse_order(order_data)
        except Exception as e:
            logger.error(f"Error parsing {self._platform} order details: {e}")
            return None

    def get_active_orders(
        self,
        page: int = 1,
        page_size: int = 100,
    ) -> List[PlatformOrder]:
        """
        Fetch all active orders from Jahez/Saned.

        Returns:
            List of PlatformOrder objects
        """
        params = {
            "status": "active",
            "page": page,
            "limit": page_size,
        }

        result = self._make_request("GET", "/api/v1/partner/orders/active", params=params)

        if result.get("error"):
            logger.error(f"{self._platform.upper()} get_active_orders error: {result.get('message')}")
            return []

        orders_data = result.get("data") or result.get("orders") or []
        orders = []
        for order_data in orders_data:
            try:
                order = self._parse_order(order_data)
                orders.append(order)
            except Exception as e:
                logger.error(f"Error parsing {self._platform} order: {e}")
                continue

        return orders

    def update_order_status(
        self,
        order_id: str,
        status: str,
        notes: Optional[str] = None,
        location: Optional[Dict[str, float]] = None,
    ) -> bool:
        """
        Update order status on Jahez/Saned.

        Args:
            order_id: Jahez order ID
            status: New status
            notes: Optional status notes
            location: Optional current location {lat, lng}

        Returns:
            True if successful
        """
        data = {"status": status}
        if notes:
            data["notes"] = notes
        if location:
            data["location"] = location

        result = self._make_request(
            "PUT",
            f"/api/v1/partner/orders/{order_id}/status",
            json_data=data,
        )

        if result.get("error"):
            logger.error(f"{self._platform.upper()} update_order_status error: {result.get('message')}")
            return False

        return True


# Singleton instances
_jahez_client: Optional[JahezClient] = None
_jahez_client_url: Optional[str] = None

_saned_client: Optional[JahezClient] = None
_saned_client_url: Optional[str] = None


def get_jahez_client() -> JahezClient:
    """Get or create the Jahez client singleton."""
    global _jahez_client, _jahez_client_url

    current_url = os.getenv("JAHEZ_API_URL", "")

    if not current_url:
        logger.warning("JAHEZ_API_URL not configured")
        current_url = "http://localhost:3001"

    if _jahez_client is None or _jahez_client_url != current_url:
        if _jahez_client:
            _jahez_client.close()

        _jahez_client = JahezClient(
            base_url=current_url,
            api_key=os.getenv("JAHEZ_API_KEY"),
            partner_id=os.getenv("JAHEZ_PARTNER_ID"),
            partner_secret=os.getenv("JAHEZ_PARTNER_SECRET"),
            platform="jahez",
            timeout=int(os.getenv("JAHEZ_API_TIMEOUT", "30")),
        )
        _jahez_client_url = current_url

    return _jahez_client


def get_saned_client() -> JahezClient:
    """Get or create the Saned client singleton."""
    global _saned_client, _saned_client_url

    current_url = os.getenv("SANED_API_URL", "")

    if not current_url:
        logger.warning("SANED_API_URL not configured")
        current_url = "http://localhost:3002"

    if _saned_client is None or _saned_client_url != current_url:
        if _saned_client:
            _saned_client.close()

        _saned_client = JahezClient(
            base_url=current_url,
            api_key=os.getenv("SANED_API_KEY"),
            partner_id=os.getenv("SANED_PARTNER_ID"),
            partner_secret=os.getenv("SANED_PARTNER_SECRET"),
            platform="saned",
            timeout=int(os.getenv("SANED_API_TIMEOUT", "30")),
        )
        _saned_client_url = current_url

    return _saned_client
