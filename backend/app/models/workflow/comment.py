from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class WorkflowComment(TenantMixin, BaseModel):
    """Comments on workflow instances for collaboration and communication"""

    __tablename__ = "workflow_comments"

    workflow_instance_id = Column(Integer, ForeignKey("workflow_instances.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_comment_id = Column(Integer, ForeignKey("workflow_comments.id"))  # For threaded comments

    comment = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # Internal vs external comments
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime)

    # Relationships
    workflow_instance = relationship("WorkflowInstance", back_populates="comments")
    user = relationship("User")
    parent_comment = relationship(
        "WorkflowComment", remote_side="WorkflowComment.id", back_populates="replies"
    )
    replies = relationship(
        "WorkflowComment", back_populates="parent_comment", cascade="all, delete-orphan"
    )
