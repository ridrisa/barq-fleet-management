"""FAQ Model"""

from sqlalchemy import Boolean, Column, Integer, String, Text

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class FAQ(TenantMixin, BaseModel):
    """
    FAQ model - Frequently Asked Questions
    Quick answers to common questions
    """

    __tablename__ = "faqs"

    # Content
    question = Column(String(500), nullable=False, index=True, comment="FAQ question")
    answer = Column(Text, nullable=False, comment="FAQ answer (Markdown supported)")

    # Categorization
    category = Column(String(100), nullable=False, index=True, comment="FAQ category")

    # Ordering
    order = Column(Integer, default=0, nullable=False, comment="Display order within category")

    # Status
    is_active = Column(
        Boolean, default=True, nullable=False, index=True, comment="Whether FAQ is active/visible"
    )

    # Analytics
    view_count = Column(
        Integer, default=0, nullable=False, comment="Number of times FAQ was viewed"
    )

    def __repr__(self):
        return f"<FAQ {self.id}: {self.question[:50]}...>"
