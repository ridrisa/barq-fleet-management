"""Organization User model for multi-tenant support"""

import enum
from sqlalchemy import Column, Integer, ForeignKey, Enum, Boolean, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class OrganizationRole(enum.Enum):
    """Organization role types"""
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    VIEWER = "viewer"


class OrganizationUser(BaseModel):
    """
    Organization User model - junction table linking users to organizations
    Manages user membership and roles within organizations
    """
    __tablename__ = "organization_users"

    # Foreign Keys
    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Role and Permissions
    role = Column(
        Enum(OrganizationRole),
        default=OrganizationRole.VIEWER,
        nullable=False
    )
    permissions = Column(JSON, default=dict, nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    organization = relationship("Organization", backref="organization_users")
    user = relationship("User", backref="organization_memberships")

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "user_id",
            name="uq_organization_user"
        ),
    )

    def __repr__(self):
        return f"<OrganizationUser org={self.organization_id} user={self.user_id} role={self.role.value}>"
