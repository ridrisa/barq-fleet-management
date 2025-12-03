"""Ticket Reply Schemas"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TicketReplyBase(BaseModel):
    """Base ticket reply schema"""

    message: str = Field(..., min_length=1, description="Reply message content")
    is_internal: bool = Field(default=False, description="Whether this is an internal note")


class TicketReplyCreate(TicketReplyBase):
    """Schema for creating a new ticket reply"""

    ticket_id: int = Field(..., description="Ticket ID this reply belongs to")


class TicketReplyUpdate(BaseModel):
    """Schema for updating a ticket reply"""

    message: Optional[str] = Field(None, min_length=1)
    is_internal: Optional[bool] = None


class TicketReplyResponse(TicketReplyBase):
    """Schema for ticket reply response"""

    id: int
    ticket_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TicketReplyWithUser(TicketReplyResponse):
    """Extended ticket reply with user information"""

    user_name: str
    user_email: Optional[str] = None

    class Config:
        from_attributes = True
