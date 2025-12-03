from sqlalchemy import JSON, Boolean, Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class WorkflowTemplateCategory(str):
    COURIER = "courier"
    VEHICLE = "vehicle"
    DELIVERY = "delivery"
    HR = "hr"
    FINANCE = "finance"
    GENERAL = "general"


class WorkflowTemplate(TenantMixin, BaseModel):
    __tablename__ = "workflow_templates"

    name = Column(String, nullable=False)
    description = Column(Text)
    steps = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    category = Column(String)
    estimated_duration = Column(Integer)
    version = Column(Integer, default=1)
    parent_template_id = Column(Integer)  # For versioning/cloning

    # Relationships
    instances = relationship("WorkflowInstance", back_populates="template")
    approval_chains = relationship("ApprovalChain", back_populates="workflow_template")
    slas = relationship("WorkflowSLA", back_populates="workflow_template")
    automations = relationship("WorkflowAutomation", back_populates="workflow_template")
    triggers = relationship("WorkflowTrigger", back_populates="workflow_template")
    metrics = relationship("WorkflowMetrics", back_populates="workflow_template")
