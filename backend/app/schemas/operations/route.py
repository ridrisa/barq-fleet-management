from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class RouteStatus(str, Enum):
    PLANNED = "planned"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RouteBase(BaseModel):
    route_name: str = Field(..., min_length=2, max_length=100)
    courier_id: Optional[int] = Field(None, description="Assigned courier ID")
    route_date: date
    zone_id: Optional[int] = None
    start_location: Optional[str] = None
    end_location: Optional[str] = None
    waypoints: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    notes: Optional[str] = None


class RouteCreate(RouteBase):
    delivery_ids: List[int] = Field(
        default_factory=list, description="Deliveries to include in route"
    )
    optimize: bool = Field(True, description="Auto-optimize route order")


class RouteUpdate(BaseModel):
    route_name: Optional[str] = Field(None, min_length=2, max_length=100)
    courier_id: Optional[int] = None
    status: Optional[RouteStatus] = None
    route_date: Optional[date] = None
    zone_id: Optional[int] = None
    start_location: Optional[str] = None
    end_location: Optional[str] = None
    waypoints: Optional[List[Dict[str, Any]]] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    actual_distance_km: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class RouteOptimize(BaseModel):
    """Schema for route optimization request"""

    delivery_ids: List[int] = Field(..., min_items=1)
    start_location: Optional[Dict[str, float]] = Field(None, description="Starting lat/lng")
    optimize_for: str = Field("time", pattern="^(time|distance|priority)$")


class RouteAssign(BaseModel):
    """Schema for assigning route to courier"""

    courier_id: int
    scheduled_start_time: datetime


class RouteResponse(RouteBase):
    id: int
    status: RouteStatus = RouteStatus.PLANNED
    total_distance_km: Optional[float] = None
    estimated_duration_minutes: Optional[int] = None
    actual_distance_km: Optional[float] = None
    actual_duration_minutes: Optional[int] = None
    total_deliveries: int = 0
    completed_deliveries: int = 0
    scheduled_start_time: Optional[datetime] = None
    scheduled_end_time: Optional[datetime] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    is_optimized: bool = False
    optimization_score: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RouteMetrics(BaseModel):
    """Route performance metrics"""

    route_id: int
    route_name: str
    total_deliveries: int
    completed_deliveries: int
    failed_deliveries: int
    completion_rate: float
    planned_distance_km: float
    actual_distance_km: float
    distance_variance: float
    planned_duration_minutes: int
    actual_duration_minutes: int
    time_variance_minutes: int
    avg_time_per_delivery_minutes: float

    model_config = ConfigDict(from_attributes=True)
