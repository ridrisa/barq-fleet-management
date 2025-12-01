from sqlalchemy import Column, String, Integer, Date, ForeignKey, Enum, JSON, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class WorkflowStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class WorkflowInstance(BaseModel):
    __tablename__ = "workflow_instances"

    template_id = Column(Integer, ForeignKey("workflow_templates.id"), nullable=False)
    initiated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(WorkflowStatus, values_callable=lambda x: [e.value for e in x]), default=WorkflowStatus.DRAFT)
    current_step = Column(Integer, default=0)
    data = Column(JSON)
    started_at = Column(Date)
    completed_at = Column(Date)
    notes = Column(Text)

    template = relationship("WorkflowTemplate", back_populates="instances")
    initiator = relationship("User")
    approval_requests = relationship("ApprovalRequest", back_populates="workflow_instance")
    sla_instances = relationship("WorkflowSLAInstance", back_populates="workflow_instance")
