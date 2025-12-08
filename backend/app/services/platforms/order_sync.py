"""
Order Sync Service
Coordinates fetching and syncing orders from external platforms for all couriers.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.fleet.courier import Courier, CourierStatus
from app.models.operations.delivery import Delivery, DeliveryStatus
from app.services.platforms.base import OrderStatus, PlatformOrder, PlatformType
from app.services.platforms.barq_client import BarqClient, get_barq_client
from app.services.platforms.jahez_client import JahezClient, get_jahez_client, get_saned_client

logger = logging.getLogger(__name__)


class OrderSyncService:
    """
    Service for syncing orders from external platforms to the local database.
    Coordinates between platform clients and local delivery records.
    """

    def __init__(self):
        self._barq_client: Optional[BarqClient] = None
        self._jahez_client: Optional[JahezClient] = None
        self._saned_client: Optional[JahezClient] = None

    @property
    def barq_client(self) -> BarqClient:
        if not self._barq_client:
            self._barq_client = get_barq_client()
        return self._barq_client

    @property
    def jahez_client(self) -> JahezClient:
        if not self._jahez_client:
            self._jahez_client = get_jahez_client()
        return self._jahez_client

    @property
    def saned_client(self) -> JahezClient:
        if not self._saned_client:
            self._saned_client = get_saned_client()
        return self._saned_client

    def _map_order_status(self, platform_status: OrderStatus) -> DeliveryStatus:
        """Map platform order status to local delivery status."""
        status_map = {
            OrderStatus.PENDING: DeliveryStatus.PENDING,
            OrderStatus.ASSIGNED: DeliveryStatus.PENDING,
            OrderStatus.PICKED_UP: DeliveryStatus.IN_TRANSIT,
            OrderStatus.IN_TRANSIT: DeliveryStatus.IN_TRANSIT,
            OrderStatus.DELIVERED: DeliveryStatus.DELIVERED,
            OrderStatus.FAILED: DeliveryStatus.FAILED,
            OrderStatus.CANCELLED: DeliveryStatus.FAILED,
            OrderStatus.RETURNED: DeliveryStatus.RETURNED,
        }
        return status_map.get(platform_status, DeliveryStatus.PENDING)

    def get_courier_platform_ids(
        self,
        db: Session,
        courier_id: Optional[int] = None,
        organization_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all couriers with their platform IDs.

        Args:
            db: Database session
            courier_id: Optional specific courier ID
            organization_id: Optional organization filter

        Returns:
            List of dicts with courier info and platform IDs
        """
        query = db.query(Courier).filter(Courier.status == CourierStatus.ACTIVE)

        if courier_id:
            query = query.filter(Courier.id == courier_id)
        if organization_id:
            query = query.filter(Courier.organization_id == organization_id)

        couriers = query.all()

        result = []
        for courier in couriers:
            result.append({
                "courier_id": courier.id,
                "barq_id": courier.barq_id,
                "jahez_driver_id": courier.jahez_driver_id,
                "hunger_rider_id": courier.hunger_rider_id,
                "mrsool_courier_id": courier.mrsool_courier_id,
                "full_name": courier.full_name,
            })

        return result

    def fetch_orders_for_courier(
        self,
        db: Session,
        courier_id: int,
        platforms: Optional[List[PlatformType]] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> Dict[str, List[PlatformOrder]]:
        """
        Fetch orders for a specific courier from all configured platforms.

        Args:
            db: Database session
            courier_id: Courier ID
            platforms: List of platforms to fetch from (None = all configured)
            from_date: Start date filter
            to_date: End date filter

        Returns:
            Dict mapping platform name to list of orders
        """
        courier = db.query(Courier).filter(Courier.id == courier_id).first()
        if not courier:
            logger.error(f"Courier {courier_id} not found")
            return {}

        results = {}

        # Default date range: last 7 days
        if not from_date:
            from_date = datetime.utcnow() - timedelta(days=7)
        if not to_date:
            to_date = datetime.utcnow()

        # Fetch from BARQ if configured
        if (not platforms or PlatformType.BARQ in platforms) and courier.barq_id:
            try:
                orders = self.barq_client.get_orders_for_driver(
                    driver_id=courier.barq_id,
                    from_date=from_date,
                    to_date=to_date,
                )
                # Tag with local courier info
                for order in orders:
                    order.courier_barq_id = courier.barq_id
                results["barq"] = orders
                logger.info(f"Fetched {len(orders)} BARQ orders for courier {courier.barq_id}")
            except Exception as e:
                logger.error(f"Error fetching BARQ orders for courier {courier_id}: {e}")
                results["barq"] = []

        # Fetch from Jahez if configured
        if (not platforms or PlatformType.JAHEZ in platforms) and courier.jahez_driver_id:
            try:
                orders = self.jahez_client.get_orders_for_driver(
                    driver_id=courier.jahez_driver_id,
                    from_date=from_date,
                    to_date=to_date,
                )
                for order in orders:
                    order.courier_barq_id = courier.barq_id
                results["jahez"] = orders
                logger.info(f"Fetched {len(orders)} Jahez orders for courier {courier.jahez_driver_id}")
            except Exception as e:
                logger.error(f"Error fetching Jahez orders for courier {courier_id}: {e}")
                results["jahez"] = []

        # Fetch from Saned if configured (uses same driver ID field as Jahez typically)
        if (not platforms or PlatformType.SANED in platforms) and courier.jahez_driver_id:
            try:
                orders = self.saned_client.get_orders_for_driver(
                    driver_id=courier.jahez_driver_id,
                    from_date=from_date,
                    to_date=to_date,
                )
                for order in orders:
                    order.courier_barq_id = courier.barq_id
                results["saned"] = orders
                logger.info(f"Fetched {len(orders)} Saned orders for courier {courier.jahez_driver_id}")
            except Exception as e:
                logger.error(f"Error fetching Saned orders for courier {courier_id}: {e}")
                results["saned"] = []

        return results

    def fetch_all_courier_orders(
        self,
        db: Session,
        organization_id: Optional[int] = None,
        platforms: Optional[List[PlatformType]] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> Dict[int, Dict[str, List[PlatformOrder]]]:
        """
        Fetch orders for all active couriers.

        Args:
            db: Database session
            organization_id: Optional organization filter
            platforms: List of platforms to fetch from
            from_date: Start date filter
            to_date: End date filter

        Returns:
            Dict mapping courier_id to platform orders
        """
        couriers = self.get_courier_platform_ids(db, organization_id=organization_id)

        results = {}
        for courier_info in couriers:
            courier_id = courier_info["courier_id"]
            orders = self.fetch_orders_for_courier(
                db,
                courier_id=courier_id,
                platforms=platforms,
                from_date=from_date,
                to_date=to_date,
            )
            if any(orders.values()):
                results[courier_id] = orders

        return results

    def sync_orders_to_db(
        self,
        db: Session,
        courier_id: int,
        orders: List[PlatformOrder],
        organization_id: Optional[int] = None,
    ) -> Dict[str, int]:
        """
        Sync fetched orders to the local database.

        Args:
            db: Database session
            courier_id: Local courier ID
            orders: List of platform orders to sync
            organization_id: Organization ID for tenant isolation

        Returns:
            Dict with counts of created, updated, skipped orders
        """
        stats = {"created": 0, "updated": 0, "skipped": 0}

        for order in orders:
            try:
                # Generate unique tracking number
                tracking_number = f"{order.platform.value.upper()}-{order.platform_order_id}"

                # Check if order exists
                existing = db.query(Delivery).filter(
                    Delivery.tracking_number == tracking_number
                ).first()

                if existing:
                    # Update existing order
                    existing.status = self._map_order_status(OrderStatus(order.status))
                    if order.delivered_at:
                        existing.delivery_time = order.delivered_at
                    if order.picked_up_at:
                        existing.pickup_time = order.picked_up_at
                    if order.cod_amount:
                        existing.cod_amount = order.cod_amount
                    if order.notes:
                        existing.notes = order.notes
                    stats["updated"] += 1
                else:
                    # Create new delivery record
                    delivery = Delivery(
                        tracking_number=tracking_number,
                        courier_id=courier_id,
                        pickup_address=order.pickup_address,
                        delivery_address=order.delivery_address,
                        status=self._map_order_status(OrderStatus(order.status)),
                        pickup_time=order.picked_up_at,
                        delivery_time=order.delivered_at,
                        cod_amount=order.cod_amount,
                        notes=f"[{order.platform.value.upper()}] {order.notes or ''}".strip(),
                    )
                    if organization_id:
                        delivery.organization_id = organization_id
                    db.add(delivery)
                    stats["created"] += 1

            except Exception as e:
                logger.error(f"Error syncing order {order.platform_order_id}: {e}")
                stats["skipped"] += 1
                continue

        db.commit()
        logger.info(f"Sync complete: {stats}")
        return stats

    def full_sync(
        self,
        db: Session,
        organization_id: Optional[int] = None,
        platforms: Optional[List[PlatformType]] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Perform a full sync of all courier orders to the database.

        Args:
            db: Database session
            organization_id: Optional organization filter
            platforms: List of platforms to sync
            from_date: Start date filter
            to_date: End date filter

        Returns:
            Summary of sync operation
        """
        all_orders = self.fetch_all_courier_orders(
            db,
            organization_id=organization_id,
            platforms=platforms,
            from_date=from_date,
            to_date=to_date,
        )

        total_stats = {"created": 0, "updated": 0, "skipped": 0}
        courier_results = {}

        for courier_id, platform_orders in all_orders.items():
            courier_stats = {"created": 0, "updated": 0, "skipped": 0}

            for platform, orders in platform_orders.items():
                if orders:
                    # Get courier's organization
                    courier = db.query(Courier).filter(Courier.id == courier_id).first()
                    org_id = courier.organization_id if courier else organization_id

                    stats = self.sync_orders_to_db(
                        db,
                        courier_id=courier_id,
                        orders=orders,
                        organization_id=org_id,
                    )
                    for key in courier_stats:
                        courier_stats[key] += stats[key]
                        total_stats[key] += stats[key]

            courier_results[courier_id] = courier_stats

        return {
            "total": total_stats,
            "by_courier": courier_results,
            "couriers_processed": len(courier_results),
        }

    def get_platform_health(self) -> Dict[str, Any]:
        """Get health status of all platform connections."""
        return {
            "barq": self.barq_client.get_health(),
            "jahez": self.jahez_client.get_health(),
            "saned": self.saned_client.get_health(),
        }


# Singleton instance
order_sync_service = OrderSyncService()
