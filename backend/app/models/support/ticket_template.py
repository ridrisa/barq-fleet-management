"""Ticket Template Model"""
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Enum as SQLEnum, Boolean, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.mixins import TenantMixin
from app.models.support.ticket import TicketCategory, TicketPriority


class TicketTemplate(TenantMixin, BaseModel):
    """
    Ticket Template model - Predefined templates for common ticket types
    Speeds up ticket creation with pre-filled fields
    """

    __tablename__ = "ticket_templates"

    # Template Identification
    name = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Template name"
    )
    description = Column(
        String(500),
        nullable=True,
        comment="Template description"
    )

    # Pre-filled Fields
    default_subject = Column(
        String(255),
        nullable=True,
        comment="Default subject for tickets"
    )
    default_description = Column(
        Text,
        nullable=True,
        comment="Default description template (can include placeholders)"
    )
    default_category = Column(
        SQLEnum(TicketCategory),
        nullable=True,
        comment="Default ticket category"
    )
    default_priority = Column(
        SQLEnum(TicketPriority),
        default=TicketPriority.MEDIUM,
        nullable=True,
        comment="Default ticket priority"
    )
    default_department = Column(
        String(100),
        nullable=True,
        comment="Default department for routing"
    )
    default_tags = Column(
        Text,
        nullable=True,
        comment="Default comma-separated tags"
    )
    default_custom_fields = Column(
        JSON,
        nullable=True,
        comment="Default custom fields as JSON"
    )

    # SLA Configuration
    sla_hours = Column(
        Integer,
        nullable=True,
        comment="SLA deadline in hours from creation"
    )

    # Template Status
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether template is active"
    )
    is_public = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether template is available to all users"
    )

    # Authorship
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who created the template"
    )

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<TicketTemplate {self.name}>"
