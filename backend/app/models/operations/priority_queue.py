import enum

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class QueuePriority(str, enum.Enum):
    """Priority level in queue"""

    CRITICAL = "CRITICAL"  # Same-hour delivery
    URGENT = "URGENT"  # 2-hour delivery
    HIGH = "HIGH"  # 4-hour delivery
    NORMAL = "NORMAL"  # Same-day delivery
    LOW = "LOW"  # Next-day delivery


class QueueStatus(str, enum.Enum):
    """Queue entry status"""

    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    ASSIGNED = "ASSIGNED"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class PriorityQueueEntry(TenantMixin, BaseModel):
    """Priority queue for delivery scheduling and assignment"""

    __tablename__ = "priority_queue_entries"

    # Queue Entry Details
    queue_number = Column(String(50), unique=True, nullable=False, index=True)
    priority = Column(SQLEnum(QueuePriority, values_callable=lambda e: [m.value for m in e]), nullable=False, index=True)
    status = Column(SQLEnum(QueueStatus, values_callable=lambda e: [m.value for m in e]), default=QueueStatus.QUEUED, nullable=False, index=True)

    # Delivery Reference
    delivery_id = Column(
        Integer,
        ForeignKey("deliveries.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Priority Calculation
    base_priority_score = Column(Integer, nullable=False, comment="Base score 1-100")
    time_factor_score = Column(Integer, default=0, comment="Urgency-based score")
    customer_tier_score = Column(Integer, default=0, comment="Customer priority score")
    sla_factor_score = Column(Integer, default=0, comment="SLA compliance score")
    total_priority_score = Column(
        Integer, nullable=False, index=True, comment="Composite priority score"
    )

    # SLA Requirements
    sla_deadline = Column(
        DateTime, nullable=False, index=True, comment="Must be delivered by this time"
    )
    sla_buffer_minutes = Column(Integer, default=30, comment="Buffer time before deadline")
    warning_threshold = Column(DateTime, comment="Time to trigger warning")

    # Customer Information
    customer_tier = Column(String(20), comment="premium, vip, standard, basic")
    is_vip_customer = Column(Boolean, default=False, index=True)
    customer_special_instructions = Column(Text)

    # Timing
    queued_at = Column(DateTime, nullable=False, index=True)
    assigned_at = Column(DateTime)
    processing_started_at = Column(DateTime)
    completed_at = Column(DateTime)
    expired_at = Column(DateTime)

    # Queue Position
    queue_position = Column(Integer, index=True, comment="Position in queue (1=first)")
    estimated_wait_time_minutes = Column(Integer, comment="Estimated time until assignment")

    # Assignment Constraints
    required_zone_id = Column(Integer, ForeignKey("zones.id", ondelete="SET NULL"), index=True)
    required_vehicle_type = Column(String(50), comment="bike, car, van")
    required_skills = Column(Text, comment="JSON array of required courier skills")

    # Matching Criteria
    preferred_courier_id = Column(Integer, ForeignKey("couriers.id", ondelete="SET NULL"))
    excluded_courier_ids = Column(Text, comment="JSON array of excluded courier IDs")
    min_courier_rating = Column(Numeric(3, 2), comment="Minimum courier rating required")

    # Business Rules
    delivery_window_start = Column(DateTime, comment="Earliest acceptable delivery time")
    delivery_window_end = Column(DateTime, comment="Latest acceptable delivery time")
    max_assignment_attempts = Column(Integer, default=3)
    assignment_attempts = Column(Integer, default=0)

    # Escalation
    is_escalated = Column(Boolean, default=False, index=True)
    escalated_at = Column(DateTime)
    escalation_reason = Column(Text)
    escalated_to_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))

    # Performance Tracking
    time_in_queue_minutes = Column(Integer, comment="Total time spent in queue")
    was_sla_met = Column(Boolean)
    sla_breach_minutes = Column(Integer, comment="Minutes past SLA deadline")

    # Relationships
    delivery = relationship("Delivery")
    zone = relationship("Zone")
    preferred_courier = relationship("Courier", foreign_keys=[preferred_courier_id])

    def __repr__(self):
        return f"<PriorityQueueEntry {self.queue_number}: Priority {self.priority.value} ({self.status.value})>"

    @property
    def is_queued(self) -> bool:
        """Check if entry is waiting in queue"""
        return self.status == QueueStatus.QUEUED

    @property
    def is_urgent(self) -> bool:
        """Check if entry is urgent or critical"""
        return self.priority in [QueuePriority.CRITICAL, QueuePriority.URGENT]

    @property
    def is_at_risk(self) -> bool:
        """Check if approaching SLA deadline"""
        from datetime import datetime, timedelta

        if not self.sla_deadline:
            return False
        warning_time = self.sla_deadline - timedelta(minutes=self.sla_buffer_minutes)
        return datetime.utcnow() >= warning_time
