"""Live Chat Session Model"""
from sqlalchemy import Column, String, Integer, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.mixins import TenantMixin
import enum


class ChatStatus(str, enum.Enum):
    """Chat session status"""
    WAITING = "waiting"
    ACTIVE = "active"
    ENDED = "ended"
    TRANSFERRED = "transferred"


class ChatSession(TenantMixin, BaseModel):
    """
    Chat Session model - Live chat conversations
    Enables real-time support communication
    """

    __tablename__ = "chat_sessions"

    # Session Identification
    session_id = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique session identifier"
    )

    # Participants
    customer_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Customer user ID"
    )
    agent_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Support agent user ID"
    )

    # Status
    status = Column(
        SQLEnum(ChatStatus),
        default=ChatStatus.WAITING,
        nullable=False,
        index=True,
        comment="Current session status"
    )

    # Timestamps
    started_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When agent joined the chat"
    )
    ended_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When chat session ended"
    )

    # Metadata
    initial_message = Column(
        String(500),
        nullable=True,
        comment="Customer's initial message"
    )

    # Relationships
    customer = relationship("User", foreign_keys=[customer_id], backref="customer_chats")
    agent = relationship("User", foreign_keys=[agent_id], backref="agent_chats")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatSession {self.session_id}: {self.status.value}>"

    @property
    def is_active(self) -> bool:
        """Check if chat is active"""
        return self.status == ChatStatus.ACTIVE

    @property
    def is_waiting(self) -> bool:
        """Check if chat is waiting for agent"""
        return self.status == ChatStatus.WAITING
