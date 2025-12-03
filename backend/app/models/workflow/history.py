from sqlalchemy import Column, String, Integer, ForeignKey, Text, JSON, DateTime, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.mixins import TenantMixin
import enum


class WorkflowHistoryEventType(str, enum.Enum):
    """Types of workflow history events"""
    CREATED = "created"
    STARTED = "started"
    STEP_COMPLETED = "step_completed"
    STATUS_CHANGED = "status_changed"
    ASSIGNED = "assigned"
    APPROVED = "approved"
    REJECTED = "rejected"
    DELEGATED = "delegated"
    COMMENT_ADDED = "comment_added"
    ATTACHMENT_ADDED = "attachment_added"
    ATTACHMENT_REMOVED = "attachment_removed"
    DATA_UPDATED = "data_updated"
    SLA_WARNING = "sla_warning"
    SLA_BREACHED = "sla_breached"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    CUSTOM = "custom"


class WorkflowHistory(TenantMixin, BaseModel):
    """Complete audit trail for workflow instances - tamper-evident"""
    __tablename__ = "workflow_history"

    workflow_instance_id = Column(Integer, ForeignKey("workflow_instances.id"), nullable=False, index=True)
    event_type = Column(Enum(WorkflowHistoryEventType, values_callable=lambda x: [e.value for e in x]), nullable=False)

    # Actor information
    actor_id = Column(Integer, ForeignKey("users.id"))
    actor_type = Column(String, default="user")  # user, system, automation

    # Event details
    event_time = Column(DateTime, nullable=False, index=True)
    description = Column(Text, nullable=False)

    # State tracking
    previous_state = Column(JSON)  # Previous state snapshot
    new_state = Column(JSON)  # New state snapshot
    field_changes = Column(JSON)  # Specific field changes

    # Additional context
    event_metadata = Column(JSON)  # Additional event metadata
    ip_address = Column(String)  # For security audit
    user_agent = Column(String)  # Browser/client info

    # Tamper detection
    checksum = Column(String)  # SHA-256 checksum of event data
    previous_checksum = Column(String)  # Checksum of previous event (blockchain-like)

    # Relationships
    workflow_instance = relationship("WorkflowInstance", back_populates="history")
    actor = relationship("User", foreign_keys=[actor_id])


class WorkflowStepHistory(TenantMixin, BaseModel):
    """Detailed history for individual workflow steps"""
    __tablename__ = "workflow_step_history"

    workflow_instance_id = Column(Integer, ForeignKey("workflow_instances.id"), nullable=False)
    step_index = Column(Integer, nullable=False)
    step_name = Column(String, nullable=False)

    # Execution details
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    executed_by_id = Column(Integer, ForeignKey("users.id"))

    # Status
    status = Column(String, nullable=False)  # started, completed, failed, skipped
    result = Column(String)  # success, failure, skipped

    # Data
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)

    # Timing
    duration_seconds = Column(Integer)
    wait_time_seconds = Column(Integer)  # Time waiting from previous step

    # Relationships
    workflow_instance = relationship("WorkflowInstance")
    executed_by = relationship("User")
