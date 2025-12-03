"""
Customer Feedback API Routes
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_organization, get_current_user
from app.crud.operations.feedback import customer_feedback, feedback_template
from app.models.tenant.organization import Organization
from app.schemas.operations.feedback import (
    CustomerFeedbackCreate,
    CustomerFeedbackResponse,
    CustomerFeedbackUpdate,
    FeedbackEscalateSchema,
    FeedbackFollowupSchema,
    FeedbackMetrics,
    FeedbackResolveSchema,
    FeedbackRespondSchema,
    FeedbackSentiment,
    FeedbackStatus,
    FeedbackSummary,
    FeedbackTemplateCreate,
    FeedbackTemplateResponse,
    FeedbackTemplateUpdate,
    FeedbackType,
)

router = APIRouter()


# Customer Feedback Endpoints
@router.get("/", response_model=List[CustomerFeedbackResponse])
def list_feedbacks(
    skip: int = 0,
    limit: int = 100,
    feedback_type: FeedbackType = Query(None, description="Filter by feedback type"),
    feedback_status: FeedbackStatus = Query(None, alias="status", description="Filter by status"),
    courier_id: int = Query(None, description="Filter by courier"),
    delivery_id: int = Query(None, description="Filter by delivery"),
    is_complaint: bool = Query(None, description="Filter complaints only"),
    min_rating: int = Query(None, ge=1, le=5, description="Minimum rating"),
    max_rating: int = Query(None, ge=1, le=5, description="Maximum rating"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List all customer feedbacks with filtering options

    Filters:
    - feedback_type: Filter by type (delivery, courier, service, etc.)
    - status: Filter by processing status
    - courier_id: Filter by courier
    - delivery_id: Filter by delivery
    - is_complaint: Show only complaints
    - min_rating/max_rating: Filter by rating range
    """
    if feedback_type:
        feedbacks = customer_feedback.get_by_type(
            db, feedback_type=feedback_type, skip=skip, limit=limit, organization_id=current_org.id
        )
    elif courier_id:
        feedbacks = customer_feedback.get_by_courier(
            db, courier_id=courier_id, skip=skip, limit=limit, organization_id=current_org.id
        )
    elif delivery_id:
        feedbacks = customer_feedback.get_by_delivery(
            db, delivery_id=delivery_id, organization_id=current_org.id
        )
    elif is_complaint:
        feedbacks = customer_feedback.get_complaints(
            db, skip=skip, limit=limit, organization_id=current_org.id
        )
    else:
        feedbacks = customer_feedback.get_multi(
            db, skip=skip, limit=limit, organization_id=current_org.id
        )
    return feedbacks


@router.get("/pending", response_model=List[CustomerFeedbackResponse])
def list_pending_feedbacks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List all pending feedbacks awaiting review

    Business Logic:
    - Returns feedbacks with status PENDING
    - Sorted by submission time (oldest first - FIFO)
    - Used by support team dashboard
    """
    feedbacks = customer_feedback.get_pending(
        db, skip=skip, limit=limit, organization_id=current_org.id
    )
    return feedbacks


@router.get("/negative", response_model=List[CustomerFeedbackResponse])
def list_negative_feedbacks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List negative feedbacks (rating <= 2)

    Business Logic:
    - Returns feedbacks with rating 1 or 2
    - Requires immediate attention
    - Priority for resolution
    """
    feedbacks = customer_feedback.get_negative_feedbacks(
        db, skip=skip, limit=limit, organization_id=current_org.id
    )
    return feedbacks


@router.get("/escalated", response_model=List[CustomerFeedbackResponse])
def list_escalated_feedbacks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List escalated feedbacks

    Business Logic:
    - Returns feedbacks that have been escalated
    - Requires supervisor/manager attention
    - Sorted by escalation time
    """
    feedbacks = customer_feedback.get_escalated(
        db, skip=skip, limit=limit, organization_id=current_org.id
    )
    return feedbacks


@router.get("/followup-required", response_model=List[CustomerFeedbackResponse])
def list_feedbacks_requiring_followup(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List feedbacks requiring follow-up

    Business Logic:
    - Returns feedbacks with requires_followup = True
    - Excludes completed follow-ups
    - Sorted by follow-up date (due soonest first)
    """
    feedbacks = customer_feedback.get_requiring_followup(db, organization_id=current_org.id)
    return feedbacks


@router.get("/{feedback_id}", response_model=CustomerFeedbackResponse)
def get_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get a specific feedback by ID"""
    feedback = customer_feedback.get(db, id=feedback_id)
    if not feedback or feedback.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    return feedback


@router.post("/", response_model=CustomerFeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    feedback_in: CustomerFeedbackCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Submit new customer feedback

    Business Logic:
    - Auto-generates feedback number
    - Sets status to PENDING
    - Records submission timestamp
    - Analyzes sentiment if AI enabled
    - Auto-categorizes based on keywords
    - Triggers notification for negative feedback
    """
    # TODO: Validate delivery exists if delivery_id provided
    # TODO: Validate courier exists if courier_id provided
    # TODO: AI sentiment analysis
    # TODO: Auto-categorization

    feedback = customer_feedback.create_with_number(
        db, obj_in=feedback_in, organization_id=current_org.id
    )
    return feedback


@router.put("/{feedback_id}", response_model=CustomerFeedbackResponse)
def update_feedback(
    feedback_id: int,
    feedback_in: CustomerFeedbackUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update feedback details"""
    feedback = customer_feedback.get(db, id=feedback_id)
    if not feedback or feedback.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    feedback = customer_feedback.update(db, db_obj=feedback, obj_in=feedback_in)
    return feedback


@router.post("/{feedback_id}/respond", response_model=CustomerFeedbackResponse)
def respond_to_feedback(
    feedback_id: int,
    response_data: FeedbackRespondSchema,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Respond to customer feedback

    Business Logic:
    - Records response and responder
    - Updates status to RESPONDED
    - Calculates response time
    - Optionally sends email to customer
    - Can use template if specified
    """
    feedback = customer_feedback.get(db, id=feedback_id)
    if not feedback or feedback.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

    if feedback.status == FeedbackStatus.CLOSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot respond to closed feedback"
        )

    # Use template if specified
    response_text = response_data.response_text
    if response_data.use_template:
        template = feedback_template.get_by_code(db, template_code=response_data.use_template)
        if template:
            response_text = template.body
            feedback_template.increment_usage(db, template_id=template.id)

    # Get current user ID
    responded_by_id = current_user.id if hasattr(current_user, "id") else 1

    feedback = customer_feedback.respond(
        db, feedback_id=feedback_id, response_text=response_text, responded_by_id=responded_by_id
    )

    # Update internal notes if provided
    if response_data.internal_notes:
        feedback.internal_notes = response_data.internal_notes
        db.add(feedback)
        db.commit()
        db.refresh(feedback)

    # TODO: Send email if response_data.send_email

    return feedback


@router.post("/{feedback_id}/resolve", response_model=CustomerFeedbackResponse)
def resolve_feedback(
    feedback_id: int,
    resolution: FeedbackResolveSchema,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Resolve customer feedback

    Business Logic:
    - Records resolution details
    - Updates status to RESOLVED
    - Records compensation/refund if applicable
    - Documents action taken
    - Optionally notifies customer
    """
    feedback = customer_feedback.get(db, id=feedback_id)
    if not feedback or feedback.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

    if feedback.status == FeedbackStatus.CLOSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot resolve closed feedback"
        )

    # Get current user ID
    resolved_by_id = current_user.id if hasattr(current_user, "id") else 1

    feedback = customer_feedback.resolve(
        db,
        feedback_id=feedback_id,
        resolution_text=resolution.resolution_text,
        resolved_by_id=resolved_by_id,
        compensation_amount=float(resolution.compensation_amount or 0),
        refund_amount=float(resolution.refund_amount or 0),
        action_taken=resolution.action_taken,
    )

    # TODO: Notify customer if resolution.notify_customer

    return feedback


@router.post("/{feedback_id}/escalate", response_model=CustomerFeedbackResponse)
def escalate_feedback(
    feedback_id: int,
    escalation: FeedbackEscalateSchema,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Escalate feedback to supervisor/manager

    Business Logic:
    - Marks feedback as escalated
    - Assigns to escalation handler
    - Records escalation reason
    - Updates priority
    - Sends escalation notification
    """
    feedback = customer_feedback.get(db, id=feedback_id)
    if not feedback or feedback.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

    if feedback.is_escalated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Feedback already escalated"
        )

    feedback = customer_feedback.escalate(
        db,
        feedback_id=feedback_id,
        escalated_to_id=escalation.escalated_to_id,
        reason=escalation.escalation_reason,
    )

    # Update priority
    feedback_update = CustomerFeedbackUpdate(priority=escalation.priority)
    feedback = customer_feedback.update(db, db_obj=feedback, obj_in=feedback_update)

    # TODO: Send escalation notification

    return feedback


@router.post("/{feedback_id}/close", response_model=CustomerFeedbackResponse)
def close_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Close feedback

    Business Logic:
    - Sets status to CLOSED
    - Final state - cannot be reopened
    - Archives feedback for reporting
    """
    feedback = customer_feedback.get(db, id=feedback_id)
    if not feedback or feedback.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

    if feedback.status == FeedbackStatus.CLOSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Feedback already closed"
        )

    feedback = customer_feedback.close(db, feedback_id=feedback_id)
    return feedback


@router.post("/{feedback_id}/schedule-followup", response_model=CustomerFeedbackResponse)
def schedule_followup(
    feedback_id: int,
    followup: FeedbackFollowupSchema,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Schedule follow-up for feedback

    Business Logic:
    - Sets follow-up date
    - Marks as requiring follow-up
    - Records follow-up notes
    - Creates reminder
    """
    feedback = customer_feedback.get(db, id=feedback_id)
    if not feedback or feedback.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

    feedback = customer_feedback.schedule_followup(
        db,
        feedback_id=feedback_id,
        followup_date=followup.followup_date,
        notes=followup.followup_notes,
    )
    return feedback


@router.post("/{feedback_id}/complete-followup", response_model=CustomerFeedbackResponse)
def complete_followup(
    feedback_id: int,
    notes: str = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Complete follow-up for feedback"""
    feedback = customer_feedback.get(db, id=feedback_id)
    if not feedback or feedback.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

    if not feedback.requires_followup:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Feedback does not require follow-up"
        )

    feedback = customer_feedback.complete_followup(db, feedback_id=feedback_id, notes=notes)
    return feedback


@router.get("/courier/{courier_id}/summary", response_model=FeedbackSummary)
def get_courier_feedback_summary(
    courier_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get feedback summary for a courier

    Returns:
    - Total feedbacks
    - Average rating
    - Sentiment distribution
    - Complaints count
    - Recent feedbacks
    """
    feedbacks = customer_feedback.get_by_courier(
        db, courier_id=courier_id, skip=0, limit=10, organization_id=current_org.id
    )
    all_feedbacks = customer_feedback.get_by_courier(
        db, courier_id=courier_id, skip=0, limit=1000, organization_id=current_org.id
    )

    total = len(all_feedbacks)
    avg_rating = customer_feedback.get_avg_rating_by_courier(
        db, courier_id=courier_id, organization_id=current_org.id
    )

    positive = len([f for f in all_feedbacks if f.overall_rating >= 4])
    neutral = len([f for f in all_feedbacks if f.overall_rating == 3])
    negative = len([f for f in all_feedbacks if f.overall_rating <= 2])
    complaints = len([f for f in all_feedbacks if f.is_complaint])

    return FeedbackSummary(
        subject_id=courier_id,
        subject_type="courier",
        total_feedbacks=total,
        avg_rating=avg_rating,
        positive_count=positive,
        neutral_count=neutral,
        negative_count=negative,
        complaints_count=complaints,
        recent_feedbacks=feedbacks,
    )


@router.get("/metrics", response_model=FeedbackMetrics)
def get_feedback_metrics(
    period: str = Query("month", pattern="^(week|month|quarter|year)$"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get feedback performance metrics

    Returns:
    - Total feedbacks
    - Average ratings
    - Response rate
    - Resolution rate
    - Escalation rate
    - Sentiment distribution
    - Top categories
    """
    # TODO: Implement comprehensive metrics calculation with organization_id filter
    # For now, return placeholder
    return FeedbackMetrics(
        period=period,
        total_feedbacks=0,
        avg_overall_rating=0.0,
        avg_delivery_speed_rating=0.0,
        avg_courier_behavior_rating=0.0,
        avg_package_condition_rating=0.0,
        avg_communication_rating=0.0,
        complaints_count=0,
        compliments_count=0,
        response_rate=0.0,
        avg_response_time_hours=0.0,
        resolution_rate=0.0,
        avg_resolution_satisfaction=0.0,
        escalation_rate=0.0,
        sentiment_distribution={},
        rating_distribution={},
        top_categories=[],
    )


# Feedback Template Endpoints
@router.get("/templates", response_model=List[FeedbackTemplateResponse])
def list_feedback_templates(
    feedback_type: FeedbackType = Query(None, description="Filter by type"),
    sentiment: FeedbackSentiment = Query(None, description="Filter by sentiment"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List all feedback response templates"""
    if feedback_type:
        templates = feedback_template.get_by_type(
            db, template_type=feedback_type, organization_id=current_org.id
        )
    elif sentiment:
        templates = feedback_template.get_by_sentiment(
            db, sentiment_type=sentiment, organization_id=current_org.id
        )
    else:
        templates = feedback_template.get_active_templates(db, organization_id=current_org.id)
    return templates


@router.post(
    "/templates", response_model=FeedbackTemplateResponse, status_code=status.HTTP_201_CREATED
)
def create_feedback_template(
    template_in: FeedbackTemplateCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Create a new feedback response template"""
    existing = feedback_template.get_by_code(
        db, template_code=template_in.template_code, organization_id=current_org.id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Template with code '{template_in.template_code}' already exists",
        )

    template = feedback_template.create(db, obj_in=template_in, organization_id=current_org.id)
    return template


@router.put("/templates/{template_id}", response_model=FeedbackTemplateResponse)
def update_feedback_template(
    template_id: int,
    template_in: FeedbackTemplateUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update a feedback template"""
    template = feedback_template.get(db, id=template_id)
    if not template or template.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    template = feedback_template.update(db, db_obj=template, obj_in=template_in)
    return template


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Delete a feedback template"""
    template = feedback_template.get(db, id=template_id)
    if not template or template.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    feedback_template.remove(db, id=template_id)
    return None
