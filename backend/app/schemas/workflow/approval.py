from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DELEGATED = "delegated"
    EXPIRED = "expired"


# Approval Chain Schemas
class ApprovalChainBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    workflow_template_id: Optional[int] = None
    levels: int = Field(default=1, ge=1, le=10)
    is_sequential: bool = True
    allow_delegation: bool = False
    auto_escalate: bool = True
    escalation_hours: int = Field(default=24, ge=1)
    is_active: bool = True


class ApprovalChainCreate(ApprovalChainBase):
    pass


class ApprovalChainUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    levels: Optional[int] = Field(None, ge=1, le=10)
    is_sequential: Optional[bool] = None
    allow_delegation: Optional[bool] = None
    auto_escalate: Optional[bool] = None
    escalation_hours: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class ApprovalChainResponse(ApprovalChainBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Approval Chain Approver Schemas
class ApprovalChainApproverBase(BaseModel):
    approval_chain_id: int
    user_id: int
    role_id: Optional[int] = None
    level: int = Field(default=1, ge=1)
    is_required: bool = True
    order: int = Field(default=0, ge=0)


class ApprovalChainApproverCreate(ApprovalChainApproverBase):
    pass


class ApprovalChainApproverUpdate(BaseModel):
    level: Optional[int] = Field(None, ge=1)
    is_required: Optional[bool] = None
    order: Optional[int] = Field(None, ge=0)


class ApprovalChainApproverResponse(ApprovalChainApproverBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Approval Request Schemas
class ApprovalRequestBase(BaseModel):
    workflow_instance_id: int
    approval_chain_id: int
    approver_id: int
    level: int = Field(default=1, ge=1)
    comments: Optional[str] = None


class ApprovalRequestCreate(ApprovalRequestBase):
    pass


class ApprovalRequestUpdate(BaseModel):
    status: Optional[ApprovalStatus] = None
    comments: Optional[str] = None
    delegated_to_id: Optional[int] = None


class ApprovalRequestResponse(ApprovalRequestBase):
    id: int
    delegated_to_id: Optional[int] = None
    status: ApprovalStatus
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    delegated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Action Schemas
class ApprovalActionRequest(BaseModel):
    """Request to approve or reject"""

    action: str = Field(..., pattern="^(approve|reject|delegate)$")
    comments: Optional[str] = None
    delegate_to_id: Optional[int] = None


class ApprovalChainWithApprovers(ApprovalChainResponse):
    """Approval chain with its approvers"""

    approvers: List[ApprovalChainApproverResponse] = []
