"""
Customer Feedback Schemas
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from decimal import Decimal


class FeedbackType(str, Enum):
    DELIVERY = "delivery"
    COURIER = "courier"
    SERVICE = "service"
    APP = "app"
    SUPPORT = "support"
    GENERAL = "general"


class FeedbackStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    RESPONDED = "responded"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    CLOSED = "closed"


class FeedbackSentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


# Customer Feedback Schemas
class CustomerFeedbackBase(BaseModel):
    feedback_type: FeedbackType
    delivery_id: Optional[int] = None
    courier_id: Optional[int] = None
    order_number: Optional[str] = Field(None, max_length=100)
    customer_name: Optional[str] = Field(None, max_length=200)
    customer_email: Optional[str] = Field(None, max_length=200)
    customer_phone: Optional[str] = Field(None, max_length=50)
    overall_rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    delivery_speed_rating: Optional[int] = Field(None, ge=1, le=5)
    courier_behavior_rating: Optional[int] = Field(None, ge=1, le=5)
    package_condition_rating: Optional[int] = Field(None, ge=1, le=5)
    communication_rating: Optional[int] = Field(None, ge=1, le=5)
    feedback_title: Optional[str] = Field(None, max_length=200)
    feedback_text: str = Field(..., min_length=10, max_length=2000)
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[str] = None
    is_complaint: bool = False
    is_compliment: bool = False
    source: Optional[str] = Field(None, pattern="^(app|web|email|phone|social)$")
    device_type: Optional[str] = Field(None, pattern="^(ios|android|web)$")

    @field_validator('overall_rating', 'delivery_speed_rating', 'courier_behavior_rating',
                     'package_condition_rating', 'communication_rating')
    @classmethod
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Rating must be between 1 and 5')
        return v


class CustomerFeedbackCreate(CustomerFeedbackBase):
    submitted_at: Optional[datetime] = None


class CustomerFeedbackUpdate(BaseModel):
    status: Optional[FeedbackStatus] = None
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[str] = None
    sentiment: Optional[FeedbackSentiment] = None
    priority: Optional[str] = Field(None, pattern="^(low|normal|high|urgent)$")
    internal_notes: Optional[str] = None


class CustomerFeedbackResponse(CustomerFeedbackBase):
    id: int
    feedback_number: str
    status: FeedbackStatus
    sentiment: Optional[FeedbackSentiment] = None
    is_verified_customer: bool
    response_text: Optional[str] = None
    responded_by_id: Optional[int] = None
    responded_at: Optional[datetime] = None
    response_time_hours: Optional[Decimal] = None
    resolution_text: Optional[str] = None
    resolved_by_id: Optional[int] = None
    resolved_at: Optional[datetime] = None
    resolution_satisfaction: Optional[int] = None
    is_escalated: bool
    escalated_at: Optional[datetime] = None
    escalated_to_id: Optional[int] = None
    escalation_reason: Optional[str] = None
    compensation_amount: Decimal
    refund_amount: Decimal
    action_taken: Optional[str] = None
    submitted_at: datetime
    requires_followup: bool
    followup_date: Optional[datetime] = None
    followup_completed: bool
    priority: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FeedbackRespondSchema(BaseModel):
    """Schema for responding to feedback"""
    response_text: str = Field(..., min_length=10, max_length=2000)
    use_template: Optional[str] = None
    send_email: bool = True
    internal_notes: Optional[str] = None


class FeedbackResolveSchema(BaseModel):
    """Schema for resolving feedback"""
    resolution_text: str = Field(..., min_length=10, max_length=2000)
    compensation_amount: Optional[Decimal] = Field(None, ge=0)
    refund_amount: Optional[Decimal] = Field(None, ge=0)
    action_taken: Optional[str] = None
    notify_customer: bool = True


class FeedbackEscalateSchema(BaseModel):
    """Schema for escalating feedback"""
    escalated_to_id: int
    escalation_reason: str = Field(..., min_length=10, max_length=500)
    priority: str = Field("high", pattern="^(normal|high|urgent)$")


class FeedbackFollowupSchema(BaseModel):
    """Schema for scheduling follow-up"""
    followup_date: datetime
    followup_notes: Optional[str] = None


# Feedback Template Schemas
class FeedbackTemplateBase(BaseModel):
    template_code: str = Field(..., min_length=2, max_length=50)
    template_name: str = Field(..., min_length=3, max_length=200)
    template_type: FeedbackType
    subject: Optional[str] = Field(None, max_length=200)
    body: str = Field(..., min_length=10)
    sentiment_type: Optional[FeedbackSentiment] = None


class FeedbackTemplateCreate(FeedbackTemplateBase):
    is_active: bool = True


class FeedbackTemplateUpdate(BaseModel):
    template_name: Optional[str] = Field(None, min_length=3, max_length=200)
    subject: Optional[str] = Field(None, max_length=200)
    body: Optional[str] = Field(None, min_length=10)
    sentiment_type: Optional[FeedbackSentiment] = None
    is_active: Optional[bool] = None


class FeedbackTemplateResponse(FeedbackTemplateBase):
    id: int
    is_active: bool
    usage_count: int
    created_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Analytics Schemas
class FeedbackMetrics(BaseModel):
    """Feedback performance metrics"""
    period: str
    total_feedbacks: int
    avg_overall_rating: float
    avg_delivery_speed_rating: float
    avg_courier_behavior_rating: float
    avg_package_condition_rating: float
    avg_communication_rating: float
    complaints_count: int
    compliments_count: int
    response_rate: float
    avg_response_time_hours: float
    resolution_rate: float
    avg_resolution_satisfaction: float
    escalation_rate: float
    sentiment_distribution: Dict[str, int]
    rating_distribution: Dict[str, int]
    top_categories: List[Dict[str, Any]]

    model_config = ConfigDict(from_attributes=True)


class FeedbackSummary(BaseModel):
    """Summary of feedback for a courier or delivery"""
    subject_id: int
    subject_type: str
    total_feedbacks: int
    avg_rating: float
    positive_count: int
    neutral_count: int
    negative_count: int
    complaints_count: int
    recent_feedbacks: List[CustomerFeedbackResponse]

    model_config = ConfigDict(from_attributes=True)
