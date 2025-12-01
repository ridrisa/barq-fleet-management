"""Organization schemas for API requests and responses"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from app.models.tenant.organization import SubscriptionPlan, SubscriptionStatus
import re


class OrganizationBase(BaseModel):
    """Base organization schema"""
    name: str = Field(..., min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: bool = True
    subscription_plan: SubscriptionPlan = SubscriptionPlan.FREE
    subscription_status: SubscriptionStatus = SubscriptionStatus.TRIAL
    max_users: int = Field(default=5, ge=1)
    max_couriers: int = Field(default=10, ge=1)
    max_vehicles: int = Field(default=10, ge=1)
    trial_ends_at: Optional[datetime] = None
    settings: Optional[Dict[str, Any]] = None

    @field_validator("slug", mode="before")
    @classmethod
    def generate_slug(cls, v: Optional[str], info) -> str:
        """Generate slug from name if not provided"""
        if v:
            # Validate slug format (lowercase, alphanumeric, hyphens only)
            if not re.match(r"^[a-z0-9-]+$", v):
                raise ValueError(
                    "Slug must contain only lowercase letters, numbers, and hyphens"
                )
            return v
        # Generate from name if available
        if "name" in info.data:
            name = info.data["name"]
            slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
            return slug
        return ""


class OrganizationCreate(OrganizationBase):
    """Schema for creating a new organization"""
    name: str = Field(..., min_length=1, max_length=255)


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None
    subscription_plan: Optional[SubscriptionPlan] = None
    subscription_status: Optional[SubscriptionStatus] = None
    max_users: Optional[int] = Field(None, ge=1)
    max_couriers: Optional[int] = Field(None, ge=1)
    max_vehicles: Optional[int] = Field(None, ge=1)
    trial_ends_at: Optional[datetime] = None
    settings: Optional[Dict[str, Any]] = None

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        """Validate slug format"""
        if v and not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError(
                "Slug must contain only lowercase letters, numbers, and hyphens"
            )
        return v


class OrganizationResponse(OrganizationBase):
    """Schema for organization response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrganizationWithStats(OrganizationResponse):
    """Organization response with statistics"""
    user_count: int = 0
    courier_count: int = 0
    vehicle_count: int = 0


class SubscriptionUpgrade(BaseModel):
    """Schema for upgrading subscription"""
    subscription_plan: SubscriptionPlan
    max_users: Optional[int] = Field(None, ge=1)
    max_couriers: Optional[int] = Field(None, ge=1)
    max_vehicles: Optional[int] = Field(None, ge=1)
