"""
Auto-Dispatch Engine for BARQ Fleet Management

This module implements a multi-layer dispatch algorithm for intelligent
order assignment to couriers.

Layers:
1. Layer 1 - Local filtering (online status, shift, zone, Haversine radius)
2. Layer 2 - Distance Matrix filtering (ETA to pickup threshold)
3. Layer 3 - Approximate route feasibility (Haversine + SLA check)
4. Layer 4 - Precise routing with scoring (Directions API + penalties)
"""

from app.services.dispatch.types import (
    Point,
    OrderStatus,
    CourierOnlineStatus,
    DispatchOrder,
    DispatchCourier,
    StopType,
    RouteStop,
    CourierPlan,
    AssignmentResult,
)
from app.services.dispatch.config import (
    PenaltyWeights,
    DispatchConfig,
    DEFAULT_DISPATCH_CONFIG,
)
from app.services.dispatch.geo import haversine_km, add_minutes
from app.services.dispatch.routing import (
    RoutingProvider,
    DistanceMatrixResult,
    RouteLeg,
    RouteResult,
)
from app.services.dispatch.google_routing import GoogleRoutingProvider
from app.services.dispatch.engine import DispatchEngine

__all__ = [
    # Types
    "Point",
    "OrderStatus",
    "CourierOnlineStatus",
    "DispatchOrder",
    "DispatchCourier",
    "StopType",
    "RouteStop",
    "CourierPlan",
    "AssignmentResult",
    # Config
    "PenaltyWeights",
    "DispatchConfig",
    "DEFAULT_DISPATCH_CONFIG",
    # Geo utilities
    "haversine_km",
    "add_minutes",
    # Routing
    "RoutingProvider",
    "DistanceMatrixResult",
    "RouteLeg",
    "RouteResult",
    "GoogleRoutingProvider",
    # Engine
    "DispatchEngine",
]
