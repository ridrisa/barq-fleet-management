"""FAQ Service"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.services.base import CRUDBase
from app.models.support import FAQ
from app.schemas.support import FAQCreate, FAQUpdate


class FAQService(CRUDBase[FAQ, FAQCreate, FAQUpdate]):
    """Service for FAQ operations"""

    def get_active(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[FAQ]:
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
        self,
        db: Session,
        *,
        category: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[FAQ]:
        """Get FAQs by category"""
        return (
            db.query(self.model)
            .filter(
                self.model.category == category,
                self.model.is_active == True
            )
            .order_by(self.model.order.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search(
        self,
        db: Session,
        *,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[FAQ]:
        """Search FAQs by question or answer"""
        search_term = f"%{query}%"
        return (
            db.query(self.model)
            .filter(
                self.model.is_active == True,
                or_(
                    self.model.question.ilike(search_term),
                    self.model.answer.ilike(search_term)
                )
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

    def get_top_viewed(
        self,
        db: Session,
        *,
        limit: int = 10
    ) -> List[FAQ]:
        """Get top viewed FAQs"""
        return (
            db.query(self.model)
            .filter(self.model.is_active == True)
            .order_by(self.model.view_count.desc())
            .limit(limit)
            .all()
        )


# Create service instance
faq_service = FAQService(FAQ)
