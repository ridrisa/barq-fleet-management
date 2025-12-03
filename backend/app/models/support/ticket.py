"""Support Ticket Model"""

import enum

from sqlalchemy import JSON, Boolean, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class TicketCategory(str, enum.Enum):
    """Ticket category types"""

    TECHNICAL = "technical"
    BILLING = "billing"
    DELIVERY = "delivery"
    COMPLAINT = "complaint"
    FEATURE_REQUEST = "feature_request"
    HR = "hr"
    VEHICLE = "vehicle"
    ACCOMMODATION = "accommodation"
    FINANCE = "finance"
    OPERATIONS = "operations"
    IT = "it"
    OTHER = "other"


class TicketPriority(str, enum.Enum):
    """Ticket priority levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketStatus(str, enum.Enum):
    """Ticket status workflow"""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING = "waiting"
    RESOLVED = "resolved"
    CLOSED = "closed"


class EscalationLevel(str, enum.Enum):
    """Ticket escalation levels"""

    NONE = "none"
    LEVEL_1 = "level_1"
    LEVEL_2 = "level_2"
    LEVEL_3 = "level_3"
    MANAGEMENT = "management"


class Ticket(TenantMixin, BaseModel):
    """Support Ticket model - Manages support requests and issues"""

    __tablename__ = "tickets"

    # Ticket Identification
    ticket_id = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique ticket identifier (e.g., TKT-20250106-001)",
    )

    # Relationships
    courier_id = Column(
        Integer,
        ForeignKey("couriers.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Related courier (nullable for non-courier issues)",
    )
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
        comment="User who created the ticket",
    )
    assigned_to = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User assigned to handle the ticket",
    )

    # Ticket Details
    category = Column(
        SQLEnum(TicketCategory), nullable=False, index=True, comment="Ticket category for routing"
    )
    priority = Column(
        SQLEnum(TicketPriority),
        default=TicketPriority.MEDIUM,
        nullable=False,
        index=True,
        comment="Ticket priority level",
    )
    status = Column(
        SQLEnum(TicketStatus),
        default=TicketStatus.OPEN,
        nullable=False,
        index=True,
        comment="Current ticket status",
    )

    # Content
    subject = Column(String(255), nullable=False, comment="Ticket subject/title")
    description = Column(Text, nullable=False, comment="Detailed description of the issue")
    resolution = Column(Text, nullable=True, comment="Resolution details when ticket is resolved")

    # SLA Tracking
    sla_due_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="SLA deadline for ticket resolution",
    )
    first_response_at = Column(
        DateTime(timezone=True), nullable=True, comment="When first response was made"
    )
    sla_breached = Column(
        Boolean, default=False, nullable=False, index=True, comment="Whether SLA was breached"
    )

    # Escalation
    escalation_level = Column(
        SQLEnum(EscalationLevel),
        default=EscalationLevel.NONE,
        nullable=False,
        index=True,
        comment="Current escalation level",
    )
    escalated_at = Column(
        DateTime(timezone=True), nullable=True, comment="When ticket was escalated"
    )
    escalated_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who escalated the ticket",
    )
    escalation_reason = Column(Text, nullable=True, comment="Reason for escalation")

    # Merge Support
    merged_into_id = Column(
        Integer,
        ForeignKey("tickets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID of ticket this was merged into",
    )
    is_merged = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Whether this ticket was merged into another",
    )

    # Template Reference
    template_id = Column(
        Integer,
        ForeignKey("ticket_templates.id", ondelete="SET NULL"),
        nullable=True,
        comment="Template used to create this ticket",
    )

    # Tags and Custom Fields
    tags = Column(Text, nullable=True, comment="Comma-separated tags")
    custom_fields = Column(JSON, nullable=True, comment="Custom fields as JSON object")

    # Contact Information
    contact_email = Column(String(255), nullable=True, comment="Contact email for notifications")
    contact_phone = Column(String(50), nullable=True, comment="Contact phone number")

    # Department Routing
    department = Column(
        String(100), nullable=True, index=True, comment="Department responsible for this ticket"
    )

    # Timestamps
    resolved_at = Column(DateTime(timezone=True), nullable=True, comment="When ticket was resolved")
    closed_at = Column(DateTime(timezone=True), nullable=True, comment="When ticket was closed")

    # Relationships
    courier = relationship("Courier", foreign_keys=[courier_id], backref="tickets")
    creator = relationship("User", foreign_keys=[created_by], backref="created_tickets")
    assignee = relationship("User", foreign_keys=[assigned_to], backref="assigned_tickets")
    escalator = relationship("User", foreign_keys=[escalated_by])
    replies = relationship("TicketReply", back_populates="ticket", cascade="all, delete-orphan")
    attachments = relationship(
        "TicketAttachment", back_populates="ticket", cascade="all, delete-orphan"
    )
    merged_tickets = relationship("Ticket", backref="parent_ticket", remote_side="Ticket.id")
    template = relationship("TicketTemplate", backref="tickets")

    def __repr__(self):
        return f"<Ticket {self.ticket_id}: {self.subject} ({self.status.value})>"

    @property
    def is_open(self) -> bool:
        """Check if ticket is open or in progress"""
        return self.status in [TicketStatus.OPEN, TicketStatus.IN_PROGRESS, TicketStatus.WAITING]

    @property
    def is_resolved(self) -> bool:
        """Check if ticket is resolved"""
        return self.status == TicketStatus.RESOLVED

    @property
    def is_closed(self) -> bool:
        """Check if ticket is closed"""
        return self.status == TicketStatus.CLOSED

    @property
    def is_high_priority(self) -> bool:
        """Check if ticket is high priority or urgent"""
        return self.priority in [TicketPriority.HIGH, TicketPriority.URGENT]

    @property
    def is_escalated(self) -> bool:
        """Check if ticket is escalated"""
        return self.escalation_level != EscalationLevel.NONE

    @property
    def sla_status(self) -> str:
        """Get SLA status"""
        if self.sla_breached:
            return "breached"
        if self.sla_due_at:
            from datetime import datetime, timezone

            now = datetime.now(timezone.utc)
            if self.sla_due_at < now:
                return "breached"
            return "active"
        return "not_set"
