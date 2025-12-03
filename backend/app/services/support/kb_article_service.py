"""Knowledge Base Article Service"""

from typing import Dict, List, Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.support import ArticleStatus, KBArticle
from app.schemas.support import KBArticleCreate, KBArticleUpdate
from app.services.base import CRUDBase


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


# Create service instance
kb_article_service = KBArticleService(KBArticle)
