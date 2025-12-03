"""
Customer Feedback Model for Operations
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum as SQLEnum, Text, Numeric, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.mixins import TenantMixin
import enum


class FeedbackType(str, enum.Enum):
    """Type of feedback"""
    DELIVERY = "delivery"
    COURIER = "courier"
    SERVICE = "service"
    APP = "app"
    SUPPORT = "support"
    GENERAL = "general"


class FeedbackStatus(str, enum.Enum):
    """Feedback processing status"""
    PENDING = "pending"
    REVIEWED = "reviewed"
    RESPONDED = "responded"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    CLOSED = "closed"


class FeedbackSentiment(str, enum.Enum):
    """Feedback sentiment analysis"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class CustomerFeedback(TenantMixin, BaseModel):
    """Customer feedback and ratings for deliveries and service"""

    __tablename__ = "customer_feedbacks"

    # Feedback Identification
    feedback_number = Column(String(50), unique=True, nullable=False, index=True, comment="Unique feedback ID")
    feedback_type = Column(
        SQLEnum(FeedbackType, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        index=True
    )
    status = Column(
        SQLEnum(
            FeedbackStatus,
            name="customerfeedbackstatus",
            values_callable=lambda obj: [e.value for e in obj]
        ),
        default=FeedbackStatus.PENDING,
        nullable=False,
        index=True
    )

    # Subject of Feedback
    delivery_id = Column(Integer, ForeignKey("deliveries.id", ondelete="CASCADE"), index=True)
    courier_id = Column(Integer, ForeignKey("couriers.id", ondelete="SET NULL"), index=True)
    order_number = Column(String(100), index=True, comment="External order reference")

    # Customer Information
    customer_name = Column(String(200))
    customer_email = Column(String(200))
    customer_phone = Column(String(50))
    is_verified_customer = Column(Boolean, default=False)

    # Rating (1-5 stars)
    overall_rating = Column(Integer, nullable=False, comment="Overall rating 1-5")
    delivery_speed_rating = Column(Integer, comment="Delivery speed rating 1-5")
    courier_behavior_rating = Column(Integer, comment="Courier behavior rating 1-5")
    package_condition_rating = Column(Integer, comment="Package condition rating 1-5")
    communication_rating = Column(Integer, comment="Communication rating 1-5")

    # Feedback Content
    feedback_title = Column(String(200))
    feedback_text = Column(Text, nullable=False)
    sentiment = Column(
        SQLEnum(FeedbackSentiment, values_callable=lambda obj: [e.value for e in obj]),
        comment="AI-analyzed sentiment"
    )

    # Categories and Tags
    category = Column(String(100), index=True, comment="Feedback category")
    tags = Column(Text, comment="Comma-separated tags")
    is_complaint = Column(Boolean, default=False, index=True)
    is_compliment = Column(Boolean, default=False, index=True)

    # Response
    response_text = Column(Text)
    responded_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    responded_at = Column(DateTime)
    response_time_hours = Column(Numeric(10, 2), comment="Time taken to respond")

    # Resolution
    resolution_text = Column(Text)
    resolved_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    resolved_at = Column(DateTime)
    resolution_satisfaction = Column(Integer, comment="Customer satisfaction with resolution 1-5")

    # Escalation
    is_escalated = Column(Boolean, default=False, index=True)
    escalated_at = Column(DateTime)
    escalated_to_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    escalation_reason = Column(Text)

    # Impact
    compensation_amount = Column(Numeric(10, 2), default=0.0, comment="Compensation given")
    refund_amount = Column(Numeric(10, 2), default=0.0, comment="Refund given")
    action_taken = Column(Text, comment="Actions taken based on feedback")

    # Tracking
    source = Column(String(50), comment="Source: app, web, email, phone, social")
    device_type = Column(String(50), comment="Device used: ios, android, web")
    submitted_at = Column(DateTime, nullable=False)

    # Follow-up
    requires_followup = Column(Boolean, default=False)
    followup_date = Column(DateTime)
    followup_completed = Column(Boolean, default=False)
    followup_notes = Column(Text)

    # Internal Notes
    internal_notes = Column(Text, comment="Internal notes not visible to customer")
    priority = Column(String(20), default="normal", comment="low, normal, high, urgent")

    # Relationships
    delivery = relationship("Delivery")
    courier = relationship("Courier")

    def __repr__(self):
        return f"<CustomerFeedback {self.feedback_number}: {self.feedback_type.value} ({self.status.value})>"

    @property
    def is_pending(self) -> bool:
        """Check if feedback is pending review"""
        return self.status == FeedbackStatus.PENDING

    @property
    def is_resolved(self) -> bool:
        """Check if feedback is resolved"""
        return self.status in [FeedbackStatus.RESOLVED, FeedbackStatus.CLOSED]

    @property
    def is_negative(self) -> bool:
        """Check if feedback is negative"""
        return self.overall_rating <= 2 or self.is_complaint

    @property
    def needs_attention(self) -> bool:
        """Check if feedback requires immediate attention"""
        return (
            self.is_negative or
            self.is_escalated or
            self.priority in ["high", "urgent"]
        )


class FeedbackTemplate(TenantMixin, BaseModel):
    """Templates for responding to common feedback types"""

    __tablename__ = "feedback_templates"

    # Template Details
    template_code = Column(String(50), unique=True, nullable=False, index=True)
    template_name = Column(String(200), nullable=False)
    template_type = Column(
        SQLEnum(FeedbackType, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        index=True
    )

    # Content
    subject = Column(String(200))
    body = Column(Text, nullable=False)

    # Usage
    sentiment_type = Column(
        SQLEnum(FeedbackSentiment, values_callable=lambda obj: [e.value for e in obj]),
        comment="Which sentiment this template is for"
    )
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)

    # Creator
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))

    def __repr__(self):
        return f"<FeedbackTemplate {self.template_code}: {self.template_name}>"
