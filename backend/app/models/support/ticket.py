"""Support Ticket Model"""
from sqlalchemy import Column, String, Integer, ForeignKey, Enum as SQLEnum, Text, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class TicketCategory(str, enum.Enum):
    """Ticket category types"""
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
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Ticket(BaseModel):
    """Support Ticket model - Manages support requests and issues"""

    __tablename__ = "tickets"

    # Ticket Identification
    ticket_id = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique ticket identifier (e.g., TKT-20250106-001)"
    )

    # Relationships
    courier_id = Column(
        Integer,
        ForeignKey("couriers.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Related courier (nullable for non-courier issues)"
    )
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
        comment="User who created the ticket"
    )
    assigned_to = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User assigned to handle the ticket"
    )

    # Ticket Details
    category = Column(
        SQLEnum(TicketCategory),
        nullable=False,
        index=True,
        comment="Ticket category for routing"
    )
    priority = Column(
        SQLEnum(TicketPriority),
        default=TicketPriority.MEDIUM,
        nullable=False,
        index=True,
        comment="Ticket priority level"
    )
    status = Column(
        SQLEnum(TicketStatus),
        default=TicketStatus.OPEN,
        nullable=False,
        index=True,
        comment="Current ticket status"
    )

    # Content
    subject = Column(String(255), nullable=False, comment="Ticket subject/title")
    description = Column(Text, nullable=False, comment="Detailed description of the issue")
    resolution = Column(Text, nullable=True, comment="Resolution details when ticket is resolved")

    # Timestamps
    resolved_at = Column(DateTime(timezone=True), nullable=True, comment="When ticket was resolved")
    closed_at = Column(DateTime(timezone=True), nullable=True, comment="When ticket was closed")

    # Relationships
    courier = relationship("Courier", foreign_keys=[courier_id], backref="tickets")
    creator = relationship("User", foreign_keys=[created_by], backref="created_tickets")
    assignee = relationship("User", foreign_keys=[assigned_to], backref="assigned_tickets")
    replies = relationship("TicketReply", back_populates="ticket", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Ticket {self.ticket_id}: {self.subject} ({self.status.value})>"

    @property
    def is_open(self) -> bool:
        """Check if ticket is open or in progress"""
        return self.status in [TicketStatus.OPEN, TicketStatus.IN_PROGRESS, TicketStatus.PENDING]

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
