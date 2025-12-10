"""Consolidated Knowledge Service

This module consolidates knowledge-related services:
- FAQ management
- Knowledge Base article management
"""

from typing import Dict, List, Optional

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.models.support import ArticleStatus, FAQ, KBArticle
from app.schemas.support import FAQCreate, FAQUpdate, KBArticleCreate, KBArticleUpdate
from app.services.base import CRUDBase


# =============================================================================
# FAQ Service
# =============================================================================


class FAQService(CRUDBase[FAQ, FAQCreate, FAQUpdate]):
    """Service for FAQ operations"""

    def get_active(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[FAQ]:
        """Get active FAQs only"""
        return (
            db.query(self.model)
            .filter(self.model.is_active == True)
            .order_by(self.model.order.asc(), self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_category(
        self, db: Session, *, category: str, skip: int = 0, limit: int = 100
    ) -> List[FAQ]:
        """Get FAQs by category"""
        return (
            db.query(self.model)
            .filter(self.model.category == category, self.model.is_active == True)
            .order_by(self.model.order.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search(self, db: Session, *, query: str, skip: int = 0, limit: int = 100) -> List[FAQ]:
        """Search FAQs by question or answer"""
        search_term = f"%{query}%"
        return (
            db.query(self.model)
            .filter(
                self.model.is_active == True,
                or_(self.model.question.ilike(search_term), self.model.answer.ilike(search_term)),
            )
            .order_by(self.model.view_count.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def increment_view_count(self, db: Session, *, faq_id: int) -> Optional[FAQ]:
        """Increment FAQ view count"""
        faq = self.get(db, id=faq_id)
        if faq:
            faq.view_count += 1
            db.commit()
            db.refresh(faq)
        return faq

    def get_categories(self, db: Session) -> Dict[str, int]:
        """Get list of categories with FAQ counts"""
        results = (
            db.query(self.model.category, func.count(self.model.id))
            .filter(self.model.is_active == True)
            .group_by(self.model.category)
            .all()
        )
        return {category: count for category, count in results}

    def reorder(self, db: Session, *, faq_id: int, new_order: int) -> Optional[FAQ]:
        """Update FAQ order"""
        faq = self.get(db, id=faq_id)
        if faq:
            faq.order = new_order
            db.commit()
            db.refresh(faq)
        return faq

    def get_top_viewed(self, db: Session, *, limit: int = 10) -> List[FAQ]:
        """Get top viewed FAQs"""
        return (
            db.query(self.model)
            .filter(self.model.is_active == True)
            .order_by(self.model.view_count.desc())
            .limit(limit)
            .all()
        )


# =============================================================================
# Knowledge Base Article Service
# =============================================================================


class KBArticleService(CRUDBase[KBArticle, KBArticleCreate, KBArticleUpdate]):
    """Service for knowledge base article operations"""

    def get_by_slug(self, db: Session, *, slug: str) -> Optional[KBArticle]:
        """Get article by slug"""
        return db.query(self.model).filter(self.model.slug == slug).first()

    def get_published(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[KBArticle]:
        """Get published articles only"""
        return (
            db.query(self.model)
            .filter(self.model.status == ArticleStatus.PUBLISHED)
            .order_by(self.model.view_count.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_category(
        self, db: Session, *, category: str, skip: int = 0, limit: int = 100
    ) -> List[KBArticle]:
        """Get articles by category"""
        return (
            db.query(self.model)
            .filter(
                and_(self.model.category == category, self.model.status == ArticleStatus.PUBLISHED)
            )
            .order_by(self.model.view_count.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search(
        self, db: Session, *, query: str, skip: int = 0, limit: int = 100
    ) -> List[KBArticle]:
        """
        Search articles by title, content, or tags

        Args:
            db: Database session
            query: Search query string
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching articles
        """
        search_term = f"%{query}%"
        return (
            db.query(self.model)
            .filter(
                and_(
                    or_(
                        self.model.title.ilike(search_term),
                        self.model.content.ilike(search_term),
                        self.model.tags.ilike(search_term),
                        self.model.summary.ilike(search_term),
                    ),
                    self.model.status == ArticleStatus.PUBLISHED,
                )
            )
            .order_by(self.model.view_count.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def increment_view_count(self, db: Session, *, article_id: int) -> Optional[KBArticle]:
        """Increment article view count"""
        article = self.get(db, id=article_id)
        if article:
            article.view_count += 1
            db.commit()
            db.refresh(article)
        return article

    def vote_helpful(self, db: Session, *, article_id: int, helpful: bool) -> Optional[KBArticle]:
        """Record helpful/not helpful vote"""
        article = self.get(db, id=article_id)
        if article:
            if helpful:
                article.helpful_count += 1
            else:
                article.not_helpful_count += 1
            db.commit()
            db.refresh(article)
        return article

    def get_categories(self, db: Session) -> List[str]:
        """Get list of all unique categories"""
        return [
            row[0]
            for row in db.query(self.model.category)
            .filter(self.model.status == ArticleStatus.PUBLISHED)
            .distinct()
            .all()
        ]

    def get_top_articles(self, db: Session, *, limit: int = 10) -> List[KBArticle]:
        """Get top viewed articles"""
        return (
            db.query(self.model)
            .filter(self.model.status == ArticleStatus.PUBLISHED)
            .order_by(self.model.view_count.desc())
            .limit(limit)
            .all()
        )

    def publish(self, db: Session, *, article_id: int) -> Optional[KBArticle]:
        """Publish an article"""
        article = self.get(db, id=article_id)
        if article:
            article.status = ArticleStatus.PUBLISHED
            article.version += 1
            db.commit()
            db.refresh(article)
        return article

    def unpublish(self, db: Session, *, article_id: int) -> Optional[KBArticle]:
        """Unpublish an article (set to draft)"""
        article = self.get(db, id=article_id)
        if article:
            article.status = ArticleStatus.DRAFT
            db.commit()
            db.refresh(article)
        return article


# =============================================================================
# Service Instances
# =============================================================================

faq_service = FAQService(FAQ)
kb_article_service = KBArticleService(KBArticle)
