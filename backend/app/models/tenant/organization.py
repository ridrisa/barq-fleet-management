"""Organization model for multi-tenant support"""

import enum
from sqlalchemy import Column, String, Boolean, Integer, Enum, DateTime, JSON
from app.models.base import BaseModel


class SubscriptionPlan(enum.Enum):
    """Subscription plan types"""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(enum.Enum):
    """Subscription status types"""
    TRIAL = "trial"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class Organization(BaseModel):
    """
    Organization model for multi-tenant SaaS
    Each organization represents a separate tenant with its own data isolation
    """
    __tablename__ = "organizations"

    # Basic Information
    name = Column(String(255), unique=True, nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Subscription Information
    subscription_plan = Column(
        Enum(SubscriptionPlan),
        default=SubscriptionPlan.FREE,
        nullable=False
    )
    subscription_status = Column(
        Enum(SubscriptionStatus),
        default=SubscriptionStatus.TRIAL,
        nullable=False
    )

    # Resource Limits
    max_users = Column(Integer, default=5, nullable=False)
    max_couriers = Column(Integer, default=10, nullable=False)
    max_vehicles = Column(Integer, default=10, nullable=False)

    # Trial Information
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)

    # Custom Settings (JSON field for flexible configuration)
    settings = Column(JSON, default=dict, nullable=True)

    def __repr__(self):
        return f"<Organization {self.name} ({self.subscription_plan.value})>"
