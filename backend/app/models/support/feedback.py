"""Customer Feedback Model"""
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class FeedbackCategory(str, enum.Enum):
    """Feedback category"""
    GENERAL = "general"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    COMPLAINT = "complaint"
    COMPLIMENT = "compliment"
    SUGGESTION = "suggestion"


class FeedbackStatus(str, enum.Enum):
    """Feedback processing status"""
    NEW = "new"
    REVIEWED = "reviewed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DISMISSED = "dismissed"


class Feedback(BaseModel):
    """
    Customer Feedback model - Collects customer feedback
    Helps improve product and service quality
    """

    __tablename__ = "feedbacks"

    # Relationships
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User who submitted feedback (nullable for anonymous)"
    )

    # Content
    subject = Column(
        String(255),
        nullable=False,
        comment="Feedback subject"
    )
    message = Column(
        Text,
        nullable=False,
        comment="Feedback message"
    )

    # Categorization
    category = Column(
        SQLEnum(FeedbackCategory),
        nullable=False,
        index=True,
        comment="Feedback category"
    )

    # Rating
    rating = Column(
        Integer,
        nullable=True,
        comment="Rating (1-5 stars)"
    )

    # Status
    status = Column(
        SQLEnum(FeedbackStatus),
        default=FeedbackStatus.NEW,
        nullable=False,
        index=True,
        comment="Feedback processing status"
    )

    # Response
    response = Column(
        Text,
        nullable=True,
        comment="Response to the feedback"
    )
    responded_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who responded to feedback"
    )

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="feedbacks")
    responder = relationship("User", foreign_keys=[responded_by])

    def __repr__(self):
        return f"<Feedback {self.id}: {self.category.value} - {self.rating}★>"

    @property
    def is_positive(self) -> bool:
        """Check if feedback is positive (4-5 stars)"""
        return self.rating is not None and self.rating >= 4

    @property
    def is_negative(self) -> bool:
        """Check if feedback is negative (1-2 stars)"""
        return self.rating is not None and self.rating <= 2
