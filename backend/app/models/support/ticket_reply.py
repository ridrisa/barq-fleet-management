"""Ticket Reply Model - for ticket threading/conversations"""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class TicketReply(TenantMixin, BaseModel):
    """
    Ticket Reply model - Manages threaded conversations on tickets
    Allows multiple replies and back-and-forth communication
    """

    __tablename__ = "ticket_replies"

    # Relationships
    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Parent ticket ID",
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="User who created this reply",
    )

    # Content
    message = Column(Text, nullable=False, comment="Reply message content")
    is_internal = Column(
        Boolean, default=False, comment="Whether this is an internal note (True) or customer-facing (False)"
    )

    # Relationships
    ticket = relationship("Ticket", back_populates="replies")
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<TicketReply {self.id} on Ticket {self.ticket_id}>"
