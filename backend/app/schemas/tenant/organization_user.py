"""Organization User schemas for API requests and responses"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.models.tenant.organization_user import OrganizationRole


class OrganizationUserBase(BaseModel):
    """Base organization user schema"""

    organization_id: int
    user_id: int
    role: OrganizationRole = OrganizationRole.VIEWER
    permissions: Optional[Dict[str, Any]] = None
    is_active: bool = True


class OrganizationUserCreate(BaseModel):
    """Schema for adding a user to an organization"""

    user_id: int
    role: OrganizationRole = OrganizationRole.VIEWER
    permissions: Optional[Dict[str, Any]] = None
    is_active: bool = True


class OrganizationUserUpdate(BaseModel):
    """Schema for updating organization user"""

    role: Optional[OrganizationRole] = None
    permissions: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class OrganizationUserResponse(OrganizationUserBase):
    """Schema for organization user response"""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrganizationUserWithDetails(OrganizationUserResponse):
    """Organization user response with user and organization details"""

    user_email: Optional[str] = None
    user_full_name: Optional[str] = None
    organization_name: Optional[str] = None
    organization_slug: Optional[str] = None
