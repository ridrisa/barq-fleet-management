"""Live Chat Schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.models.support import ChatStatus


class ChatMessageBase(BaseModel):
    """Base chat message schema"""
    message: str = Field(..., min_length=1, description="Message content")


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating a chat message"""
    session_id: int = Field(..., description="Chat session ID")


class ChatMessageResponse(ChatMessageBase):
    """Schema for chat message response"""
    id: int
    session_id: int
    sender_id: int
    is_agent: bool
    is_system: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ChatMessageWithSender(ChatMessageResponse):
    """Extended chat message with sender info"""
    sender_name: str

    class Config:
        from_attributes = True


class ChatSessionBase(BaseModel):
    """Base chat session schema"""
    initial_message: Optional[str] = Field(None, max_length=500, description="Customer's initial message")


class ChatSessionCreate(ChatSessionBase):
    """Schema for creating a chat session"""
    pass


class ChatSessionUpdate(BaseModel):
    """Schema for updating a chat session"""
    status: Optional[ChatStatus] = None
    agent_id: Optional[int] = None


class ChatSessionAssign(BaseModel):
    """Schema for assigning chat to agent"""
    agent_id: int = Field(..., description="Agent user ID to assign")


class ChatSessionTransfer(BaseModel):
    """Schema for transferring chat to another agent"""
    new_agent_id: int = Field(..., description="New agent user ID")
    reason: Optional[str] = Field(None, description="Reason for transfer")


class ChatSessionResponse(ChatSessionBase):
    """Schema for chat session response"""
    id: int
    session_id: str
    customer_id: int
    agent_id: Optional[int] = None
    status: ChatStatus
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = Field(default=False, description="Whether chat is active")
    is_waiting: bool = Field(default=False, description="Whether chat is waiting for agent")

    class Config:
        from_attributes = True


class ChatSessionWithMessages(ChatSessionResponse):
    """Extended chat session with messages"""
    messages: List[ChatMessageWithSender] = []

    class Config:
        from_attributes = True


class ChatSessionList(BaseModel):
    """Minimal chat session schema for list views"""
    id: int
    session_id: str
    customer_id: int
    agent_id: Optional[int] = None
    status: ChatStatus
    created_at: datetime

    class Config:
        from_attributes = True


class ChatTranscript(BaseModel):
    """Chat transcript for download/export"""
    session_id: str
    customer_name: str
    agent_name: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    messages: List[ChatMessageWithSender]
    duration_minutes: Optional[int] = None
