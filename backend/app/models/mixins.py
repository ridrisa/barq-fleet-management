"""
Multi-Tenancy Mixins for BARQ Fleet Management
Provides tenant isolation through organization_id on all tenant-aware models
"""

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer
from sqlalchemy.orm import declared_attr, relationship
from sqlalchemy.sql import func


class TenantMixin:
    """
    Mixin to add organization_id to tenant-aware models.

    This mixin provides:
    - organization_id foreign key column with cascade delete
    - Automatic index on organization_id for query performance
    - Relationship to Organization model

    Usage:
        class Courier(TenantMixin, BaseModel):
            __tablename__ = "couriers"
            # ... other columns
    """

    @declared_attr
    def organization_id(cls):
        """Organization ID foreign key - required for all tenant-aware models"""
        return Column(
            Integer,
            ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
            comment="Organization ID for multi-tenant isolation",
        )

    @declared_attr
    def organization(cls):
        """Relationship to Organization model"""
        return relationship("Organization", foreign_keys=[cls.organization_id], lazy="select")

    # Note: We don't use __table_args__ here because it causes recursion issues
    # The organization_id column already has index=True in the column definition above
    # Child models can define their own __table_args__ without issues


class SoftDeleteMixin:
    """
    Mixin for soft delete functionality.
    Models with this mixin won't be physically deleted but marked as deleted.
    """

    @declared_attr
    def is_deleted(cls):
        from sqlalchemy import Boolean, Column

        return Column(Boolean, default=False, nullable=False, index=True)

    @declared_attr
    def deleted_at(cls):
        from sqlalchemy import Column, DateTime

        return Column(DateTime(timezone=True), nullable=True)

    @declared_attr
    def deleted_by(cls):
        return Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)


class AuditMixin:
    """
    Mixin for audit trail functionality.
    Tracks who created and last modified the record.
    """

    @declared_attr
    def created_by(cls):
        return Column(
            Integer,
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
            comment="User who created this record",
        )

    @declared_attr
    def updated_by(cls):
        return Column(
            Integer,
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
            comment="User who last updated this record",
        )


__all__ = [
    "TenantMixin",
    "SoftDeleteMixin",
    "AuditMixin",
]
