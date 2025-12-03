"""Ticket Attachment Model"""
from sqlalchemy import Column, String, Integer, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class TicketAttachment(TenantMixin, BaseModel):
    """
    Ticket Attachment model - File attachments for tickets and replies
    Stores metadata about uploaded files
    """

    __tablename__ = "ticket_attachments"

    # Relationships
    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Parent ticket ID"
    )
    reply_id = Column(
        Integer,
        ForeignKey("ticket_replies.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Reply ID if attachment is on a reply"
    )
    uploaded_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        comment="User who uploaded the file"
    )

    # File Information
    filename = Column(
        String(255),
        nullable=False,
        comment="Original filename"
    )
    file_path = Column(
        String(500),
        nullable=False,
        comment="Storage path for the file"
    )
    file_type = Column(
        String(100),
        nullable=False,
        comment="MIME type of the file"
    )
    file_size = Column(
        BigInteger,
        nullable=False,
        comment="File size in bytes"
    )

    # Relationships
    ticket = relationship("Ticket", back_populates="attachments")
    reply = relationship("TicketReply", backref="attachments")
    uploader = relationship("User", foreign_keys=[uploaded_by])

    def __repr__(self):
        return f"<TicketAttachment {self.id}: {self.filename}>"

    @property
    def file_size_kb(self) -> float:
        """Get file size in KB"""
        return self.file_size / 1024

    @property
    def file_size_mb(self) -> float:
        """Get file size in MB"""
        return self.file_size / (1024 * 1024)
