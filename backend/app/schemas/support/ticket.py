"""Support Ticket Schemas"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

# Import enums from model
from app.models.support import TicketCategory, TicketPriority, TicketStatus


class TicketBase(BaseModel):
    """Base ticket schema with common fields"""
    subject: str = Field(..., min_length=5, max_length=255, description="Ticket subject/title")
    description: str = Field(..., min_length=10, description="Detailed description of the issue")
    category: TicketCategory = Field(..., description="Ticket category")
    priority: TicketPriority = Field(default=TicketPriority.MEDIUM, description="Ticket priority level")
    courier_id: Optional[int] = Field(None, description="Related courier ID (if applicable)")


class TicketCreate(TicketBase):
    """Schema for creating a new ticket"""
    pass


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


class TicketAssign(BaseModel):
    """Schema for assigning a ticket to a user"""
    assigned_to: int = Field(..., description="User ID to assign the ticket to")


class TicketResolve(BaseModel):
    """Schema for resolving a ticket"""
    resolution: str = Field(..., min_length=10, description="Resolution details")


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

    # Computed properties
    is_open: bool = Field(default=False, description="Whether ticket is open/in-progress/pending")
    is_resolved: bool = Field(default=False, description="Whether ticket is resolved")
    is_closed: bool = Field(default=False, description="Whether ticket is closed")
    is_high_priority: bool = Field(default=False, description="Whether ticket is high priority or urgent")

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

    class Config:
        from_attributes = True


class TicketStatistics(BaseModel):
    """Ticket statistics schema"""
    total: int = 0
    open: int = 0
    in_progress: int = 0
    pending: int = 0
    resolved: int = 0
    closed: int = 0
    by_category: dict = Field(default_factory=dict)
    by_priority: dict = Field(default_factory=dict)
    avg_resolution_time_hours: float = 0.0


class TicketWithRelations(TicketResponse):
    """Extended ticket response with related objects"""
    courier_name: Optional[str] = None
    creator_name: str
    assignee_name: Optional[str] = None

    class Config:
        from_attributes = True
