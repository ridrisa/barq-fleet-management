"""
Dispatch Service - Integration layer between API and Dispatch Engine

Integrates with database SLA definitions for dynamic deadline calculation.
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy import and_, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.fleet.courier import Courier, CourierStatus
from app.models.operations.delivery import Delivery, DeliveryStatus
from app.models.operations.dispatch import DispatchAssignment, DispatchStatus
from app.models.operations.sla import SLADefinition, SLAType
from app.services.dispatch.config import DEFAULT_DISPATCH_CONFIG, DispatchConfig
from app.services.dispatch.engine import DispatchEngine
from app.services.dispatch.google_routing import get_google_routing_provider
from app.services.dispatch.types import (
    AssignmentResult,
    CourierOnlineStatus,
    DispatchCourier,
    DispatchOrder,
    OrderStatus,
    Point,
)

logger = logging.getLogger(__name__)


class DispatchService:
    """
    Service layer for auto-dispatch functionality.

    Bridges the database models with the dispatch engine,
    handling conversions and persistence.
    """

    def __init__(
        self,
        db: AsyncSession,
        config: Optional[DispatchConfig] = None
    ):
        self.db = db
        self.config = config or DEFAULT_DISPATCH_CONFIG
        routing_provider = get_google_routing_provider()
        self.engine = DispatchEngine(routing_provider, self.config)

    async def auto_assign_order(
        self,
        delivery_id: int,
        zone_id: Optional[int] = None
    ) -> Optional[DispatchAssignment]:
        """
        Auto-assign a delivery to the best available courier.

        Args:
            delivery_id: ID of the delivery to assign
            zone_id: Optional zone filter

        Returns:
            DispatchAssignment if successful, None otherwise
        """
        now = datetime.utcnow()

        # Load the delivery
        delivery = await self.db.get(Delivery, delivery_id)
        if not delivery:
            logger.error(f"Delivery {delivery_id} not found")
            return None

        # Check if delivery is pending - compare with string value due to enum type
        if str(delivery.status) != "pending" and delivery.status != DeliveryStatus.PENDING:
            logger.warning(f"Delivery {delivery_id} is not pending (status: {delivery.status})")
            return None

        # Convert to dispatch order (async to fetch SLA from database)
        order = await self._convert_delivery_to_order(delivery)
        if not order:
            logger.error(f"Could not convert delivery {delivery_id} to dispatch order")
            return None

        # Load available couriers
        couriers = await self._load_available_couriers(zone_id, now)
        if not couriers:
            logger.warning(f"No available couriers for delivery {delivery_id}")
            return None

        # Load all orders for route building
        all_orders = await self._load_all_active_orders()

        # Run the dispatch engine
        result = await self.engine.assign_new_order(
            order=order,
            all_orders_by_id=all_orders,
            couriers=couriers,
            now=now
        )

        if not result:
            logger.info(f"No feasible courier found for delivery {delivery_id}")
            return None

        # Create the dispatch assignment
        assignment = await self._create_assignment(delivery, result, now)

        # Update delivery status
        delivery.status = DeliveryStatus.IN_TRANSIT
        delivery.courier_id = int(result.courier_id)
        await self.db.commit()

        logger.info(
            f"Delivery {delivery_id} assigned to courier {result.courier_id} "
            f"(score: {result.score:.2f})"
        )

        return assignment

    async def auto_assign_batch(
        self,
        delivery_ids: list[int],
        zone_id: Optional[int] = None
    ) -> list[DispatchAssignment]:
        """
        Auto-assign multiple deliveries.

        Args:
            delivery_ids: List of delivery IDs to assign
            zone_id: Optional zone filter

        Returns:
            List of successful assignments
        """
        assignments = []

        for delivery_id in delivery_ids:
            try:
                assignment = await self.auto_assign_order(delivery_id, zone_id)
                if assignment:
                    assignments.append(assignment)
            except Exception as e:
                logger.error(f"Error assigning delivery {delivery_id}: {e}")
                continue

        return assignments

    async def _get_sla_hours(
        self,
        organization_id: Optional[int] = None,
        zone_id: Optional[int] = None,
        service_type: Optional[str] = None
    ) -> float:
        """
        Get SLA hours from database definition.

        Fetches the active SLA definition for delivery_time, with optional
        filters for organization, zone, and service type. Falls back to
        config.sla_hours if no database definition exists.

        Args:
            organization_id: Filter by organization
            zone_id: Filter by zone
            service_type: Filter by service type (express, standard, economy)

        Returns:
            SLA deadline in hours
        """
        # Build query for active delivery_time SLA
        # Use raw SQL for enum comparison to avoid asyncpg type issues
        # Note: PostgreSQL enum values are UPPERCASE
        query = (
            select(SLADefinition)
            .where(text("sla_definitions.sla_type = 'DELIVERY_TIME'"))
            .where(SLADefinition.is_active == True)
        )

        # Add organization filter if provided
        if organization_id:
            query = query.where(SLADefinition.organization_id == organization_id)

        # Add zone filter if provided
        if zone_id:
            query = query.where(
                (SLADefinition.applies_to_zone_id == zone_id) |
                (SLADefinition.applies_to_zone_id.is_(None))
            )

        # Add service type filter if provided
        if service_type:
            query = query.where(
                (SLADefinition.applies_to_service_type == service_type) |
                (SLADefinition.applies_to_service_type.is_(None))
            )

        # Order by specificity: zone-specific first, then general
        query = query.order_by(
            SLADefinition.applies_to_zone_id.desc().nullslast(),
            SLADefinition.applies_to_service_type.desc().nullslast()
        ).limit(1)

        result = await self.db.execute(query)
        sla_def = result.scalar_one_or_none()

        if sla_def:
            # Convert target_value to hours based on unit_of_measure
            target_value = float(sla_def.target_value)
            unit = (sla_def.unit_of_measure or "minutes").lower()

            if unit == "minutes":
                hours = target_value / 60
            elif unit == "hours":
                hours = target_value
            elif unit == "days":
                hours = target_value * 24
            else:
                # Default to minutes
                hours = target_value / 60

            logger.info(
                f"Using SLA from database: {target_value} {unit} = {hours:.2f} hours "
                f"(definition: {sla_def.sla_code})"
            )
            return hours

        # Fall back to config
        logger.debug(f"No SLA definition found, using config: {self.config.sla_hours} hours")
        return self.config.sla_hours

    async def _convert_delivery_to_order(
        self,
        delivery: Delivery
    ) -> Optional[DispatchOrder]:
        """
        Convert a Delivery model to a DispatchOrder.

        Fetches SLA from database for deadline calculation.
        """
        # Parse coordinates from addresses (simplified - in production you'd geocode)
        # For now, we'll use default coordinates or stored lat/lng if available

        # Try to parse pickup coordinates
        pickup = self._parse_location(delivery.pickup_address)
        if not pickup:
            logger.warning(f"Could not parse pickup address for delivery {delivery.id}")
            return None

        # Try to parse dropoff coordinates
        dropoff = self._parse_location(delivery.delivery_address)
        if not dropoff:
            logger.warning(f"Could not parse dropoff address for delivery {delivery.id}")
            return None

        created_at = delivery.created_at or datetime.utcnow()

        # Get SLA hours from database (with fallback to config)
        sla_hours = await self._get_sla_hours(
            organization_id=delivery.organization_id,
            zone_id=None,  # Could add zone resolution here
            service_type=None  # Could add service type from delivery
        )
        deadline_at = created_at + timedelta(hours=sla_hours)

        return DispatchOrder(
            id=str(delivery.id),
            pickup=pickup,
            dropoff=dropoff,
            created_at=created_at,
            deadline_at=deadline_at,
            status=OrderStatus.UNASSIGNED,
            zone_id=None,  # Would need zone resolution
        )

    def _parse_location(self, address: str) -> Optional[Point]:
        """
        Parse a location from an address string.

        In production, this would use geocoding. For now, we check if
        the address contains coordinates or use a default.
        """
        if not address:
            return None

        # Check if address contains lat,lng format
        parts = address.split(",")
        if len(parts) >= 2:
            try:
                lat = float(parts[0].strip())
                lng = float(parts[1].strip())
                if -90 <= lat <= 90 and -180 <= lng <= 180:
                    return Point(lat=lat, lng=lng)
            except ValueError:
                pass

        # Default to Riyadh center for demo (would use geocoding in production)
        return Point(lat=24.7136, lng=46.6753)

    async def _load_available_couriers(
        self,
        zone_id: Optional[int],
        now: datetime
    ) -> list[DispatchCourier]:
        """Load all available couriers from the database."""
        # Use text() for raw SQL enum comparison to avoid asyncpg type issues
        query = (
            select(Courier)
            .where(text("couriers.status = 'ACTIVE'"))
        )

        result = await self.db.execute(query)
        db_couriers = result.scalars().all()

        couriers = []
        for c in db_couriers:
            # Get open delivery count for this courier
            # Use text() for raw SQL enum comparison to avoid asyncpg type issues
            delivery_query = (
                select(Delivery)
                .where(Delivery.courier_id == c.id)
                .where(text("deliveries.status IN ('pending', 'in_transit')"))
            )
            delivery_result = await self.db.execute(delivery_query)
            open_deliveries = delivery_result.scalars().all()

            # Default shift end (8 hours from now if not set)
            shift_end = now + timedelta(hours=8)

            # Default location (would come from GPS/FMS in production)
            location = Point(lat=24.7136, lng=46.6753)

            courier = DispatchCourier(
                id=str(c.id),
                current_location=location,
                online_status=CourierOnlineStatus.ONLINE,
                shift_end_at=shift_end,
                completed_orders_today=c.total_deliveries or 0,
                assigned_open_order_ids=[str(d.id) for d in open_deliveries],
                zone_id=str(zone_id) if zone_id else None,
            )
            couriers.append(courier)

        return couriers

    async def _load_all_active_orders(self) -> dict[str, DispatchOrder]:
        """Load all active orders for route building."""
        # Use text() for raw SQL enum comparison to avoid asyncpg type issues
        query = (
            select(Delivery)
            .where(text("deliveries.status IN ('pending', 'in_transit')"))
        )

        result = await self.db.execute(query)
        deliveries = result.scalars().all()

        orders = {}
        for d in deliveries:
            order = await self._convert_delivery_to_order(d)
            if order:
                # Update status based on delivery status (compare with string due to enum)
                if str(d.status) == "in_transit" or d.status == DeliveryStatus.IN_TRANSIT:
                    order.status = OrderStatus.ASSIGNED
                orders[order.id] = order

        return orders

    async def _create_assignment(
        self,
        delivery: Delivery,
        result: AssignmentResult,
        now: datetime
    ) -> DispatchAssignment:
        """Create a DispatchAssignment record."""
        import uuid

        assignment = DispatchAssignment(
            assignment_number=f"DA-{uuid.uuid4().hex[:8].upper()}",
            status="ASSIGNED",  # Use uppercase string for PostgreSQL enum
            delivery_id=delivery.id,
            courier_id=int(result.courier_id),
            created_at_time=now,
            assigned_at=now,
            assignment_algorithm="auto_dispatch_v1",
            distance_to_pickup_km=result.plan.total_distance_km,
            estimated_time_minutes=int(result.plan.total_duration_minutes),
            courier_current_load=len(result.plan.stops),
            organization_id=delivery.organization_id,
        )

        self.db.add(assignment)
        await self.db.flush()

        return assignment


# Factory function for dependency injection
async def get_dispatch_service(db: AsyncSession) -> DispatchService:
    """Get a DispatchService instance."""
    return DispatchService(db)
