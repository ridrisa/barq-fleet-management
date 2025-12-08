"""
Domain Types for the Dispatch Engine
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


@dataclass
class Point:
    """Geographic coordinate point"""
    lat: float
    lng: float

    def to_tuple(self) -> tuple[float, float]:
        return (self.lat, self.lng)

    def __repr__(self) -> str:
        return f"Point({self.lat:.6f}, {self.lng:.6f})"


class OrderStatus(str, Enum):
    """Order status for dispatch purposes"""
    UNASSIGNED = "unassigned"
    ASSIGNED = "assigned"
    PICKED_UP = "picked_up"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class CourierOnlineStatus(str, Enum):
    """Courier availability status"""
    ONLINE = "online"
    OFFLINE = "offline"
    BREAK = "break"


class StopType(str, Enum):
    """Type of route stop"""
    PICKUP = "pickup"
    DROPOFF = "dropoff"


@dataclass
class DispatchOrder:
    """Order representation for dispatch engine"""
    id: str
    pickup: Point
    dropoff: Point
    created_at: datetime
    deadline_at: datetime  # Should be created_at + sla_hours
    status: OrderStatus
    zone_id: Optional[str] = None

    @property
    def is_unassigned(self) -> bool:
        return self.status == OrderStatus.UNASSIGNED

    @property
    def is_active(self) -> bool:
        return self.status in [OrderStatus.ASSIGNED, OrderStatus.PICKED_UP]


@dataclass
class DispatchCourier:
    """Courier representation for dispatch engine"""
    id: str
    current_location: Point
    online_status: CourierOnlineStatus
    shift_end_at: datetime
    completed_orders_today: int
    assigned_open_order_ids: list[str] = field(default_factory=list)
    zone_id: Optional[str] = None

    @property
    def is_available(self) -> bool:
        return self.online_status == CourierOnlineStatus.ONLINE

    @property
    def current_load(self) -> int:
        return len(self.assigned_open_order_ids)


@dataclass
class RouteStop:
    """A single stop in a courier's route"""
    order_id: str
    type: StopType
    location: Point
    eta: datetime


@dataclass
class CourierPlan:
    """Complete route plan for a courier"""
    courier_id: str
    stops: list[RouteStop] = field(default_factory=list)
    polyline: Optional[str] = None
    total_distance_km: float = 0.0
    total_duration_minutes: float = 0.0


@dataclass
class AssignmentResult:
    """Result of order assignment"""
    order_id: str
    courier_id: str
    plan: CourierPlan
    score: float = 0.0  # Lower is better
