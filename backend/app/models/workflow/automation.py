import enum

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class AutomationTriggerType(str, enum.Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT = "event"
    CONDITION = "condition"
    WEBHOOK = "webhook"


class AutomationActionType(str, enum.Enum):
    CREATE_WORKFLOW = "create_workflow"
    UPDATE_WORKFLOW = "update_workflow"
    SEND_NOTIFICATION = "send_notification"
    SEND_EMAIL = "send_email"
    SEND_SMS = "send_sms"
    UPDATE_RECORD = "update_record"
    WEBHOOK_CALL = "webhook_call"
    CUSTOM_SCRIPT = "custom_script"


class AutomationStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    ERROR = "error"


class WorkflowAutomation(TenantMixin, BaseModel):
    """Automation rules for workflows"""

    __tablename__ = "workflow_automations"

    name = Column(String, nullable=False)
    description = Column(Text)
    workflow_template_id = Column(Integer, ForeignKey("workflow_templates.id"))

    # Trigger configuration
    trigger_type = Column(Enum(AutomationTriggerType), nullable=False)
    trigger_config = Column(JSON)  # Configuration for trigger (schedule, event, condition)

    # Condition evaluation
    conditions = Column(JSON)  # Array of conditions to check
    condition_logic = Column(String, default="AND")  # AND/OR logic for multiple conditions

    # Action configuration
    action_type = Column(Enum(AutomationActionType), nullable=False)
    action_config = Column(JSON)  # Configuration for action

    # Execution settings
    is_active = Column(Boolean, default=True)
    run_order = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    retry_delay = Column(Integer, default=60)  # seconds
    timeout = Column(Integer, default=300)  # seconds

    # Schedule settings (for scheduled triggers)
    schedule_cron = Column(String)  # Cron expression
    schedule_timezone = Column(String, default="UTC")
    last_run_at = Column(DateTime)
    next_run_at = Column(DateTime)

    status = Column(Enum(AutomationStatus), default=AutomationStatus.ACTIVE)

    # Relationships
    workflow_template = relationship("WorkflowTemplate", back_populates="automations")
    execution_logs = relationship(
        "AutomationExecutionLog", back_populates="automation", cascade="all, delete-orphan"
    )


class AutomationExecutionLog(TenantMixin, BaseModel):
    """Log of automation executions"""

    __tablename__ = "automation_execution_logs"

    automation_id = Column(Integer, ForeignKey("workflow_automations.id"), nullable=False)
    workflow_instance_id = Column(Integer, ForeignKey("workflow_instances.id"))

    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)

    status = Column(String, nullable=False)  # success, failed, timeout, skipped
    trigger_data = Column(JSON)  # Data that triggered the automation
    action_result = Column(JSON)  # Result of the action
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)

    execution_time_ms = Column(Integer)

    # Relationships
    automation = relationship("WorkflowAutomation", back_populates="execution_logs")
    workflow_instance = relationship("WorkflowInstance")
