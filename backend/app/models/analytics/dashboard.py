"""Dashboard Model - Custom dashboards for users"""
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class Dashboard(TenantMixin, BaseModel):
    """
    Custom dashboards with configurable widgets.
    Users can create personalized views of their data.
    """

    __tablename__ = "dashboards"

    # Dashboard metadata
    name = Column(String(255), nullable=False, comment="Dashboard name")
    description = Column(Text, nullable=True, comment="Dashboard description")

    # Widget configuration
    widgets = Column(JSONB, nullable=False, default=list, comment="Array of widget configurations")
    layout = Column(JSONB, nullable=True, comment="Dashboard layout configuration (grid positions, etc.)")

    # Ownership and sharing
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    is_default = Column(Boolean, default=False, nullable=False, comment="Is this the user's default dashboard?")
    is_shared = Column(Boolean, default=False, nullable=False, comment="Is dashboard shared with team?")

    # Configuration
    refresh_interval_seconds = Column(Integer, default=300, nullable=False, comment="Auto-refresh interval")
    filters = Column(JSONB, nullable=True, comment="Global dashboard filters")

    # Relationships
    user = relationship("User", backref="dashboards")

    # Indexes
    __table_args__ = (
        Index('idx_dashboard_user_default', 'user_id', 'is_default'),
        Index('idx_dashboard_shared', 'is_shared', 'created_at'),
    )

    def __repr__(self):
        return f"<Dashboard {self.name} (User: {self.user_id})>"
