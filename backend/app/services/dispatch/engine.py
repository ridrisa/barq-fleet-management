"""
Dispatch Engine - Multi-layer order assignment algorithm

Layer 1: Local filtering (online status, shift, zone, Haversine radius)
Layer 2: Distance Matrix filtering (ETA to pickup threshold)
Layer 3: Approximate route feasibility (Haversine + SLA check)
Layer 4: Precise routing with scoring (Directions API + penalties)
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.services.dispatch.config import DEFAULT_DISPATCH_CONFIG, DispatchConfig
from app.services.dispatch.geo import add_minutes, haversine_km
from app.services.dispatch.routing import RoutingProvider
from app.services.dispatch.types import (
    AssignmentResult,
    CourierPlan,
    DispatchCourier,
    DispatchOrder,
    OrderStatus,
    Point,
    RouteStop,
    StopType,
)

logger = logging.getLogger(__name__)


@dataclass
class _RouteStop:
    """Internal stop representation for route building"""
    order_id: str
    type: StopType
    location: Point


class DispatchEngine:
    """
    Multi-layer dispatch engine for intelligent order assignment.

    The engine uses a 4-layer approach:
    1. Fast local filtering using business rules and Haversine distance
    2. Distance Matrix API for accurate ETA filtering
    3. Approximate route feasibility check using nearest-neighbor heuristic
    4. Precise route planning with Google Directions and scoring
    """

    def __init__(
        self,
        routing_provider: RoutingProvider,
        config: Optional[DispatchConfig] = None
    ):
        self.routing = routing_provider
        self.config = config or DEFAULT_DISPATCH_CONFIG

    async def assign_new_order(
        self,
        order: DispatchOrder,
        all_orders_by_id: dict[str, DispatchOrder],
        couriers: list[DispatchCourier],
        now: datetime
    ) -> Optional[AssignmentResult]:
        """
        Assign a single new order to the best available courier.

        Args:
            order: The order to assign (must be unassigned)
            all_orders_by_id: Map of all orders for route building
            couriers: List of all couriers
            now: Current timestamp

        Returns:
            AssignmentResult if successful, None if no feasible courier found
        """
        if order.status != OrderStatus.UNASSIGNED:
            logger.debug(f"Order {order.id} is not unassigned (status: {order.status})")
            return None

        if order.deadline_at <= now:
            logger.debug(f"Order {order.id} is already past deadline")
            return None

        # Layer 1: Local filtering
        layer1_candidates = self._filter_couriers_layer1(order, couriers, now)
        if not layer1_candidates:
            logger.debug(f"Order {order.id}: No couriers passed Layer 1 filtering")
            return None
        logger.info(f"Order {order.id}: Layer 1 passed {len(layer1_candidates)} couriers")

        # Layer 2: Distance Matrix filtering
        layer2_candidates = await self._filter_couriers_layer2(
            order, layer1_candidates, now
        )
        if not layer2_candidates:
            logger.debug(f"Order {order.id}: No couriers passed Layer 2 filtering")
            return None
        logger.info(f"Order {order.id}: Layer 2 passed {len(layer2_candidates)} couriers")

        # Layer 3: Approximate feasibility
        layer3_candidates = []
        for courier in layer2_candidates:
            if self._check_approximate_feasibility(order, courier, all_orders_by_id, now):
                layer3_candidates.append(courier)

        if not layer3_candidates:
            logger.debug(f"Order {order.id}: No couriers passed Layer 3 feasibility")
            return None
        logger.info(f"Order {order.id}: Layer 3 passed {len(layer3_candidates)} couriers")

        # Layer 4: Precise scoring
        best = await self._choose_best_courier_with_precise_routing(
            order, layer3_candidates, all_orders_by_id, now
        )

        if best:
            logger.info(
                f"Order {order.id}: Assigned to courier {best.courier_id} "
                f"(score: {best.score:.2f})"
            )
        else:
            logger.debug(f"Order {order.id}: No couriers passed Layer 4 scoring")

        return best

    # ======================== Layer 1 ========================

    def _filter_couriers_layer1(
        self,
        order: DispatchOrder,
        couriers: list[DispatchCourier],
        now: datetime
    ) -> list[DispatchCourier]:
        """
        Layer 1: Fast local filtering.

        Filters by:
        - Online status
        - Shift not ended
        - Zone matching (if applicable)
        - Haversine distance within radius
        """
        max_radius = self.config.max_haversine_radius_km
        result = []

        for courier in couriers:
            # Must be online
            if not courier.is_available:
                continue

            # Shift must not have ended
            if courier.shift_end_at <= now:
                continue

            # Zone matching (if both have zones)
            if order.zone_id and courier.zone_id:
                if order.zone_id != courier.zone_id:
                    continue

            # Haversine distance check
            dist_km = haversine_km(courier.current_location, order.pickup)
            if dist_km <= max_radius:
                result.append(courier)

        return result

    # ======================== Layer 2 ========================

    async def _filter_couriers_layer2(
        self,
        order: DispatchOrder,
        couriers: list[DispatchCourier],
        now: datetime
    ) -> list[DispatchCourier]:
        """
        Layer 2: Distance Matrix filtering.

        Uses routing API to get accurate ETA to pickup,
        filters by maximum pickup ETA threshold.
        """
        if not couriers:
            return []

        origins = [c.current_location for c in couriers]
        destinations = [order.pickup]

        matrix = await self.routing.get_travel_times(origins, destinations, now)

        max_eta = self.config.max_pickup_eta_minutes
        result = []

        for i, courier in enumerate(couriers):
            if matrix.durations_minutes and i < len(matrix.durations_minutes):
                eta_to_pickup = matrix.durations_minutes[i][0] if matrix.durations_minutes[i] else 0
                if 0 < eta_to_pickup <= max_eta:
                    result.append(courier)

        return result

    # ======================== Layer 3 ========================

    def _check_approximate_feasibility(
        self,
        new_order: DispatchOrder,
        courier: DispatchCourier,
        all_orders_by_id: dict[str, DispatchOrder],
        now: datetime
    ) -> bool:
        """
        Layer 3: Approximate route feasibility check.

        Uses nearest-neighbor heuristic with Haversine distances
        to quickly check if all orders can be delivered within SLA.
        """
        # Collect all orders (existing + new)
        order_ids = list(courier.assigned_open_order_ids) + [new_order.id]
        orders = []

        for oid in order_ids:
            o = all_orders_by_id.get(oid)
            if o:
                orders.append(o)

        if not orders:
            return True

        # Build stops (pickup + dropoff for each order)
        stops: list[_RouteStop] = []
        for o in orders:
            stops.append(_RouteStop(order_id=o.id, type=StopType.PICKUP, location=o.pickup))
            stops.append(_RouteStop(order_id=o.id, type=StopType.DROPOFF, location=o.dropoff))

        # Nearest-neighbor heuristic
        unvisited = stops.copy()
        visited_pickups: set[str] = set()
        route: list[_RouteStop] = []
        current_location = courier.current_location

        while unvisited:
            # Candidates: pickups OR dropoffs whose pickup is done
            candidates = [
                s for s in unvisited
                if s.type == StopType.PICKUP or s.order_id in visited_pickups
            ]

            if not candidates:
                break

            # Find nearest
            best_stop = None
            best_dist = float("inf")
            for s in candidates:
                d = haversine_km(current_location, s.location)
                if d < best_dist:
                    best_dist = d
                    best_stop = s

            if not best_stop:
                break

            route.append(best_stop)
            current_location = best_stop.location

            if best_stop.type == StopType.PICKUP:
                visited_pickups.add(best_stop.order_id)

            # Remove from unvisited
            unvisited = [
                s for s in unvisited
                if not (s.order_id == best_stop.order_id and s.type == best_stop.type)
            ]

        # Calculate approximate ETAs
        avg_speed = self.config.average_speed_kmh
        t = now
        eta_dropoff: dict[str, datetime] = {}
        prev_loc = courier.current_location

        for stop in route:
            dist_km = haversine_km(prev_loc, stop.location)
            travel_minutes = (dist_km / avg_speed) * 60 if avg_speed > 0 else 0
            t = add_minutes(t, travel_minutes)

            if stop.type == StopType.DROPOFF:
                eta_dropoff[stop.order_id] = t

            prev_loc = stop.location

        # Check SLA for each order
        sla_ms = self.config.sla_hours * 60 * 60 * 1000

        for o in orders:
            eta = eta_dropoff.get(o.id)
            if not eta:
                continue
            deadline = datetime.fromtimestamp(
                o.created_at.timestamp() + sla_ms / 1000
            )
            if eta > deadline:
                return False

        return True

    # ======================== Layer 4 ========================

    async def _choose_best_courier_with_precise_routing(
        self,
        new_order: DispatchOrder,
        couriers: list[DispatchCourier],
        all_orders_by_id: dict[str, DispatchOrder],
        now: datetime
    ) -> Optional[AssignmentResult]:
        """
        Layer 4: Precise routing and scoring.

        Uses Directions API to build exact routes and scores
        each courier based on distance, SLA slack, fairness, and overload.
        """
        results: list[AssignmentResult] = []

        for courier in couriers:
            plan = await self._build_precise_plan_for_courier(
                new_order, courier, all_orders_by_id, now
            )
            if not plan:
                continue

            score = self._score_plan(new_order, courier, plan, all_orders_by_id)
            results.append(AssignmentResult(
                order_id=new_order.id,
                courier_id=courier.id,
                plan=plan,
                score=score,
            ))

        if not results:
            return None

        # Sort by score (lower is better)
        results.sort(key=lambda r: r.score)
        return results[0]

    async def _build_precise_plan_for_courier(
        self,
        new_order: DispatchOrder,
        courier: DispatchCourier,
        all_orders_by_id: dict[str, DispatchOrder],
        now: datetime
    ) -> Optional[CourierPlan]:
        """Build a precise route plan for a courier with the new order."""
        order_ids = list(courier.assigned_open_order_ids) + [new_order.id]
        orders = [all_orders_by_id.get(oid) for oid in order_ids if oid in all_orders_by_id]
        orders = [o for o in orders if o is not None]

        if not orders:
            return CourierPlan(
                courier_id=courier.id,
                stops=[],
                polyline=None,
                total_distance_km=0.0,
                total_duration_minutes=0.0,
            )

        # Build waypoints for routing
        waypoint_info: list[tuple[Point, str, StopType]] = []
        for o in orders:
            waypoint_info.append((o.pickup, o.id, StopType.PICKUP))
            waypoint_info.append((o.dropoff, o.id, StopType.DROPOFF))

        waypoints = [w[0] for w in waypoint_info]

        # Get route from Directions API
        route = await self.routing.get_route(
            courier.current_location,
            waypoints,
            now,
            optimize=True  # Let Google optimize waypoint order
        )

        if not route.legs:
            return None

        # Build stops with ETAs
        stops: list[RouteStop] = []
        t = now

        for i, leg in enumerate(route.legs):
            t = add_minutes(t, leg.duration_minutes)

            if i < len(waypoint_info):
                _, order_id, stop_type = waypoint_info[i]
                stops.append(RouteStop(
                    order_id=order_id,
                    type=stop_type,
                    location=leg.to_point,
                    eta=t,
                ))

        # Check SLA feasibility
        sla_ms = self.config.sla_hours * 60 * 60 * 1000

        eta_by_order: dict[str, list[RouteStop]] = {}
        for stop in stops:
            if stop.order_id not in eta_by_order:
                eta_by_order[stop.order_id] = []
            eta_by_order[stop.order_id].append(stop)

        for order_id, order_stops in eta_by_order.items():
            order = all_orders_by_id.get(order_id)
            if not order:
                continue

            dropoff_stop = next(
                (s for s in order_stops if s.type == StopType.DROPOFF), None
            )
            if not dropoff_stop:
                continue

            deadline = datetime.fromtimestamp(
                order.created_at.timestamp() + sla_ms / 1000
            )
            if dropoff_stop.eta > deadline:
                return None  # SLA violation

        return CourierPlan(
            courier_id=courier.id,
            stops=stops,
            polyline=route.polyline,
            total_distance_km=route.total_distance_km,
            total_duration_minutes=route.total_duration_minutes,
        )

    def _score_plan(
        self,
        new_order: DispatchOrder,
        courier: DispatchCourier,
        plan: CourierPlan,
        all_orders_by_id: dict[str, DispatchOrder]
    ) -> float:
        """
        Score a courier plan for the new order.

        Lower score is better. Considers:
        - Distance penalty
        - Fairness penalty (deviation from target load)
        - Overload penalty (exceeding target)
        - SLA penalty (time buffer to deadline)
        """
        penalties = self.config.penalties
        target_orders = self.config.target_orders_per_courier_per_day
        sla_buffer = self.config.sla_buffer_minutes
        sla_ms = self.config.sla_hours * 60 * 60 * 1000

        # Load before and after assignment
        load_before = courier.completed_orders_today + len(courier.assigned_open_order_ids)
        load_after = load_before + 1

        # Distance penalty
        distance_penalty = penalties.distance * plan.total_distance_km

        # Fairness penalty (deviation from target)
        fairness_penalty = penalties.fairness * abs(load_after - target_orders)

        # Overload penalty (exceeding target)
        overload_penalty = penalties.overload * max(0, load_after - target_orders)

        # SLA penalty (based on minimum slack across all orders)
        min_slack_minutes = float("inf")

        for stop in plan.stops:
            if stop.type == StopType.DROPOFF:
                order = all_orders_by_id.get(stop.order_id)
                if not order:
                    continue
                deadline = datetime.fromtimestamp(
                    order.created_at.timestamp() + sla_ms / 1000
                )
                slack_minutes = (deadline.timestamp() - stop.eta.timestamp()) / 60
                if slack_minutes < min_slack_minutes:
                    min_slack_minutes = slack_minutes

        if min_slack_minutes == float("inf"):
            min_slack_minutes = sla_buffer

        sla_penalty = penalties.sla * max(0, sla_buffer - min_slack_minutes)

        # Total score
        score = distance_penalty + fairness_penalty + overload_penalty + sla_penalty

        return score
