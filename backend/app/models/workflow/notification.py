import enum

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class NotificationType(str, enum.Enum):
    """Types of workflow notifications"""

    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    APPROVAL_REQUIRED = "approval_required"
    APPROVAL_APPROVED = "approval_approved"
    APPROVAL_REJECTED = "approval_rejected"
    APPROVAL_DELEGATED = "approval_delegated"
    TASK_ASSIGNED = "task_assigned"
    SLA_WARNING = "sla_warning"
    SLA_BREACHED = "sla_breached"
    COMMENT_MENTIONED = "comment_mentioned"
    COMMENT_REPLIED = "comment_replied"
    STATUS_CHANGED = "status_changed"
    ESCALATED = "escalated"
    CUSTOM = "custom"


class NotificationChannel(str, enum.Enum):
    """Channels for sending notifications"""

    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"


class NotificationStatus(str, enum.Enum):
    """Status of notification delivery"""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowNotificationTemplate(TenantMixin, BaseModel):
    """Templates for workflow notifications"""

    __tablename__ = "workflow_notification_templates"

    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    notification_type = Column(
        Enum(NotificationType, values_callable=lambda x: [e.value for e in x]), nullable=False
    )

    # Template content
    subject_template = Column(String)  # For email/push
    body_template = Column(Text, nullable=False)  # Supports template variables
    sms_template = Column(String)  # Short version for SMS

    # Channels
    channels = Column(JSON)  # Array of channels: ["email", "in_app", "sms"]

    # Settings
    priority = Column(String, default="normal")  # low, normal, high, urgent
    is_active = Column(Boolean, default=True)
    send_immediately = Column(Boolean, default=True)
    batch_delay_minutes = Column(Integer, default=0)

    # Variables that can be used in template
    available_variables = Column(JSON)  # e.g., ["workflow_name", "initiator_name", ...]

    # Relationships
    notifications = relationship("WorkflowNotification", back_populates="template")


class WorkflowNotification(TenantMixin, BaseModel):
    """Individual notification instances"""

    __tablename__ = "workflow_notifications"

    workflow_instance_id = Column(Integer, ForeignKey("workflow_instances.id"))
    template_id = Column(Integer, ForeignKey("workflow_notification_templates.id"))
    notification_type = Column(
        Enum(NotificationType, values_callable=lambda x: [e.value for e in x]), nullable=False
    )

    # Recipient
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_email = Column(String)
    recipient_phone = Column(String)

    # Content
    subject = Column(String)
    body = Column(Text, nullable=False)
    sms_content = Column(String)

    # Channel and delivery
    channel = Column(
        Enum(NotificationChannel, values_callable=lambda x: [e.value for e in x]), nullable=False
    )
    status = Column(
        Enum(NotificationStatus, values_callable=lambda x: [e.value for e in x]),
        default=NotificationStatus.PENDING,
    )
    priority = Column(String, default="normal")

    # Timing
    scheduled_at = Column(DateTime)
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    read_at = Column(DateTime)
    expires_at = Column(DateTime)

    # Delivery tracking
    delivery_attempts = Column(Integer, default=0)
    last_attempt_at = Column(DateTime)
    error_message = Column(Text)

    # Interaction tracking
    clicked_at = Column(DateTime)
    action_taken = Column(String)  # e.g., "approved", "rejected", "viewed"

    # Additional data
    notification_metadata = Column(JSON)

    # Relationships
    workflow_instance = relationship("WorkflowInstance", back_populates="notifications")
    template = relationship("WorkflowNotificationTemplate", back_populates="notifications")
    recipient = relationship("User")


class NotificationPreference(TenantMixin, BaseModel):
    """User preferences for workflow notifications"""

    __tablename__ = "workflow_notification_preferences"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    notification_type = Column(
        Enum(NotificationType, values_callable=lambda x: [e.value for e in x]), nullable=False
    )

    # Channel preferences
    enable_email = Column(Boolean, default=True)
    enable_in_app = Column(Boolean, default=True)
    enable_sms = Column(Boolean, default=False)
    enable_push = Column(Boolean, default=True)

    # Timing preferences
    do_not_disturb_start = Column(String)  # e.g., "22:00"
    do_not_disturb_end = Column(String)  # e.g., "08:00"
    batch_notifications = Column(Boolean, default=False)
    batch_interval_minutes = Column(Integer, default=60)

    # Frequency control
    max_notifications_per_day = Column(Integer)
    digest_mode = Column(Boolean, default=False)  # Daily/weekly digest instead of immediate

    # Relationships
    user = relationship("User")
