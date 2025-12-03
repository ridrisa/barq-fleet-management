"""Knowledge Base Article Schemas"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from app.models.support import ArticleStatus


class KBArticleBase(BaseModel):
    """Base KB article schema"""

    title: str = Field(..., min_length=5, max_length=255, description="Article title")
    content: str = Field(..., min_length=10, description="Article content (Markdown supported)")
    summary: Optional[str] = Field(None, max_length=500, description="Short summary")
    category: str = Field(..., min_length=1, max_length=100, description="Article category")
    tags: Optional[str] = Field(None, description="Comma-separated tags")
    meta_description: Optional[str] = Field(
        None, max_length=255, description="SEO meta description"
    )


class KBArticleCreate(KBArticleBase):
    """Schema for creating a new KB article"""

    slug: str = Field(..., min_length=1, max_length=255, description="URL-friendly slug")
    status: ArticleStatus = Field(default=ArticleStatus.DRAFT, description="Article status")

    @validator("slug")
    def validate_slug(cls, v):
        """Ensure slug is URL-friendly"""
        import re

        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError("Slug must contain only lowercase letters, numbers, and hyphens")
        return v


class KBArticleUpdate(BaseModel):
    """Schema for updating a KB article"""

    title: Optional[str] = Field(None, min_length=5, max_length=255)
    content: Optional[str] = Field(None, min_length=10)
    summary: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    tags: Optional[str] = None
    status: Optional[ArticleStatus] = None
    meta_description: Optional[str] = Field(None, max_length=255)


class KBArticlePublish(BaseModel):
    """Schema for publishing an article"""

    status: ArticleStatus = Field(..., description="New status (PUBLISHED or DRAFT)")


class KBArticleVote(BaseModel):
    """Schema for voting on article helpfulness"""

    helpful: bool = Field(..., description="True if helpful, False if not helpful")


class KBArticleResponse(KBArticleBase):
    """Schema for KB article response"""

    id: int
    slug: str
    status: ArticleStatus
    version: int
    author_id: int
    view_count: int
    helpful_count: int
    not_helpful_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_published: bool = Field(default=False, description="Whether article is published")
    helpfulness_score: float = Field(default=0.0, description="Helpfulness score (0-1)")

    class Config:
        from_attributes = True


class KBArticleList(BaseModel):
    """Minimal KB article schema for list views"""

    id: int
    slug: str
    title: str
    summary: Optional[str] = None
    category: str
    status: ArticleStatus
    view_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class KBArticleWithAuthor(KBArticleResponse):
    """Extended KB article with author information"""

    author_name: str

    class Config:
        from_attributes = True


class KBArticleSearch(BaseModel):
    """Schema for KB article search results"""

    articles: List[KBArticleList]
    total: int
    page: int
    page_size: int
