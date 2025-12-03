"""Support Ticket Schemas"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

# Import enums from model
from app.models.support import EscalationLevel, TicketCategory, TicketPriority, TicketStatus


class TicketBase(BaseModel):
    """Base ticket schema with common fields"""

    subject: str = Field(..., min_length=5, max_length=255, description="Ticket subject/title")
    description: str = Field(..., min_length=10, description="Detailed description of the issue")
    category: TicketCategory = Field(..., description="Ticket category")
    priority: TicketPriority = Field(
        default=TicketPriority.MEDIUM, description="Ticket priority level"
    )
    courier_id: Optional[int] = Field(None, description="Related courier ID (if applicable)")
    tags: Optional[str] = Field(None, description="Comma-separated tags")
    contact_email: Optional[str] = Field(None, max_length=255, description="Contact email")
    contact_phone: Optional[str] = Field(None, max_length=50, description="Contact phone")
    department: Optional[str] = Field(None, max_length=100, description="Department for routing")
    custom_fields: Optional[Dict[str, Any]] = Field(None, description="Custom fields")


class TicketCreate(TicketBase):
    """Schema for creating a new ticket"""

    template_id: Optional[int] = Field(None, description="Template to use for creation")


class TicketCreateFromTemplate(BaseModel):
    """Schema for creating a ticket from a template"""

    template_id: int = Field(..., description="Template ID")
    subject: Optional[str] = Field(None, description="Override subject")
    description: Optional[str] = Field(None, description="Override description")
    courier_id: Optional[int] = Field(None, description="Related courier ID")
    custom_fields: Optional[Dict[str, Any]] = Field(None, description="Override custom fields")


class TicketUpdate(BaseModel):
    """Schema for updating a ticket - all fields optional"""

    subject: Optional[str] = Field(None, min_length=5, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[TicketCategory] = None
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None
    courier_id: Optional[int] = None
    assigned_to: Optional[int] = None
    resolution: Optional[str] = None
    tags: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    department: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


class TicketAssign(BaseModel):
    """Schema for assigning a ticket to a user"""

    assigned_to: int = Field(..., description="User ID to assign the ticket to")


class TicketResolve(BaseModel):
    """Schema for resolving a ticket"""

    resolution: str = Field(..., min_length=10, description="Resolution details")


class TicketEscalate(BaseModel):
    """Schema for escalating a ticket"""

    escalation_level: EscalationLevel = Field(..., description="New escalation level")
    reason: str = Field(..., min_length=10, description="Reason for escalation")
    assign_to: Optional[int] = Field(None, description="User to assign the escalated ticket to")


class TicketMerge(BaseModel):
    """Schema for merging tickets"""

    source_ticket_ids: List[int] = Field(
        ..., min_length=1, description="Ticket IDs to merge into target"
    )
    target_ticket_id: int = Field(..., description="Target ticket ID to merge into")
    merge_note: Optional[str] = Field(None, description="Note to add about the merge")


class TicketBulkAction(BaseModel):
    """Schema for bulk ticket operations"""

    ticket_ids: List[int] = Field(..., min_length=1, description="List of ticket IDs")
    action: str = Field(
        ..., description="Action to perform: assign, change_status, change_priority, close, delete"
    )
    assigned_to: Optional[int] = Field(None, description="User ID for assign action")
    status: Optional[TicketStatus] = Field(None, description="New status for change_status action")
    priority: Optional[TicketPriority] = Field(
        None, description="New priority for change_priority action"
    )


class TicketSLAConfig(BaseModel):
    """Schema for setting SLA on a ticket"""

    sla_hours: int = Field(..., ge=1, description="SLA deadline in hours from now")


class TicketResponse(TicketBase):
    """Schema for ticket response with database fields"""

    id: int
    ticket_id: str
    created_by: int
    assigned_to: Optional[int] = None
    status: TicketStatus
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # SLA fields
    sla_due_at: Optional[datetime] = None
    first_response_at: Optional[datetime] = None
    sla_breached: bool = False

    # Escalation fields
    escalation_level: EscalationLevel = EscalationLevel.NONE
    escalated_at: Optional[datetime] = None
    escalated_by: Optional[int] = None
    escalation_reason: Optional[str] = None

    # Merge fields
    merged_into_id: Optional[int] = None
    is_merged: bool = False
    template_id: Optional[int] = None

    # Computed properties
    is_open: bool = Field(default=False, description="Whether ticket is open/in-progress/waiting")
    is_resolved: bool = Field(default=False, description="Whether ticket is resolved")
    is_closed: bool = Field(default=False, description="Whether ticket is closed")
    is_high_priority: bool = Field(
        default=False, description="Whether ticket is high priority or urgent"
    )
    is_escalated: bool = Field(default=False, description="Whether ticket is escalated")
    sla_status: str = Field(default="not_set", description="SLA status: active, breached, not_set")

    class Config:
        from_attributes = True


class TicketList(BaseModel):
    """Minimal ticket schema for list views"""

    id: int
    ticket_id: str
    subject: str
    category: TicketCategory
    priority: TicketPriority
    status: TicketStatus
    courier_id: Optional[int] = None
    created_by: int
    assigned_to: Optional[int] = None
    created_at: datetime
    sla_due_at: Optional[datetime] = None
    sla_breached: bool = False
    escalation_level: EscalationLevel = EscalationLevel.NONE
    is_merged: bool = False

    class Config:
        from_attributes = True


class TicketStatistics(BaseModel):
    """Ticket statistics schema"""

    total: int = 0
    open: int = 0
    in_progress: int = 0
    waiting: int = 0
    resolved: int = 0
    closed: int = 0
    by_category: dict = Field(default_factory=dict)
    by_priority: dict = Field(default_factory=dict)
    by_escalation: dict = Field(default_factory=dict)
    avg_resolution_time_hours: float = 0.0
    avg_first_response_minutes: float = 0.0
    sla_compliance_rate: float = 0.0
    escalated_count: int = 0
    merged_count: int = 0


class TicketWithRelations(TicketResponse):
    """Extended ticket response with related objects"""

    courier_name: Optional[str] = None
    creator_name: str
    assignee_name: Optional[str] = None
    escalator_name: Optional[str] = None
    merged_tickets_count: int = 0
    reply_count: int = 0
    attachment_count: int = 0

    class Config:
        from_attributes = True


class TicketAttachmentCreate(BaseModel):
    """Schema for creating ticket attachment"""

    ticket_id: int = Field(..., description="Parent ticket ID")
    reply_id: Optional[int] = Field(None, description="Reply ID if attachment is on a reply")
    filename: str = Field(..., max_length=255, description="Original filename")
    file_path: str = Field(..., max_length=500, description="Storage path")
    file_type: str = Field(..., max_length=100, description="MIME type")
    file_size: int = Field(..., ge=0, description="File size in bytes")


class TicketAttachmentResponse(BaseModel):
    """Schema for ticket attachment response"""

    id: int
    ticket_id: int
    reply_id: Optional[int] = None
    uploaded_by: int
    filename: str
    file_path: str
    file_type: str
    file_size: int
    file_size_kb: float
    file_size_mb: float
    created_at: datetime

    class Config:
        from_attributes = True


class TicketTemplateCreate(BaseModel):
    """Schema for creating ticket template"""

    name: str = Field(..., min_length=3, max_length=100, description="Template name")
    description: Optional[str] = Field(None, max_length=500, description="Template description")
    default_subject: Optional[str] = Field(None, max_length=255, description="Default subject")
    default_description: Optional[str] = Field(None, description="Default description")
    default_category: Optional[TicketCategory] = None
    default_priority: Optional[TicketPriority] = TicketPriority.MEDIUM
    default_department: Optional[str] = Field(
        None, max_length=100, description="Default department"
    )
    default_tags: Optional[str] = Field(None, description="Default tags")
    default_custom_fields: Optional[Dict[str, Any]] = None
    sla_hours: Optional[int] = Field(None, ge=1, description="SLA in hours")
    is_active: bool = True
    is_public: bool = True


class TicketTemplateUpdate(BaseModel):
    """Schema for updating ticket template"""

    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    default_subject: Optional[str] = Field(None, max_length=255)
    default_description: Optional[str] = None
    default_category: Optional[TicketCategory] = None
    default_priority: Optional[TicketPriority] = None
    default_department: Optional[str] = None
    default_tags: Optional[str] = None
    default_custom_fields: Optional[Dict[str, Any]] = None
    sla_hours: Optional[int] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None


class TicketTemplateResponse(BaseModel):
    """Schema for ticket template response"""

    id: int
    name: str
    description: Optional[str] = None
    default_subject: Optional[str] = None
    default_description: Optional[str] = None
    default_category: Optional[TicketCategory] = None
    default_priority: Optional[TicketPriority] = None
    default_department: Optional[str] = None
    default_tags: Optional[str] = None
    default_custom_fields: Optional[Dict[str, Any]] = None
    sla_hours: Optional[int] = None
    is_active: bool
    is_public: bool
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CannedResponseCreate(BaseModel):
    """Schema for creating canned response"""

    title: str = Field(..., min_length=3, max_length=100, description="Response title")
    shortcut: Optional[str] = Field(None, max_length=50, description="Keyboard shortcut")
    content: str = Field(..., min_length=5, description="Response content")
    category: str = Field(..., min_length=1, max_length=100, description="Response category")
    is_active: bool = True
    is_public: bool = True


class CannedResponseUpdate(BaseModel):
    """Schema for updating canned response"""

    title: Optional[str] = Field(None, min_length=3, max_length=100)
    shortcut: Optional[str] = Field(None, max_length=50)
    content: Optional[str] = Field(None, min_length=5)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None


class CannedResponseResponse(BaseModel):
    """Schema for canned response response"""

    id: int
    title: str
    shortcut: Optional[str] = None
    content: str
    category: str
    is_active: bool
    is_public: bool
    usage_count: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
