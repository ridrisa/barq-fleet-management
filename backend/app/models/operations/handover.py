from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum as SQLEnum, Text, Numeric
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.mixins import TenantMixin
import enum


class HandoverStatus(str, enum.Enum):
    """Handover transaction status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class HandoverType(str, enum.Enum):
    """Type of handover"""
    SHIFT_START = "shift_start"
    SHIFT_END = "shift_end"
    VEHICLE_SWAP = "vehicle_swap"
    EMERGENCY = "emergency"
    MAINTENANCE = "maintenance"


class Handover(TenantMixin, BaseModel):
    """Courier-to-courier handover records for vehicles, deliveries, and assets"""

    __tablename__ = "handovers"

    # Handover Details
    handover_number = Column(String(50), unique=True, nullable=False, index=True, comment="Unique handover ID")
    handover_type = Column(SQLEnum(HandoverType), nullable=False, index=True)
    status = Column(SQLEnum(HandoverStatus), default=HandoverStatus.PENDING, nullable=False, index=True)

    # Couriers Involved
    from_courier_id = Column(Integer, ForeignKey("couriers.id", ondelete="RESTRICT"), nullable=False, index=True)
    to_courier_id = Column(Integer, ForeignKey("couriers.id", ondelete="RESTRICT"), nullable=False, index=True)

    # Vehicle Information
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="RESTRICT"), index=True)
    vehicle_mileage_start = Column(Integer, comment="Odometer reading at handover")
    vehicle_fuel_level = Column(Numeric(5, 2), comment="Fuel level percentage 0-100")
    vehicle_condition = Column(Text, comment="Vehicle condition notes")

    # Delivery Items
    pending_deliveries_count = Column(Integer, default=0)
    pending_cod_amount = Column(Numeric(10, 2), default=0.0, comment="COD amount being transferred")

    # Timing
    scheduled_at = Column(DateTime, comment="Planned handover time")
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    # Verification
    from_courier_signature = Column(String(500), comment="Digital signature or URL")
    to_courier_signature = Column(String(500), comment="Digital signature or URL")
    witness_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), comment="Supervisor/witness")

    # Approval
    approved_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    approved_at = Column(DateTime)
    rejection_reason = Column(Text)

    # Documentation
    photos = Column(Text, comment="Comma-separated photo URLs")
    notes = Column(Text)
    checklist_completed = Column(Text, comment="JSON array of completed checklist items")

    # Discrepancy Tracking
    discrepancies_reported = Column(Text, comment="Issues found during handover")
    discrepancy_resolved = Column(String(20), default="pending", comment="pending, resolved, escalated")

    # Relationships
    from_courier = relationship("Courier", foreign_keys=[from_courier_id])
    to_courier = relationship("Courier", foreign_keys=[to_courier_id])
    vehicle = relationship("Vehicle")

    def __repr__(self):
        return f"<Handover {self.handover_number}: {self.from_courier_id} → {self.to_courier_id} ({self.status.value})>"

    @property
    def is_pending(self) -> bool:
        """Check if handover is awaiting action"""
        return self.status == HandoverStatus.PENDING

    @property
    def is_completed(self) -> bool:
        """Check if handover is fully completed"""
        return self.status == HandoverStatus.COMPLETED

    @property
    def has_discrepancies(self) -> bool:
        """Check if handover has reported issues"""
        return bool(self.discrepancies_reported)
