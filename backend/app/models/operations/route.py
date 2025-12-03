"""
Route Management Model for Operations
"""

import enum

from sqlalchemy import JSON, Boolean, Column, Date, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class RouteStatus(str, enum.Enum):
    """Route operational status"""

    PLANNED = "planned"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Route(TenantMixin, BaseModel):
    """Delivery routes for courier operations"""

    __tablename__ = "routes"

    # Route Identification
    route_number = Column(String(50), unique=True, index=True, comment="Unique route identifier")
    route_name = Column(String(200), nullable=False)
    status = Column(SQLEnum(RouteStatus), default=RouteStatus.PLANNED, nullable=False, index=True)

    # Courier Assignment
    courier_id = Column(Integer, ForeignKey("couriers.id", ondelete="SET NULL"), index=True)
    zone_id = Column(Integer, ForeignKey("zones.id", ondelete="SET NULL"), index=True)

    # Schedule
    route_date = Column(Date, nullable=False, index=True, name="date")
    scheduled_start_time = Column(DateTime)
    scheduled_end_time = Column(DateTime)
    actual_start_time = Column(DateTime)
    actual_end_time = Column(DateTime)

    # Route Details
    start_location = Column(String(500), comment="Starting address/location")
    start_latitude = Column(Numeric(10, 8))
    start_longitude = Column(Numeric(11, 8))
    end_location = Column(String(500), comment="Ending address/location")
    end_latitude = Column(Numeric(10, 8))
    end_longitude = Column(Numeric(11, 8))

    # Waypoints (JSON array of stops)
    waypoints = Column(JSON, comment="Array of waypoint objects with order, address, lat/lng")
    total_stops = Column(Integer, default=0, comment="Number of stops on route")

    # Distance and Time Estimates
    total_distance_km = Column(
        Numeric(10, 2), name="total_distance", comment="Total distance in kilometers"
    )
    estimated_duration_minutes = Column(
        Integer, name="estimated_time", comment="Estimated duration in minutes"
    )
    actual_distance_km = Column(Numeric(10, 2), comment="Actual distance traveled")
    actual_duration_minutes = Column(Integer, comment="Actual duration in minutes")

    # Optimization
    is_optimized = Column(Boolean, default=False)
    optimization_algorithm = Column(String(50), comment="Algorithm used for optimization")
    optimization_score = Column(Numeric(5, 2), comment="Optimization quality score 0-100")

    # Delivery Tracking
    total_deliveries = Column(Integer, default=0)
    completed_deliveries = Column(Integer, default=0)
    failed_deliveries = Column(Integer, default=0)

    # Performance
    avg_time_per_stop_minutes = Column(Numeric(10, 2))
    distance_variance_km = Column(Numeric(10, 2), comment="Difference from planned distance")
    time_variance_minutes = Column(Integer, comment="Difference from planned time")

    # Notes and Instructions
    notes = Column(Text)
    special_instructions = Column(Text)
    internal_notes = Column(Text)

    # Audit
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    assigned_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    assigned_at = Column(DateTime)

    # Relationships
    courier = relationship("Courier")
    zone = relationship("Zone")

    def __repr__(self):
        return f"<Route {self.route_number or self.id}: {self.route_name} ({self.status.value})>"

    @property
    def is_active(self) -> bool:
        """Check if route is currently active"""
        return self.status in [RouteStatus.ASSIGNED, RouteStatus.IN_PROGRESS]

    @property
    def is_completed(self) -> bool:
        """Check if route is completed"""
        return self.status == RouteStatus.COMPLETED

    @property
    def completion_rate(self) -> float:
        """Calculate delivery completion rate"""
        if self.total_deliveries == 0:
            return 0.0
        return (self.completed_deliveries / self.total_deliveries) * 100

    @property
    def efficiency_score(self) -> float:
        """Calculate route efficiency based on distance and time variance"""
        if not self.is_completed:
            return 0.0

        score = 100.0

        # Deduct for distance variance
        if self.distance_variance_km and self.total_distance_km:
            variance_pct = (
                abs(float(self.distance_variance_km)) / float(self.total_distance_km) * 100
            )
            score -= min(variance_pct, 20)  # Max 20 point deduction

        # Deduct for time variance
        if self.time_variance_minutes and self.estimated_duration_minutes:
            variance_pct = abs(self.time_variance_minutes) / self.estimated_duration_minutes * 100
            score -= min(variance_pct, 20)  # Max 20 point deduction

        # Deduct for failed deliveries
        if self.total_deliveries > 0:
            failure_rate = (self.failed_deliveries / self.total_deliveries) * 100
            score -= min(failure_rate, 30)  # Max 30 point deduction

        return max(score, 0.0)
