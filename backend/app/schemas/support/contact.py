"""Contact Support Schemas"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class ContactFormSubmit(BaseModel):
    """Schema for contact form submission"""

    name: str = Field(..., min_length=2, max_length=100, description="Contact name")
    email: str = Field(..., max_length=255, description="Contact email")
    phone: Optional[str] = Field(None, max_length=50, description="Contact phone")
    subject: str = Field(..., min_length=5, max_length=255, description="Subject")
    message: str = Field(..., min_length=10, description="Message content")
    department: Optional[str] = Field(None, max_length=100, description="Department to route to")
    preferred_contact_method: str = Field(
        default="email", description="Preferred contact method: email, phone"
    )
    urgency: str = Field(default="normal", description="Urgency level: normal, high, critical")


class ContactFormResponse(BaseModel):
    """Schema for contact form submission response"""

    success: bool = True
    message: str = "Your message has been received. We will get back to you shortly."
    ticket_id: Optional[str] = Field(None, description="Auto-created ticket ID if applicable")
    reference_number: str = Field(..., description="Reference number for tracking")
    estimated_response_time: str = Field(default="24 hours", description="Estimated response time")


class ContactPreferences(BaseModel):
    """Schema for contact preferences"""

    email_notifications: bool = True
    sms_notifications: bool = False
    preferred_language: str = Field(default="en", description="Preferred language code")
    timezone: str = Field(default="UTC", description="Preferred timezone")


class DepartmentInfo(BaseModel):
    """Schema for department contact information"""

    name: str
    email: str
    phone: Optional[str] = None
    hours: Optional[str] = Field(None, description="Operating hours")
    description: Optional[str] = None
    average_response_time: str = Field(default="24 hours", description="Average response time")
