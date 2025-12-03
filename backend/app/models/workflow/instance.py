import enum

from sqlalchemy import JSON, Column, Date, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class WorkflowStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WorkflowInstance(TenantMixin, BaseModel):
    __tablename__ = "workflow_instances"

    template_id = Column(Integer, ForeignKey("workflow_templates.id"), nullable=False)
    initiated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(
        Enum(WorkflowStatus, values_callable=lambda x: [e.value for e in x]),
        default=WorkflowStatus.DRAFT,
    )
    current_step = Column(Integer, default=0)
    data = Column(JSON)
    started_at = Column(Date)
    completed_at = Column(Date)
    notes = Column(Text)

    # Core relationships
    template = relationship("WorkflowTemplate", back_populates="instances")
    initiator = relationship("User")

    # Approval relationships
    approval_requests = relationship("ApprovalRequest", back_populates="workflow_instance")

    # SLA relationships
    sla_instances = relationship("WorkflowSLAInstance", back_populates="workflow_instance")

    # Collaboration relationships
    comments = relationship(
        "WorkflowComment", back_populates="workflow_instance", cascade="all, delete-orphan"
    )
    attachments = relationship(
        "WorkflowAttachment", back_populates="workflow_instance", cascade="all, delete-orphan"
    )

    # Audit trail relationships
    history = relationship(
        "WorkflowHistory",
        back_populates="workflow_instance",
        cascade="all, delete-orphan",
        order_by="WorkflowHistory.event_time",
    )

    # Notification relationships
    notifications = relationship(
        "WorkflowNotification", back_populates="workflow_instance", cascade="all, delete-orphan"
    )
