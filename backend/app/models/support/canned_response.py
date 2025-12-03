"""Canned Response Model"""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class CannedResponse(TenantMixin, BaseModel):
    """
    Canned Response model - Pre-written responses for quick replies
    Used in tickets and live chat for common responses
    """

    __tablename__ = "canned_responses"

    # Response Identification
    title = Column(String(100), nullable=False, index=True, comment="Response title/name")
    shortcut = Column(
        String(50),
        unique=True,
        nullable=True,
        index=True,
        comment="Keyboard shortcut (e.g., /greeting)",
    )

    # Content
    content = Column(
        Text,
        nullable=False,
        comment="Response content (can include variables like {customer_name})",
    )

    # Categorization
    category = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Response category (e.g., greeting, closing, technical)",
    )

    # Status
    is_active = Column(
        Boolean, default=True, nullable=False, index=True, comment="Whether response is active"
    )
    is_public = Column(
        Boolean, default=True, nullable=False, comment="Whether response is available to all agents"
    )

    # Usage Tracking
    usage_count = Column(
        Integer, default=0, nullable=False, comment="Number of times this response was used"
    )

    # Authorship
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who created the response",
    )

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<CannedResponse {self.title}>"
