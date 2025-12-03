"""Knowledge Base Article Model"""

import enum

from sqlalchemy import Boolean, Column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class ArticleStatus(str, enum.Enum):
    """Article status"""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class KBArticle(TenantMixin, BaseModel):
    """
    Knowledge Base Article model - Self-service documentation
    Helps reduce support ticket volume with searchable articles
    """

    __tablename__ = "kb_articles"

    # Article Identification
    slug = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="URL-friendly slug for the article",
    )

    # Content
    title = Column(String(255), nullable=False, index=True, comment="Article title")
    content = Column(Text, nullable=False, comment="Article content (Markdown supported)")
    summary = Column(String(500), nullable=True, comment="Short summary/excerpt")

    # Categorization
    category = Column(String(100), nullable=False, index=True, comment="Article category")
    tags = Column(Text, nullable=True, comment="Comma-separated tags for search")

    # Status & Publishing
    status = Column(
        SQLEnum(ArticleStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=ArticleStatus.DRAFT,
        nullable=False,
        index=True,
        comment="Article publication status",
    )
    version = Column(Integer, default=1, nullable=False, comment="Article version number")

    # Authorship
    author_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
        comment="Article author",
    )

    # Analytics
    view_count = Column(
        Integer, default=0, nullable=False, comment="Number of times article was viewed"
    )
    helpful_count = Column(Integer, default=0, nullable=False, comment="Number of helpful votes")
    not_helpful_count = Column(
        Integer, default=0, nullable=False, comment="Number of not helpful votes"
    )

    # SEO
    meta_description = Column(String(255), nullable=True, comment="SEO meta description")

    # Relationships
    author = relationship("User", foreign_keys=[author_id])

    def __repr__(self):
        return f"<KBArticle {self.slug}: {self.title}>"

    @property
    def is_published(self) -> bool:
        """Check if article is published"""
        return self.status == ArticleStatus.PUBLISHED

    @property
    def helpfulness_score(self) -> float:
        """Calculate helpfulness score (0-1)"""
        total = self.helpful_count + self.not_helpful_count
        if total == 0:
            return 0.0
        return self.helpful_count / total
