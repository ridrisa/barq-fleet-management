"""
BARQ Main Backend Client
Integration with the main BARQ delivery platform backend.
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


class BarqClient(BasePlatformClient):
    """
    Client for BARQ Main Backend API.
    Fetches orders assigned to couriers from the main BARQ system.
    """

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        timeout: int = 30,
    ):
        super().__init__(base_url, timeout)
        self.api_key = api_key
        self.client_id = client_id
        self.client_secret = client_secret

    @property
    def platform_type(self) -> PlatformType:
        return PlatformType.BARQ

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for BARQ API requests."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if self.api_key:
            headers["X-API-Key"] = self.api_key

        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"

        return headers

    def _refresh_token(self) -> bool:
        """Refresh OAuth token for BARQ API."""
        if not self.client_id or not self.client_secret:
            # Use API key auth instead
            if self.api_key:
                self._access_token = self.api_key
                self._token_expiry = time.time() + 86400  # 24 hours
                return True
            return False

        if self._token_lock:
            time.sleep(0.5)
            return self._access_token is not None

        self._token_lock = True
        try:
            auth_url = f"{self.base_url}/oauth/token"

            response = self._client.post(
                auth_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            if response.status_code == 200:
                token_data = response.json()
                self._access_token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", 3600)
                self._token_expiry = time.time() + expires_in
                logger.info("BARQ token refreshed successfully")
                return True
            else:
                logger.error(f"BARQ token refresh failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"BARQ token refresh error: {e}")
            return False
        finally:
            self._token_lock = False

    def _map_status(self, barq_status: str) -> OrderStatus:
        """Map BARQ order status to unified status."""
        status_map = {
            "pending": OrderStatus.PENDING,
            "new": OrderStatus.PENDING,
            "assigned": OrderStatus.ASSIGNED,
            "accepted": OrderStatus.ASSIGNED,
            "picked_up": OrderStatus.PICKED_UP,
            "picking": OrderStatus.PICKED_UP,
            "in_transit": OrderStatus.IN_TRANSIT,
            "on_the_way": OrderStatus.IN_TRANSIT,
            "delivering": OrderStatus.IN_TRANSIT,
            "delivered": OrderStatus.DELIVERED,
            "completed": OrderStatus.DELIVERED,
            "failed": OrderStatus.FAILED,
            "cancelled": OrderStatus.CANCELLED,
            "returned": OrderStatus.RETURNED,
        }
        return status_map.get(barq_status.lower(), OrderStatus.PENDING)

    def _parse_order(self, data: Dict[str, Any]) -> PlatformOrder:
        """Parse BARQ API response into PlatformOrder."""
        # Parse timestamps
        created_at = data.get("created_at") or data.get("createdAt")
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except:
                created_at = datetime.utcnow()
        elif not created_at:
            created_at = datetime.utcnow()

        assigned_at = data.get("assigned_at") or data.get("assignedAt")
        if isinstance(assigned_at, str):
            try:
                assigned_at = datetime.fromisoformat(assigned_at.replace("Z", "+00:00"))
            except:
                assigned_at = None

        picked_up_at = data.get("picked_up_at") or data.get("pickedUpAt")
        if isinstance(picked_up_at, str):
            try:
                picked_up_at = datetime.fromisoformat(picked_up_at.replace("Z", "+00:00"))
            except:
                picked_up_at = None

        delivered_at = data.get("delivered_at") or data.get("deliveredAt")
        if isinstance(delivered_at, str):
            try:
                delivered_at = datetime.fromisoformat(delivered_at.replace("Z", "+00:00"))
            except:
                delivered_at = None

        # Extract pickup info
        pickup = data.get("pickup", {}) or {}
        pickup_address = (
            pickup.get("address")
            or data.get("pickup_address")
            or data.get("pickupAddress")
            or "Unknown"
        )

        # Extract delivery info
        delivery = data.get("delivery", {}) or data.get("dropoff", {}) or {}
        delivery_address = (
            delivery.get("address")
            or data.get("delivery_address")
            or data.get("deliveryAddress")
            or data.get("dropoff_address")
            or "Unknown"
        )

        # Extract customer info
        customer = data.get("customer", {}) or delivery or {}

        return PlatformOrder(
            platform=PlatformType.BARQ,
            platform_order_id=str(data.get("id") or data.get("order_id") or data.get("orderId")),
            platform_tracking_number=data.get("tracking_number") or data.get("trackingNumber"),
            platform_driver_id=str(data.get("driver_id") or data.get("driverId") or data.get("courier_id") or ""),
            courier_barq_id=data.get("barq_id") or data.get("barqId"),
            status=self._map_status(data.get("status", "pending")),
            order_type=data.get("order_type") or data.get("orderType") or data.get("type"),
            pickup_address=pickup_address,
            pickup_lat=pickup.get("lat") or pickup.get("latitude") or data.get("pickup_lat"),
            pickup_lng=pickup.get("lng") or pickup.get("longitude") or data.get("pickup_lng"),
            pickup_contact_name=pickup.get("contact_name") or pickup.get("name"),
            pickup_contact_phone=pickup.get("contact_phone") or pickup.get("phone"),
            delivery_address=delivery_address,
            delivery_lat=delivery.get("lat") or delivery.get("latitude") or data.get("delivery_lat"),
            delivery_lng=delivery.get("lng") or delivery.get("longitude") or data.get("delivery_lng"),
            customer_name=customer.get("name") or data.get("customer_name"),
            customer_phone=customer.get("phone") or data.get("customer_phone"),
            order_amount=Decimal(str(data.get("total_amount") or data.get("totalAmount") or 0)),
            cod_amount=Decimal(str(data.get("cod_amount") or data.get("codAmount") or 0)),
            delivery_fee=Decimal(str(data.get("delivery_fee") or data.get("deliveryFee") or 0)),
            created_at=created_at,
            assigned_at=assigned_at,
            picked_up_at=picked_up_at,
            delivered_at=delivered_at,
            notes=data.get("notes") or data.get("instructions"),
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
        Fetch orders for a specific driver from BARQ backend.

        Args:
            driver_id: BARQ driver/courier ID
            from_date: Start date filter
            to_date: End date filter
            status: Order status filter
            page: Page number (1-indexed)
            page_size: Number of orders per page

        Returns:
            List of PlatformOrder objects
        """
        params = {
            "driver_id": driver_id,
            "page": page,
            "page_size": page_size,
        }

        if from_date:
            params["from_date"] = from_date.isoformat()
        if to_date:
            params["to_date"] = to_date.isoformat()
        if status:
            params["status"] = status

        # Try multiple possible endpoint patterns
        endpoints = [
            "/api/v1/orders/driver",
            "/api/v1/driver/orders",
            "/api/orders",
            "/v1/orders",
        ]

        result = None
        for endpoint in endpoints:
            result = self._make_request("GET", endpoint, params=params)
            if not result.get("error"):
                break

        if result.get("error"):
            logger.error(f"BARQ get_orders_for_driver error: {result.get('message')}")
            return []

        # Parse response - handle different response formats
        orders_data = result.get("data") or result.get("orders") or result.get("items") or []
        if isinstance(result, list):
            orders_data = result

        orders = []
        for order_data in orders_data:
            try:
                order = self._parse_order(order_data)
                orders.append(order)
            except Exception as e:
                logger.error(f"Error parsing BARQ order: {e}")
                continue

        logger.info(f"Fetched {len(orders)} orders for BARQ driver {driver_id}")
        return orders

    def get_order_details(self, order_id: str) -> Optional[PlatformOrder]:
        """
        Get detailed information for a specific order.

        Args:
            order_id: BARQ order ID

        Returns:
            PlatformOrder object or None if not found
        """
        # Try multiple possible endpoint patterns
        endpoints = [
            f"/api/v1/orders/{order_id}",
            f"/api/orders/{order_id}",
            f"/v1/orders/{order_id}",
        ]

        result = None
        for endpoint in endpoints:
            result = self._make_request("GET", endpoint)
            if not result.get("error"):
                break

        if result.get("error"):
            logger.error(f"BARQ get_order_details error: {result.get('message')}")
            return None

        order_data = result.get("data") or result
        try:
            return self._parse_order(order_data)
        except Exception as e:
            logger.error(f"Error parsing BARQ order details: {e}")
            return None

    def get_all_active_orders(
        self,
        page: int = 1,
        page_size: int = 100,
    ) -> List[PlatformOrder]:
        """
        Fetch all active/pending orders from BARQ backend.

        Returns:
            List of PlatformOrder objects
        """
        params = {
            "status": "active",
            "page": page,
            "page_size": page_size,
        }

        result = self._make_request("GET", "/api/v1/orders", params=params)

        if result.get("error"):
            logger.error(f"BARQ get_all_active_orders error: {result.get('message')}")
            return []

        orders_data = result.get("data") or result.get("orders") or []
        orders = []
        for order_data in orders_data:
            try:
                order = self._parse_order(order_data)
                orders.append(order)
            except Exception as e:
                logger.error(f"Error parsing BARQ order: {e}")
                continue

        return orders

    def update_order_status(
        self,
        order_id: str,
        status: str,
        notes: Optional[str] = None,
    ) -> bool:
        """
        Update order status on BARQ backend.

        Args:
            order_id: BARQ order ID
            status: New status
            notes: Optional status notes

        Returns:
            True if successful
        """
        data = {"status": status}
        if notes:
            data["notes"] = notes

        result = self._make_request(
            "PUT",
            f"/api/v1/orders/{order_id}/status",
            json_data=data,
        )

        if result.get("error"):
            logger.error(f"BARQ update_order_status error: {result.get('message')}")
            return False

        return True


# Singleton instance
_barq_client: Optional[BarqClient] = None
_barq_client_url: Optional[str] = None


def get_barq_client() -> BarqClient:
    """Get or create the BARQ client singleton."""
    global _barq_client, _barq_client_url

    current_url = os.getenv("BARQ_MAIN_API_URL", "")

    if not current_url:
        logger.warning("BARQ_MAIN_API_URL not configured")
        # Return a client with empty URL for now
        current_url = "http://localhost:3000"

    if _barq_client is None or _barq_client_url != current_url:
        if _barq_client:
            _barq_client.close()

        _barq_client = BarqClient(
            base_url=current_url,
            api_key=os.getenv("BARQ_MAIN_API_KEY"),
            client_id=os.getenv("BARQ_MAIN_CLIENT_ID"),
            client_secret=os.getenv("BARQ_MAIN_CLIENT_SECRET"),
            timeout=int(os.getenv("BARQ_MAIN_API_TIMEOUT", "30")),
        )
        _barq_client_url = current_url

    return _barq_client
