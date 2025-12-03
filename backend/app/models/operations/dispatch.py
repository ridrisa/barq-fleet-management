from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum as SQLEnum, Text, Numeric, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.mixins import TenantMixin
import enum


class DispatchStatus(str, enum.Enum):
    """Dispatch request status"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DispatchPriority(str, enum.Enum):
    """Dispatch priority level"""
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class DispatchAssignment(TenantMixin, BaseModel):
    """Dispatch assignments for delivery allocation"""

    __tablename__ = "dispatch_assignments"

    # Assignment Details
    assignment_number = Column(String(50), unique=True, nullable=False, index=True)
    status = Column(SQLEnum(DispatchStatus), default=DispatchStatus.PENDING, nullable=False, index=True)
    priority = Column(SQLEnum(DispatchPriority), default=DispatchPriority.NORMAL, index=True)

    # Delivery Reference
    delivery_id = Column(Integer, ForeignKey("deliveries.id", ondelete="CASCADE"), nullable=False, index=True)

    # Courier Assignment
    courier_id = Column(Integer, ForeignKey("couriers.id", ondelete="SET NULL"), index=True)
    zone_id = Column(Integer, ForeignKey("zones.id", ondelete="SET NULL"), index=True)

    # Timing
    created_at_time = Column(DateTime, nullable=False)
    assigned_at = Column(DateTime)
    accepted_at = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    # Assignment Logic
    assignment_algorithm = Column(String(50), comment="nearest, load_balanced, priority_based, manual")
    distance_to_pickup_km = Column(Numeric(10, 2), comment="Distance from courier to pickup")
    estimated_time_minutes = Column(Integer, comment="Estimated completion time")

    # Courier Availability
    courier_current_load = Column(Integer, default=0, comment="Number of active deliveries")
    courier_max_capacity = Column(Integer, default=5)
    courier_rating = Column(Numeric(3, 2), comment="Courier rating at assignment time")

    # Rejection/Cancellation
    rejection_reason = Column(Text)
    rejected_at = Column(DateTime)
    rejection_count = Column(Integer, default=0, comment="Number of times rejected")

    # Reassignment
    is_reassignment = Column(Boolean, default=False)
    previous_courier_id = Column(Integer, ForeignKey("couriers.id", ondelete="SET NULL"))
    reassignment_reason = Column(Text)

    # Performance
    actual_completion_time_minutes = Column(Integer)
    performance_variance = Column(Integer, comment="Difference from estimated time")

    # Dispatcher
    assigned_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    assignment_notes = Column(Text)

    # Real-time Updates
    last_location_update = Column(DateTime)
    current_latitude = Column(Numeric(10, 8))
    current_longitude = Column(Numeric(11, 8))

    # Relationships
    delivery = relationship("Delivery")
    courier = relationship("Courier", foreign_keys=[courier_id])
    zone = relationship("Zone")
    previous_courier = relationship("Courier", foreign_keys=[previous_courier_id])

    def __repr__(self):
        return f"<DispatchAssignment {self.assignment_number}: {self.status.value}>"

    @property
    def is_pending(self) -> bool:
        """Check if assignment is awaiting acceptance"""
        return self.status == DispatchStatus.PENDING

    @property
    def is_active(self) -> bool:
        """Check if assignment is currently active"""
        return self.status in [DispatchStatus.ASSIGNED, DispatchStatus.ACCEPTED, DispatchStatus.IN_PROGRESS]

    @property
    def is_completed_status(self) -> bool:
        """Check if assignment is in final state"""
        return self.status in [DispatchStatus.COMPLETED, DispatchStatus.CANCELLED, DispatchStatus.REJECTED]
