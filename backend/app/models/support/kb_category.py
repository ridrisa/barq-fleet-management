"""Knowledge Base Category Model"""
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class KBCategory(TenantMixin, BaseModel):
    """
    Knowledge Base Category model - Hierarchical categories for articles
    Allows organizing articles in a tree structure
    """

    __tablename__ = "kb_categories"

    # Category Identification
    name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Category name"
    )
    slug = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="URL-friendly slug"
    )
    description = Column(
        Text,
        nullable=True,
        comment="Category description"
    )

    # Hierarchy
    parent_id = Column(
        Integer,
        ForeignKey("kb_categories.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Parent category ID for hierarchy"
    )

    # Display
    icon = Column(
        String(50),
        nullable=True,
        comment="Icon name/class for display"
    )
    order = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Display order within parent"
    )

    # Status
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether category is active"
    )
    is_public = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether category is publicly visible"
    )

    # Analytics
    article_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of articles in this category"
    )

    # Relationships
    parent = relationship("KBCategory", remote_side="KBCategory.id", backref="children")

    def __repr__(self):
        return f"<KBCategory {self.slug}: {self.name}>"

    @property
    def full_path(self) -> str:
        """Get full category path (parent/child/grandchild)"""
        path = [self.name]
        current = self
        while current.parent:
            current = current.parent
            path.insert(0, current.name)
        return " / ".join(path)
