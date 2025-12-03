"""Role and Permission Schemas"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# Permission Schemas
class PermissionBase(BaseModel):
    """Base permission schema"""

    name: str = Field(..., max_length=100)
    resource: str = Field(..., max_length=50)
    action: str = Field(..., max_length=20)
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    """Schema for creating permission"""

    pass


class PermissionUpdate(BaseModel):
    """Schema for updating permission"""

    description: Optional[str] = None


class PermissionResponse(PermissionBase):
    """Schema for permission response"""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Role Schemas
class RoleBase(BaseModel):
    """Base role schema"""

    name: str = Field(..., max_length=50)
    display_name: str = Field(..., max_length=100)
    description: Optional[str] = None
    is_active: bool = True


class RoleCreate(RoleBase):
    """Schema for creating role"""

    permission_ids: List[int] = []


class RoleUpdate(BaseModel):
    """Schema for updating role"""

    display_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    permission_ids: Optional[List[int]] = None


class RoleResponse(RoleBase):
    """Schema for role response"""

    id: int
    is_system_role: bool
    created_at: datetime
    updated_at: datetime
    permissions: List[PermissionResponse] = []

    model_config = {"from_attributes": True}


class RoleWithUsersResponse(RoleResponse):
    """Schema for role response with user count"""

    user_count: int


class UserRoleAssignment(BaseModel):
    """Schema for assigning roles to user"""

    user_id: int
    role_ids: List[int]
