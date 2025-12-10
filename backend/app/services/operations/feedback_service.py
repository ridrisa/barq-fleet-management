"""Customer Feedback Service"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.operations.feedback import (
    CustomerFeedback,
    FeedbackSentiment,
    FeedbackStatus,
    FeedbackTemplate,
    FeedbackType,
)
from app.schemas.operations.feedback import (
    CustomerFeedbackCreate,
    CustomerFeedbackUpdate,
    FeedbackTemplateCreate,
    FeedbackTemplateUpdate,
)
from app.services.base import CRUDBase


class CustomerFeedbackService(
    CRUDBase[CustomerFeedback, CustomerFeedbackCreate, CustomerFeedbackUpdate]
):
    """Service for customer feedback management operations"""

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, organization_id: int = None
    ) -> List[CustomerFeedback]:
        """Get multiple feedbacks with optional organization filter"""
        query = db.query(CustomerFeedback)
        if organization_id:
            query = query.filter(CustomerFeedback.organization_id == organization_id)
        return (
            query.order_by(CustomerFeedback.submitted_at.desc()).offset(skip).limit(limit).all()
        )

    def create_with_number(
        self, db: Session, *, obj_in: CustomerFeedbackCreate, organization_id: int = None
    ) -> CustomerFeedback:
        """Create feedback with auto-generated number"""
        last_feedback = db.query(CustomerFeedback).order_by(CustomerFeedback.id.desc()).first()
        next_number = 1 if not last_feedback else last_feedback.id + 1
        feedback_number = f"FB-{datetime.now().strftime('%Y%m%d')}-{next_number:04d}"

        obj_in_data = obj_in.model_dump()
        if organization_id:
            obj_in_data["organization_id"] = organization_id
        db_obj = CustomerFeedback(
            **obj_in_data,
            feedback_number=feedback_number,
            submitted_at=obj_in.submitted_at or datetime.utcnow(),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_number(
        self, db: Session, *, feedback_number: str, organization_id: int = None
    ) -> Optional[CustomerFeedback]:
        """Get feedback by number"""
        query = db.query(CustomerFeedback).filter(
            CustomerFeedback.feedback_number == feedback_number
        )
        if organization_id:
            query = query.filter(CustomerFeedback.organization_id == organization_id)
        return query.first()

    def get_by_delivery(
        self, db: Session, *, delivery_id: int, organization_id: int = None
    ) -> List[CustomerFeedback]:
        """Get all feedbacks for a delivery"""
        query = db.query(CustomerFeedback).filter(CustomerFeedback.delivery_id == delivery_id)
        if organization_id:
            query = query.filter(CustomerFeedback.organization_id == organization_id)
        return query.order_by(CustomerFeedback.submitted_at.desc()).all()

    def get_by_courier(
        self,
        db: Session,
        *,
        courier_id: int,
        skip: int = 0,
        limit: int = 100,
        organization_id: int = None,
    ) -> List[CustomerFeedback]:
        """Get feedbacks for a courier"""
        query = db.query(CustomerFeedback).filter(CustomerFeedback.courier_id == courier_id)
        if organization_id:
            query = query.filter(CustomerFeedback.organization_id == organization_id)
        return (
            query.order_by(CustomerFeedback.submitted_at.desc()).offset(skip).limit(limit).all()
        )

    def get_pending(
        self, db: Session, *, skip: int = 0, limit: int = 100, organization_id: int = None
    ) -> List[CustomerFeedback]:
        """Get pending feedbacks"""
        query = db.query(CustomerFeedback).filter(
            CustomerFeedback.status == FeedbackStatus.PENDING
        )
        if organization_id:
            query = query.filter(CustomerFeedback.organization_id == organization_id)
        return (
            query.order_by(CustomerFeedback.submitted_at.asc()).offset(skip).limit(limit).all()
        )

    def get_by_type(
        self,
        db: Session,
        *,
        feedback_type: FeedbackType,
        skip: int = 0,
        limit: int = 100,
        organization_id: int = None,
    ) -> List[CustomerFeedback]:
        """Get feedbacks by type"""
        query = db.query(CustomerFeedback).filter(
            CustomerFeedback.feedback_type == feedback_type
        )
        if organization_id:
            query = query.filter(CustomerFeedback.organization_id == organization_id)
        return (
            query.order_by(CustomerFeedback.submitted_at.desc()).offset(skip).limit(limit).all()
        )

    def get_complaints(
        self, db: Session, *, skip: int = 0, limit: int = 100, organization_id: int = None
    ) -> List[CustomerFeedback]:
        """Get all complaints"""
        query = db.query(CustomerFeedback).filter(CustomerFeedback.is_complaint == True)
        if organization_id:
            query = query.filter(CustomerFeedback.organization_id == organization_id)
        return (
            query.order_by(CustomerFeedback.submitted_at.desc()).offset(skip).limit(limit).all()
        )

    def get_negative_feedbacks(
        self, db: Session, *, skip: int = 0, limit: int = 100, organization_id: int = None
    ) -> List[CustomerFeedback]:
        """Get negative feedbacks (rating <= 2)"""
        query = db.query(CustomerFeedback).filter(CustomerFeedback.overall_rating <= 2)
        if organization_id:
            query = query.filter(CustomerFeedback.organization_id == organization_id)
        return (
            query.order_by(CustomerFeedback.submitted_at.desc()).offset(skip).limit(limit).all()
        )

    def get_escalated(
        self, db: Session, *, skip: int = 0, limit: int = 100, organization_id: int = None
    ) -> List[CustomerFeedback]:
        """Get escalated feedbacks"""
        query = db.query(CustomerFeedback).filter(CustomerFeedback.is_escalated == True)
        if organization_id:
            query = query.filter(CustomerFeedback.organization_id == organization_id)
        return (
            query.order_by(CustomerFeedback.escalated_at.desc()).offset(skip).limit(limit).all()
        )

    def get_requiring_followup(
        self, db: Session, organization_id: int = None
    ) -> List[CustomerFeedback]:
        """Get feedbacks requiring follow-up"""
        query = db.query(CustomerFeedback).filter(
            CustomerFeedback.requires_followup == True,
            CustomerFeedback.followup_completed == False,
        )
        if organization_id:
            query = query.filter(CustomerFeedback.organization_id == organization_id)
        return query.order_by(CustomerFeedback.followup_date.asc()).all()

    def respond(
        self, db: Session, *, feedback_id: int, response_text: str, responded_by_id: int
    ) -> Optional[CustomerFeedback]:
        """Respond to feedback"""
        feedback = self.get(db, id=feedback_id)
        if feedback:
            feedback.response_text = response_text
            feedback.responded_by_id = responded_by_id
            feedback.responded_at = datetime.utcnow()
            feedback.status = FeedbackStatus.RESPONDED
            # Calculate response time
            if feedback.submitted_at:
                delta = feedback.responded_at - feedback.submitted_at
                feedback.response_time_hours = round(delta.total_seconds() / 3600, 2)
            db.add(feedback)
            db.commit()
            db.refresh(feedback)
        return feedback

    def resolve(
        self,
        db: Session,
        *,
        feedback_id: int,
        resolution_text: str,
        resolved_by_id: int,
        compensation_amount: float = 0.0,
        refund_amount: float = 0.0,
        action_taken: str = None,
    ) -> Optional[CustomerFeedback]:
        """Resolve feedback"""
        feedback = self.get(db, id=feedback_id)
        if feedback:
            feedback.resolution_text = resolution_text
            feedback.resolved_by_id = resolved_by_id
            feedback.resolved_at = datetime.utcnow()
            feedback.status = FeedbackStatus.RESOLVED
            feedback.compensation_amount = compensation_amount
            feedback.refund_amount = refund_amount
            feedback.action_taken = action_taken
            db.add(feedback)
            db.commit()
            db.refresh(feedback)
        return feedback

    def escalate(
        self, db: Session, *, feedback_id: int, escalated_to_id: int, reason: str
    ) -> Optional[CustomerFeedback]:
        """Escalate feedback"""
        feedback = self.get(db, id=feedback_id)
        if feedback:
            feedback.is_escalated = True
            feedback.escalated_at = datetime.utcnow()
            feedback.escalated_to_id = escalated_to_id
            feedback.escalation_reason = reason
            feedback.status = FeedbackStatus.ESCALATED
            db.add(feedback)
            db.commit()
            db.refresh(feedback)
        return feedback

    def close(self, db: Session, *, feedback_id: int) -> Optional[CustomerFeedback]:
        """Close feedback"""
        feedback = self.get(db, id=feedback_id)
        if feedback:
            feedback.status = FeedbackStatus.CLOSED
            db.add(feedback)
            db.commit()
            db.refresh(feedback)
        return feedback

    def schedule_followup(
        self, db: Session, *, feedback_id: int, followup_date: datetime, notes: str = None
    ) -> Optional[CustomerFeedback]:
        """Schedule follow-up for feedback"""
        feedback = self.get(db, id=feedback_id)
        if feedback:
            feedback.requires_followup = True
            feedback.followup_date = followup_date
            feedback.followup_notes = notes
            db.add(feedback)
            db.commit()
            db.refresh(feedback)
        return feedback

    def complete_followup(
        self, db: Session, *, feedback_id: int, notes: str = None
    ) -> Optional[CustomerFeedback]:
        """Complete follow-up for feedback"""
        feedback = self.get(db, id=feedback_id)
        if feedback:
            feedback.followup_completed = True
            if notes:
                feedback.followup_notes = (feedback.followup_notes or "") + "\n" + notes
            db.add(feedback)
            db.commit()
            db.refresh(feedback)
        return feedback

    def get_avg_rating_by_courier(
        self, db: Session, *, courier_id: int, organization_id: int = None
    ) -> float:
        """Get average rating for a courier"""
        query = db.query(func.avg(CustomerFeedback.overall_rating)).filter(
            CustomerFeedback.courier_id == courier_id
        )
        if organization_id:
            query = query.filter(CustomerFeedback.organization_id == organization_id)
        result = query.scalar()
        return float(result) if result else 0.0

    def get_feedback_counts_by_status(self, db: Session) -> dict:
        """Get feedback counts by status"""
        counts = (
            db.query(CustomerFeedback.status, func.count(CustomerFeedback.id))
            .group_by(CustomerFeedback.status)
            .all()
        )
        return {status.value: count for status, count in counts}


class FeedbackTemplateService(
    CRUDBase[FeedbackTemplate, FeedbackTemplateCreate, FeedbackTemplateUpdate]
):
    """Service for feedback template management operations"""

    def get_by_code(
        self, db: Session, *, template_code: str, organization_id: int = None
    ) -> Optional[FeedbackTemplate]:
        """Get template by code"""
        query = db.query(FeedbackTemplate).filter(
            FeedbackTemplate.template_code == template_code
        )
        if organization_id:
            query = query.filter(FeedbackTemplate.organization_id == organization_id)
        return query.first()

    def get_active_templates(
        self, db: Session, organization_id: int = None
    ) -> List[FeedbackTemplate]:
        """Get all active templates"""
        query = db.query(FeedbackTemplate).filter(FeedbackTemplate.is_active == True)
        if organization_id:
            query = query.filter(FeedbackTemplate.organization_id == organization_id)
        return query.all()

    def get_by_type(
        self, db: Session, *, template_type: FeedbackType, organization_id: int = None
    ) -> List[FeedbackTemplate]:
        """Get templates by type"""
        query = db.query(FeedbackTemplate).filter(
            FeedbackTemplate.template_type == template_type, FeedbackTemplate.is_active == True
        )
        if organization_id:
            query = query.filter(FeedbackTemplate.organization_id == organization_id)
        return query.all()

    def get_by_sentiment(
        self, db: Session, *, sentiment_type: FeedbackSentiment, organization_id: int = None
    ) -> List[FeedbackTemplate]:
        """Get templates by sentiment"""
        query = db.query(FeedbackTemplate).filter(
            FeedbackTemplate.sentiment_type == sentiment_type,
            FeedbackTemplate.is_active == True,
        )
        if organization_id:
            query = query.filter(FeedbackTemplate.organization_id == organization_id)
        return query.all()

    def create(
        self, db: Session, *, obj_in: FeedbackTemplateCreate, organization_id: int = None
    ) -> FeedbackTemplate:
        """Create template with organization_id"""
        obj_in_data = obj_in.model_dump()
        if organization_id:
            obj_in_data["organization_id"] = organization_id
        db_obj = FeedbackTemplate(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def increment_usage(self, db: Session, *, template_id: int) -> Optional[FeedbackTemplate]:
        """Increment template usage count"""
        template = self.get(db, id=template_id)
        if template:
            template.usage_count += 1
            db.add(template)
            db.commit()
            db.refresh(template)
        return template


customer_feedback_service = CustomerFeedbackService(CustomerFeedback)
feedback_template_service = FeedbackTemplateService(FeedbackTemplate)
