"""FAQ Schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class FAQBase(BaseModel):
    """Base FAQ schema"""
    question: str = Field(..., min_length=5, max_length=500, description="FAQ question")
    answer: str = Field(..., min_length=5, description="FAQ answer (Markdown supported)")
    category: str = Field(..., min_length=1, max_length=100, description="FAQ category")
    order: int = Field(default=0, description="Display order within category")


class FAQCreate(FAQBase):
    """Schema for creating a new FAQ"""
    is_active: bool = Field(default=True, description="Whether FAQ is active")


class FAQUpdate(BaseModel):
    """Schema for updating a FAQ"""
    question: Optional[str] = Field(None, min_length=5, max_length=500)
    answer: Optional[str] = Field(None, min_length=5)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    order: Optional[int] = None
    is_active: Optional[bool] = None


class FAQResponse(FAQBase):
    """Schema for FAQ response"""
    id: int
    is_active: bool
    view_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FAQList(BaseModel):
    """Minimal FAQ schema for list views"""
    id: int
    question: str
    category: str
    order: int
    is_active: bool

    class Config:
        from_attributes = True


class FAQByCategory(BaseModel):
    """FAQs grouped by category"""
    category: str
    faqs: List[FAQResponse]


class FAQCategoryList(BaseModel):
    """List of FAQ categories with counts"""
    categories: Dict[str, int]
