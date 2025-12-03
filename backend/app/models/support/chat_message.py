"""Chat Message Model"""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class ChatMessage(TenantMixin, BaseModel):
    """
    Chat Message model - Individual messages in chat sessions
    Stores the conversation history
    """

    __tablename__ = "chat_messages"

    # Relationships
    session_id = Column(
        Integer,
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Chat session ID",
    )
    sender_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
        comment="User who sent the message",
    )

    # Content
    message = Column(Text, nullable=False, comment="Message content")

    # Message Type
    is_agent = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether message is from agent (True) or customer (False)",
    )
    is_system = Column(
        Boolean, default=False, nullable=False, comment="Whether message is a system message"
    )

    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])

    def __repr__(self):
        return f"<ChatMessage {self.id} in Session {self.session_id}>"
