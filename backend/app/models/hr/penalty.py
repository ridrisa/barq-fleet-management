"""
Penalty Model for HR module.

Records penalties/deductions applied to couriers for various infractions
such as SLA violations, attendance issues, traffic violations, etc.
"""

import enum
from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class PenaltyType(str, enum.Enum):
    """Types of penalties that can be applied"""
    SLA_VIOLATION = "sla_violation"
    ATTENDANCE = "attendance"
    TRAFFIC_VIOLATION = "traffic_violation"
    VEHICLE_DAMAGE = "vehicle_damage"
    CUSTOMER_COMPLAINT = "customer_complaint"
    POLICY_VIOLATION = "policy_violation"
    LATE_DELIVERY = "late_delivery"
    MISSING_ITEM = "missing_item"
    MISCONDUCT = "misconduct"
    OTHER = "other"


class PenaltyStatus(str, enum.Enum):
    """Status of the penalty"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPEALED = "appealed"
    WAIVED = "waived"
    APPLIED = "applied"


class Penalty(TenantMixin, BaseModel):
    """
    Penalty/Deduction record for a courier.

    Used to track financial penalties applied for various infractions.
    Can be linked to salary deductions, SLA breaches, incidents, etc.
    """
    __tablename__ = "penalties"

    # Courier association
    courier_id = Column(
        Integer,
        ForeignKey("couriers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Courier receiving the penalty"
    )

    # Penalty details
    penalty_type = Column(
        Enum(PenaltyType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
        comment="Type of penalty"
    )
    status = Column(
        Enum(PenaltyStatus, values_callable=lambda x: [e.value for e in x]),
        default=PenaltyStatus.PENDING,
        nullable=False,
        index=True,
        comment="Current status of the penalty"
    )

    # Financial
    amount = Column(
        Numeric(10, 2),
        nullable=False,
        comment="Penalty amount in SAR"
    )

    # Context
    reason = Column(
        Text,
        nullable=False,
        comment="Detailed reason for the penalty"
    )
    incident_date = Column(
        Date,
        nullable=False,
        default=date.today,
        comment="Date when the incident occurred"
    )
    reference_number = Column(
        String(50),
        nullable=True,
        unique=True,
        index=True,
        comment="Reference/ticket number if applicable"
    )

    # Related records
    incident_id = Column(
        Integer,
        ForeignKey("incidents.id", ondelete="SET NULL"),
        nullable=True,
        comment="Related incident if applicable"
    )
    sla_tracking_id = Column(
        Integer,
        ForeignKey("sla_tracking.id", ondelete="SET NULL"),
        nullable=True,
        comment="Related SLA tracking if applicable"
    )
    delivery_id = Column(
        Integer,
        ForeignKey("deliveries.id", ondelete="SET NULL"),
        nullable=True,
        comment="Related delivery if applicable"
    )

    # Approval workflow
    created_by_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who created the penalty"
    )
    approved_by_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who approved the penalty"
    )
    approved_at = Column(
        DateTime,
        nullable=True,
        comment="When the penalty was approved"
    )

    # Appeal handling
    appeal_reason = Column(
        Text,
        nullable=True,
        comment="Reason for appeal if appealed"
    )
    appeal_resolved_at = Column(
        DateTime,
        nullable=True,
        comment="When the appeal was resolved"
    )
    appeal_resolution = Column(
        Text,
        nullable=True,
        comment="Resolution of the appeal"
    )

    # Salary linkage
    salary_id = Column(
        Integer,
        ForeignKey("salaries.id", ondelete="SET NULL"),
        nullable=True,
        comment="Salary record where penalty was deducted"
    )
    applied_at = Column(
        DateTime,
        nullable=True,
        comment="When the penalty was applied to salary"
    )

    # Notes
    notes = Column(Text, nullable=True)

    # Relationships
    courier = relationship("Courier", backref="penalties")

    def __repr__(self):
        return f"<Penalty {self.id}: {self.penalty_type.value} - SAR {self.amount} for courier {self.courier_id}>"

    @property
    def is_appealable(self) -> bool:
        """Check if penalty can be appealed"""
        return self.status in [PenaltyStatus.PENDING, PenaltyStatus.APPROVED]

    @property
    def is_editable(self) -> bool:
        """Check if penalty can be edited"""
        return self.status == PenaltyStatus.PENDING
