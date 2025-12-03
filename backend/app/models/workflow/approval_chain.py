import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DELEGATED = "delegated"
    EXPIRED = "expired"


class ApprovalChain(TenantMixin, BaseModel):
    """Approval chain template for workflows"""

    __tablename__ = "approval_chains"

    name = Column(String, nullable=False)
    description = Column(Text)
    workflow_template_id = Column(Integer, ForeignKey("workflow_templates.id"))
    levels = Column(Integer, nullable=False, default=1)  # Number of approval levels
    is_sequential = Column(Boolean, default=True)  # Sequential or parallel approvals
    allow_delegation = Column(Boolean, default=False)
    auto_escalate = Column(Boolean, default=True)
    escalation_hours = Column(Integer, default=24)
    is_active = Column(Boolean, default=True)

    # Relationships
    workflow_template = relationship("WorkflowTemplate", back_populates="approval_chains")
    approvers = relationship(
        "ApprovalChainApprover", back_populates="approval_chain", cascade="all, delete-orphan"
    )
    approval_requests = relationship("ApprovalRequest", back_populates="approval_chain")


class ApprovalChainApprover(TenantMixin, BaseModel):
    """Approvers in an approval chain with level hierarchy"""

    __tablename__ = "approval_chain_approvers"

    approval_chain_id = Column(Integer, ForeignKey("approval_chains.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"))  # Optionally approve by role
    level = Column(Integer, nullable=False, default=1)
    is_required = Column(Boolean, default=True)
    order = Column(Integer, default=0)

    # Relationships
    approval_chain = relationship("ApprovalChain", back_populates="approvers")
    user = relationship("User")
    role = relationship("Role")


class ApprovalRequest(TenantMixin, BaseModel):
    """Individual approval requests for workflow instances"""

    __tablename__ = "approval_requests"

    workflow_instance_id = Column(Integer, ForeignKey("workflow_instances.id"), nullable=False)
    approval_chain_id = Column(Integer, ForeignKey("approval_chains.id"), nullable=False)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    delegated_to_id = Column(Integer, ForeignKey("users.id"))
    level = Column(Integer, nullable=False, default=1)
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    comments = Column(Text)
    approved_at = Column(DateTime)
    rejected_at = Column(DateTime)
    delegated_at = Column(DateTime)
    expires_at = Column(DateTime)

    # Relationships
    workflow_instance = relationship("WorkflowInstance", back_populates="approval_requests")
    approval_chain = relationship("ApprovalChain", back_populates="approval_requests")
    approver = relationship("User", foreign_keys=[approver_id])
    delegated_to = relationship("User", foreign_keys=[delegated_to_id])
