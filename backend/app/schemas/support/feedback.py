"""Customer Feedback Schemas"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime

from app.models.support import FeedbackCategory, FeedbackStatus


class FeedbackBase(BaseModel):
    """Base feedback schema"""
    subject: str = Field(..., min_length=5, max_length=255, description="Feedback subject")
    message: str = Field(..., min_length=10, description="Feedback message")
    category: FeedbackCategory = Field(..., description="Feedback category")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating (1-5 stars)")

    @validator("rating")
    def validate_rating(cls, v):
        """Validate rating is between 1 and 5"""
        if v is not None and (v < 1 or v > 5):
            raise ValueError("Rating must be between 1 and 5")
        return v


class FeedbackCreate(FeedbackBase):
    """Schema for creating feedback"""
    pass


class FeedbackUpdate(BaseModel):
    """Schema for updating feedback"""
    subject: Optional[str] = Field(None, min_length=5, max_length=255)
    message: Optional[str] = Field(None, min_length=10)
    category: Optional[FeedbackCategory] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    status: Optional[FeedbackStatus] = None


class FeedbackRespond(BaseModel):
    """Schema for responding to feedback"""
    response: str = Field(..., min_length=10, description="Response message")


class FeedbackResponse(FeedbackBase):
    """Schema for feedback response"""
    id: int
    user_id: Optional[int] = None
    status: FeedbackStatus
    response: Optional[str] = None
    responded_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_positive: bool = Field(default=False, description="Whether feedback is positive (4-5 stars)")
    is_negative: bool = Field(default=False, description="Whether feedback is negative (1-2 stars)")

    class Config:
        from_attributes = True


class FeedbackList(BaseModel):
    """Minimal feedback schema for list views"""
    id: int
    subject: str
    category: FeedbackCategory
    rating: Optional[int] = None
    status: FeedbackStatus
    user_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackWithUser(FeedbackResponse):
    """Extended feedback with user information"""
    user_name: Optional[str] = None
    responder_name: Optional[str] = None

    class Config:
        from_attributes = True


class FeedbackStatistics(BaseModel):
    """Feedback statistics schema"""
    total: int = 0
    by_category: Dict[str, int] = Field(default_factory=dict)
    by_status: Dict[str, int] = Field(default_factory=dict)
    by_rating: Dict[int, int] = Field(default_factory=dict)
    average_rating: float = 0.0
    positive_count: int = 0
    negative_count: int = 0
    response_rate: float = 0.0
