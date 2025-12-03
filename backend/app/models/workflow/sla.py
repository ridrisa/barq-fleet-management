import enum

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class SLAStatus(str, enum.Enum):
    ACTIVE = "active"
    WARNING = "warning"
    BREACHED = "breached"
    PAUSED = "paused"
    COMPLETED = "completed"


class SLAPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WorkflowSLA(TenantMixin, BaseModel):
    """SLA definitions for workflow templates"""

    __tablename__ = "workflow_slas"

    name = Column(String, nullable=False)
    description = Column(Text)
    workflow_template_id = Column(Integer, ForeignKey("workflow_templates.id"))
    priority = Column(Enum(SLAPriority), default=SLAPriority.MEDIUM)

    # Time thresholds in minutes
    response_time = Column(Integer)  # Time to first action
    resolution_time = Column(Integer, nullable=False)  # Time to complete
    warning_threshold = Column(Integer)  # Warning before breach (percentage)

    # Business hours calculation
    use_business_hours = Column(Boolean, default=False)
    business_hours_start = Column(String)  # e.g., "09:00"
    business_hours_end = Column(String)  # e.g., "17:00"
    business_days = Column(JSON)  # e.g., ["monday", "tuesday", ...]

    # Escalation
    escalate_on_warning = Column(Boolean, default=False)
    escalate_on_breach = Column(Boolean, default=True)
    escalation_chain = Column(JSON)  # Array of user IDs or role IDs

    is_active = Column(Boolean, default=True)

    # Relationships
    workflow_template = relationship("WorkflowTemplate", back_populates="slas")
    sla_instances = relationship("WorkflowSLAInstance", back_populates="sla")


class WorkflowSLAInstance(TenantMixin, BaseModel):
    """SLA tracking for individual workflow instances"""

    __tablename__ = "workflow_sla_instances"

    workflow_instance_id = Column(Integer, ForeignKey("workflow_instances.id"), nullable=False)
    sla_id = Column(Integer, ForeignKey("workflow_slas.id"), nullable=False)
    status = Column(Enum(SLAStatus), default=SLAStatus.ACTIVE)

    # Timestamps
    started_at = Column(DateTime, nullable=False)
    response_due_at = Column(DateTime)
    resolution_due_at = Column(DateTime, nullable=False)
    warning_at = Column(DateTime)
    first_response_at = Column(DateTime)
    resolved_at = Column(DateTime)
    breached_at = Column(DateTime)
    paused_at = Column(DateTime)

    # Metrics
    pause_duration = Column(Integer, default=0)  # Total pause time in minutes
    response_time_minutes = Column(Integer)
    resolution_time_minutes = Column(Integer)
    breach_time_minutes = Column(Integer)

    # Escalation tracking
    warning_sent = Column(Boolean, default=False)
    escalation_sent = Column(Boolean, default=False)
    escalation_level = Column(Integer, default=0)

    notes = Column(Text)

    # Relationships
    workflow_instance = relationship("WorkflowInstance", back_populates="sla_instances")
    sla = relationship("WorkflowSLA", back_populates="sla_instances")
    events = relationship("SLAEvent", back_populates="sla_instance", cascade="all, delete-orphan")


class SLAEvent(TenantMixin, BaseModel):
    """Event log for SLA tracking"""

    __tablename__ = "sla_events"

    sla_instance_id = Column(Integer, ForeignKey("workflow_sla_instances.id"), nullable=False)
    event_type = Column(
        String, nullable=False
    )  # started, warning, breached, paused, resumed, completed
    event_time = Column(DateTime, nullable=False)
    triggered_by_id = Column(Integer, ForeignKey("users.id"))
    details = Column(JSON)
    notes = Column(Text)

    # Relationships
    sla_instance = relationship("WorkflowSLAInstance", back_populates="events")
    triggered_by = relationship("User")
