from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.workflow.notification import (
    NotificationType,
    NotificationChannel,
    NotificationStatus,
)


# ============================================================================
# Notification Template Schemas
# ============================================================================

class WorkflowNotificationTemplateBase(BaseModel):
    """Base schema for notification templates"""
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    notification_type: NotificationType
    subject_template: Optional[str] = Field(None, max_length=200)
    body_template: str = Field(..., min_length=1)
    sms_template: Optional[str] = Field(None, max_length=160)
    channels: List[str] = ["email", "in_app"]
    priority: str = "normal"
    is_active: bool = True
    send_immediately: bool = True
    batch_delay_minutes: int = 0
    available_variables: Optional[List[str]] = []


class WorkflowNotificationTemplateCreate(WorkflowNotificationTemplateBase):
    """Schema for creating a notification template"""
    pass


class WorkflowNotificationTemplateUpdate(BaseModel):
    """Schema for updating a notification template"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    subject_template: Optional[str] = Field(None, max_length=200)
    body_template: Optional[str] = Field(None, min_length=1)
    sms_template: Optional[str] = Field(None, max_length=160)
    channels: Optional[List[str]] = None
    priority: Optional[str] = None
    is_active: Optional[bool] = None
    send_immediately: Optional[bool] = None
    batch_delay_minutes: Optional[int] = None


class WorkflowNotificationTemplateResponse(WorkflowNotificationTemplateBase):
    """Schema for notification template response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Notification Schemas
# ============================================================================

class WorkflowNotificationBase(BaseModel):
    """Base schema for notifications"""
    notification_type: NotificationType
    subject: Optional[str] = Field(None, max_length=200)
    body: str = Field(..., min_length=1)
    sms_content: Optional[str] = Field(None, max_length=160)
    channel: NotificationChannel
    priority: str = "normal"
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class WorkflowNotificationCreate(WorkflowNotificationBase):
    """Schema for creating a notification"""
    workflow_instance_id: Optional[int] = None
    template_id: Optional[int] = None
    recipient_id: int
    recipient_email: Optional[EmailStr] = None
    recipient_phone: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class WorkflowNotificationUpdate(BaseModel):
    """Schema for updating a notification"""
    status: Optional[NotificationStatus] = None
    read_at: Optional[datetime] = None
    action_taken: Optional[str] = None


class WorkflowNotificationResponse(WorkflowNotificationBase):
    """Schema for notification response"""
    id: int
    workflow_instance_id: Optional[int] = None
    template_id: Optional[int] = None
    recipient_id: int
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    status: NotificationStatus
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    delivery_attempts: int
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class WorkflowNotificationWithRecipient(WorkflowNotificationResponse):
    """Extended schema with recipient details"""
    recipient_name: Optional[str] = None


class BulkNotificationRequest(BaseModel):
    """Schema for sending bulk notifications"""
    template_id: int
    recipient_ids: List[int]
    workflow_instance_id: Optional[int] = None
    variables: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[datetime] = None


# ============================================================================
# Notification Preference Schemas
# ============================================================================

class NotificationPreferenceBase(BaseModel):
    """Base schema for notification preferences"""
    notification_type: NotificationType
    enable_email: bool = True
    enable_in_app: bool = True
    enable_sms: bool = False
    enable_push: bool = True
    do_not_disturb_start: Optional[str] = None
    do_not_disturb_end: Optional[str] = None
    batch_notifications: bool = False
    batch_interval_minutes: int = 60
    max_notifications_per_day: Optional[int] = None
    digest_mode: bool = False


class NotificationPreferenceCreate(NotificationPreferenceBase):
    """Schema for creating notification preference"""
    user_id: int


class NotificationPreferenceUpdate(BaseModel):
    """Schema for updating notification preference"""
    enable_email: Optional[bool] = None
    enable_in_app: Optional[bool] = None
    enable_sms: Optional[bool] = None
    enable_push: Optional[bool] = None
    do_not_disturb_start: Optional[str] = None
    do_not_disturb_end: Optional[str] = None
    batch_notifications: Optional[bool] = None
    batch_interval_minutes: Optional[int] = None
    max_notifications_per_day: Optional[int] = None
    digest_mode: Optional[bool] = None


class NotificationPreferenceResponse(NotificationPreferenceBase):
    """Schema for notification preference response"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Notification Statistics
# ============================================================================

class NotificationStatistics(BaseModel):
    """Schema for notification statistics"""
    total_notifications: int
    sent_count: int
    delivered_count: int
    read_count: int
    failed_count: int
    pending_count: int
    delivery_rate: float
    read_rate: float
    average_delivery_time_seconds: Optional[float] = None
    average_read_time_seconds: Optional[float] = None


class NotificationSendRequest(BaseModel):
    """Schema for sending a single notification"""
    template_id: int
    recipient_id: int
    workflow_instance_id: Optional[int] = None
    variables: Optional[Dict[str, Any]] = None
    channel: Optional[NotificationChannel] = None
    scheduled_at: Optional[datetime] = None
