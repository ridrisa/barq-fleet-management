"""Customer Feedback Service"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.services.base import CRUDBase
from app.models.support import Feedback, FeedbackCategory, FeedbackStatus
from app.schemas.support import FeedbackCreate, FeedbackUpdate


class FeedbackService(CRUDBase[Feedback, FeedbackCreate, FeedbackUpdate]):
    """Service for customer feedback operations"""

    def get_by_category(
        self,
        db: Session,
        *,
        category: FeedbackCategory,
        skip: int = 0,
        limit: int = 100
    ) -> List[Feedback]:
        """Get feedback by category"""
        return (
            db.query(self.model)
            .filter(self.model.category == category)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(
        self,
        db: Session,
        *,
        status: FeedbackStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Feedback]:
        """Get feedback by status"""
        return (
            db.query(self.model)
            .filter(self.model.status == status)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_rating(
        self,
        db: Session,
        *,
        rating: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Feedback]:
        """Get feedback by rating"""
        return (
            db.query(self.model)
            .filter(self.model.rating == rating)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_positive_feedback(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Feedback]:
        """Get positive feedback (4-5 stars)"""
        return (
            db.query(self.model)
            .filter(self.model.rating >= 4)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_negative_feedback(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Feedback]:
        """Get negative feedback (1-2 stars)"""
        return (
            db.query(self.model)
            .filter(self.model.rating <= 2)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def respond_to_feedback(
        self,
        db: Session,
        *,
        feedback_id: int,
        response: str,
        responded_by: int
    ) -> Optional[Feedback]:
        """Respond to customer feedback"""
        feedback = self.get(db, id=feedback_id)
        if feedback:
            feedback.response = response
            feedback.responded_by = responded_by
            feedback.status = FeedbackStatus.COMPLETED
            db.commit()
            db.refresh(feedback)
        return feedback

    def get_statistics(self, db: Session) -> Dict:
        """Get feedback statistics"""
        total = db.query(func.count(self.model.id)).scalar()

        # By category
        by_category = dict(
            db.query(self.model.category, func.count(self.model.id))
            .group_by(self.model.category)
            .all()
        )

        # By status
        by_status = dict(
            db.query(self.model.status, func.count(self.model.id))
            .group_by(self.model.status)
            .all()
        )

        # By rating
        by_rating = dict(
            db.query(self.model.rating, func.count(self.model.id))
            .filter(self.model.rating.isnot(None))
            .group_by(self.model.rating)
            .all()
        )

        # Average rating
        avg_rating = db.query(func.avg(self.model.rating)).filter(
            self.model.rating.isnot(None)
        ).scalar() or 0.0

        # Positive/Negative counts
        positive_count = db.query(func.count(self.model.id)).filter(
            self.model.rating >= 4
        ).scalar()

        negative_count = db.query(func.count(self.model.id)).filter(
            self.model.rating <= 2
        ).scalar()

        # Response rate
        responded = db.query(func.count(self.model.id)).filter(
            self.model.response.isnot(None)
        ).scalar()
        response_rate = (responded / total * 100) if total > 0 else 0.0

        return {
            "total": total,
            "by_category": {k.value: v for k, v in by_category.items()},
            "by_status": {k.value: v for k, v in by_status.items()},
            "by_rating": by_rating,
            "average_rating": round(avg_rating, 2),
            "positive_count": positive_count,
            "negative_count": negative_count,
            "response_rate": round(response_rate, 2)
        }


# Create service instance
feedback_service = FeedbackService(Feedback)
