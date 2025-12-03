import enum

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class TriggerType(str, enum.Enum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    SCHEDULED = "scheduled"
    EVENT_BASED = "event_based"
    API = "api"
    WEBHOOK = "webhook"


class TriggerEventType(str, enum.Enum):
    # Record events
    RECORD_CREATED = "record_created"
    RECORD_UPDATED = "record_updated"
    RECORD_DELETED = "record_deleted"

    # Workflow events
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"

    # Approval events
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_APPROVED = "approval_approved"
    APPROVAL_REJECTED = "approval_rejected"

    # SLA events
    SLA_WARNING = "sla_warning"
    SLA_BREACHED = "sla_breached"

    # Custom events
    CUSTOM = "custom"


class WorkflowTrigger(TenantMixin, BaseModel):
    """Trigger configuration for workflows"""

    __tablename__ = "workflow_triggers"

    name = Column(String, nullable=False)
    description = Column(Text)
    workflow_template_id = Column(Integer, ForeignKey("workflow_templates.id"), nullable=False)

    # Trigger type and configuration
    trigger_type = Column(Enum(TriggerType), nullable=False)
    event_type = Column(Enum(TriggerEventType))

    # Entity and field triggers
    entity_type = Column(String)  # e.g., "courier", "vehicle", "order"
    field_conditions = Column(JSON)  # Conditions on fields

    # Scheduled trigger settings
    schedule_cron = Column(String)
    schedule_timezone = Column(String, default="UTC")

    # Condition evaluation
    conditions = Column(JSON)  # Additional conditions to evaluate
    condition_logic = Column(String, default="AND")

    # Execution settings
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)

    # Deduplication
    deduplicate = Column(Boolean, default=False)
    deduplicate_key = Column(String)
    deduplicate_window = Column(Integer)  # Window in seconds

    # Rate limiting
    rate_limit = Column(Integer)  # Max executions per hour
    rate_limit_window = Column(Integer, default=3600)  # seconds

    # Webhook settings
    webhook_url = Column(String)
    webhook_secret = Column(String)

    # Timestamps
    last_triggered_at = Column(DateTime)
    next_trigger_at = Column(DateTime)

    # Relationships
    workflow_template = relationship("WorkflowTemplate", back_populates="triggers")
    trigger_executions = relationship(
        "TriggerExecution", back_populates="trigger", cascade="all, delete-orphan"
    )


class TriggerExecution(TenantMixin, BaseModel):
    """Log of trigger executions"""

    __tablename__ = "trigger_executions"

    trigger_id = Column(Integer, ForeignKey("workflow_triggers.id"), nullable=False)
    workflow_instance_id = Column(Integer, ForeignKey("workflow_instances.id"))

    triggered_at = Column(DateTime, nullable=False)
    trigger_data = Column(JSON)  # Data that caused the trigger

    status = Column(String, nullable=False)  # success, failed, skipped, rate_limited
    workflow_created = Column(Boolean, default=False)
    error_message = Column(Text)

    execution_time_ms = Column(Integer)

    # Relationships
    trigger = relationship("WorkflowTrigger", back_populates="trigger_executions")
    workflow_instance = relationship("WorkflowInstance")
