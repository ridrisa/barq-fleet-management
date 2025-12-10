"""
Customer Feedback API Routes
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_organization, get_current_user
from app.models.tenant.organization import Organization
from app.models.operations.feedback import CustomerFeedback
from app.services.operations import customer_feedback_service, feedback_template_service, delivery_service
from app.services.fleet import courier_service
from app.services.user_service import user_service
from app.services.email_notification_service import email_notification_service, EmailRecipient
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

logger = logging.getLogger(__name__)


# Feedback Analysis Utilities
def analyze_sentiment(text: str, rating: int) -> FeedbackSentiment:
    """
    Analyze sentiment of feedback text using keyword-based analysis.
    Combines text analysis with overall rating for better accuracy.

    Args:
        text: The feedback text to analyze
        rating: The overall rating (1-5)

    Returns:
        FeedbackSentiment enum value
    """
    text_lower = text.lower()

    # Positive keywords
    positive_keywords = [
        'excellent', 'amazing', 'great', 'fantastic', 'wonderful', 'perfect',
        'best', 'love', 'thank', 'thanks', 'appreciate', 'happy', 'satisfied',
        'quick', 'fast', 'professional', 'friendly', 'helpful', 'awesome',
        'outstanding', 'exceptional', 'recommend', 'impressed', 'pleasant'
    ]

    # Negative keywords
    negative_keywords = [
        'terrible', 'horrible', 'awful', 'bad', 'worst', 'hate', 'angry',
        'disappointed', 'frustrat', 'poor', 'slow', 'late', 'damaged',
        'broken', 'rude', 'unprofessional', 'missing', 'lost', 'never',
        'wrong', 'complaint', 'refund', 'unacceptable', 'disgusting'
    ]

    # Count keyword matches
    positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
    negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)

    # Combine text analysis with rating
    # Rating: 1-2 = negative, 3 = neutral, 4-5 = positive
    rating_sentiment = 0 if rating <= 2 else (1 if rating == 3 else 2)

    # Text sentiment
    if negative_count > positive_count:
        text_sentiment = 0
    elif positive_count > negative_count:
        text_sentiment = 2
    else:
        text_sentiment = 1

    # Combined score
    combined_score = (rating_sentiment + text_sentiment) / 2

    if combined_score < 0.8:
        return FeedbackSentiment.NEGATIVE
    elif combined_score > 1.2:
        return FeedbackSentiment.POSITIVE
    else:
        return FeedbackSentiment.NEUTRAL


def auto_categorize_feedback(text: str, feedback_type: FeedbackType) -> str:
    """
    Auto-categorize feedback based on text content and feedback type.

    Args:
        text: The feedback text to analyze
        feedback_type: The type of feedback

    Returns:
        Category string
    """
    text_lower = text.lower()

    # Category keyword mappings
    category_keywords = {
        'delivery_speed': ['fast', 'slow', 'late', 'delay', 'time', 'quick', 'wait', 'early', 'on time'],
        'courier_behavior': ['rude', 'friendly', 'polite', 'professional', 'helpful', 'attitude', 'behavior', 'manner'],
        'package_handling': ['damaged', 'broken', 'condition', 'package', 'item', 'handling', 'careful', 'intact'],
        'communication': ['call', 'message', 'notify', 'update', 'inform', 'contact', 'respond', 'communication'],
        'pricing': ['price', 'cost', 'expensive', 'cheap', 'fee', 'charge', 'value', 'money'],
        'app_experience': ['app', 'website', 'interface', 'tracking', 'order', 'easy', 'difficult', 'navigation'],
        'customer_service': ['support', 'help', 'service', 'issue', 'problem', 'resolve', 'complaint', 'assistance'],
        'general': []
    }

    # Score each category
    category_scores = {}
    for category, keywords in category_keywords.items():
        if keywords:
            score = sum(1 for keyword in keywords if keyword in text_lower)
            category_scores[category] = score

    # Find best matching category
    if category_scores:
        best_category = max(category_scores, key=category_scores.get)
        if category_scores[best_category] > 0:
            return best_category

    # Default based on feedback type
    type_defaults = {
        FeedbackType.DELIVERY: 'delivery_speed',
        FeedbackType.COURIER: 'courier_behavior',
        FeedbackType.SERVICE: 'customer_service',
        FeedbackType.APP: 'app_experience',
        FeedbackType.SUPPORT: 'customer_service',
        FeedbackType.GENERAL: 'general'
    }

    return type_defaults.get(feedback_type, 'general')


def send_feedback_response_email(
    customer_email: str,
    customer_name: str,
    feedback_number: str,
    response_text: str
) -> bool:
    """
    Send email notification to customer when feedback is responded to.

    Args:
        customer_email: Customer email address
        customer_name: Customer name
        feedback_number: Feedback reference number
        response_text: The response text

    Returns:
        True if email sent successfully
    """
    if not customer_email:
        return False

    subject = f"Response to Your Feedback - {feedback_number}"
    html_content = f"""
    <html>
    <body>
        <h2>Thank You for Your Feedback</h2>
        <p>Dear {customer_name or 'Valued Customer'},</p>
        <p>Thank you for taking the time to share your feedback with us. We have reviewed your feedback (Reference: {feedback_number}) and would like to share our response:</p>
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p>{response_text}</p>
        </div>
        <p>We value your input as it helps us improve our service.</p>
        <p>Best regards,<br>BARQ Fleet Management Team</p>
    </body>
    </html>
    """

    try:
        return email_notification_service.send_email(
            to=EmailRecipient(email=customer_email, name=customer_name),
            subject=subject,
            html_content=html_content
        )
    except Exception as e:
        logger.error(f"Failed to send feedback response email: {e}")
        return False


def send_feedback_resolution_email(
    customer_email: str,
    customer_name: str,
    feedback_number: str,
    resolution_text: str,
    compensation_amount: float = 0,
    refund_amount: float = 0
) -> bool:
    """
    Send email notification to customer when feedback is resolved.

    Args:
        customer_email: Customer email address
        customer_name: Customer name
        feedback_number: Feedback reference number
        resolution_text: The resolution details
        compensation_amount: Compensation amount if any
        refund_amount: Refund amount if any

    Returns:
        True if email sent successfully
    """
    if not customer_email:
        return False

    compensation_section = ""
    if compensation_amount > 0 or refund_amount > 0:
        compensation_section = "<h3>Compensation Details:</h3><ul>"
        if refund_amount > 0:
            compensation_section += f"<li>Refund Amount: SAR {refund_amount:,.2f}</li>"
        if compensation_amount > 0:
            compensation_section += f"<li>Compensation Amount: SAR {compensation_amount:,.2f}</li>"
        compensation_section += "</ul>"

    subject = f"Your Feedback Has Been Resolved - {feedback_number}"
    html_content = f"""
    <html>
    <body>
        <h2>Feedback Resolution</h2>
        <p>Dear {customer_name or 'Valued Customer'},</p>
        <p>We are pleased to inform you that your feedback (Reference: {feedback_number}) has been resolved.</p>
        <h3>Resolution Details:</h3>
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p>{resolution_text}</p>
        </div>
        {compensation_section}
        <p>We apologize for any inconvenience and thank you for bringing this to our attention.</p>
        <p>If you have any further concerns, please don't hesitate to contact us.</p>
        <p>Best regards,<br>BARQ Fleet Management Team</p>
    </body>
    </html>
    """

    try:
        return email_notification_service.send_email(
            to=EmailRecipient(email=customer_email, name=customer_name),
            subject=subject,
            html_content=html_content
        )
    except Exception as e:
        logger.error(f"Failed to send feedback resolution email: {e}")
        return False


def send_escalation_notification(
    escalated_to_email: str,
    escalated_to_name: str,
    feedback_number: str,
    feedback_text: str,
    escalation_reason: str,
    customer_name: str,
    priority: str
) -> bool:
    """
    Send email notification to the person receiving the escalation.

    Args:
        escalated_to_email: Email of person receiving escalation
        escalated_to_name: Name of person receiving escalation
        feedback_number: Feedback reference number
        feedback_text: Original feedback text
        escalation_reason: Reason for escalation
        customer_name: Customer name
        priority: Priority level

    Returns:
        True if email sent successfully
    """
    if not escalated_to_email:
        return False

    priority_color = {
        'urgent': 'red',
        'high': 'orange',
        'normal': 'blue'
    }.get(priority, 'blue')

    subject = f"[{priority.upper()}] Feedback Escalated - {feedback_number}"
    html_content = f"""
    <html>
    <body>
        <h2 style="color: {priority_color};">Escalated Feedback Requires Your Attention</h2>
        <p>Dear {escalated_to_name or 'Team'},</p>
        <p>A customer feedback has been escalated to you for review and action.</p>

        <h3>Feedback Details:</h3>
        <ul>
            <li><strong>Reference:</strong> {feedback_number}</li>
            <li><strong>Customer:</strong> {customer_name or 'Not provided'}</li>
            <li><strong>Priority:</strong> <span style="color: {priority_color}; font-weight: bold;">{priority.upper()}</span></li>
        </ul>

        <h3>Original Feedback:</h3>
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0;">
            <p>{feedback_text[:500]}{'...' if len(feedback_text) > 500 else ''}</p>
        </div>

        <h3>Escalation Reason:</h3>
        <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 10px 0;">
            <p>{escalation_reason}</p>
        </div>

        <p>Please review and take appropriate action as soon as possible.</p>
        <p>Best regards,<br>BARQ Fleet Management System</p>
    </body>
    </html>
    """

    try:
        return email_notification_service.send_email(
            to=EmailRecipient(email=escalated_to_email, name=escalated_to_name),
            subject=subject,
            html_content=html_content
        )
    except Exception as e:
        logger.error(f"Failed to send escalation notification: {e}")
        return False

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
        feedbacks = customer_feedback_service.get_by_type(
            db, feedback_type=feedback_type, skip=skip, limit=limit, organization_id=current_org.id
        )
    elif courier_id:
        feedbacks = customer_feedback_service.get_by_courier(
            db, courier_id=courier_id, skip=skip, limit=limit, organization_id=current_org.id
        )
    elif delivery_id:
        feedbacks = customer_feedback_service.get_by_delivery(
            db, delivery_id=delivery_id, organization_id=current_org.id
        )
    elif is_complaint:
        feedbacks = customer_feedback_service.get_complaints(
            db, skip=skip, limit=limit, organization_id=current_org.id
        )
    else:
        feedbacks = customer_feedback_service.get_multi(
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
    feedbacks = customer_feedback_service.get_pending(
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
    feedbacks = customer_feedback_service.get_negative_feedbacks(
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
    feedbacks = customer_feedback_service.get_escalated(
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
    feedbacks = customer_feedback_service.get_requiring_followup(db, organization_id=current_org.id)
    return feedbacks


@router.get("/{feedback_id}", response_model=CustomerFeedbackResponse)
def get_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get a specific feedback by ID"""
    feedback = customer_feedback_service.get(db, id=feedback_id)
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
    # Validate delivery exists if delivery_id provided
    if feedback_in.delivery_id:
        delivery = delivery_service.get(db, id=feedback_in.delivery_id)
        if not delivery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Delivery with id {feedback_in.delivery_id} not found"
            )

    # Validate courier exists if courier_id provided
    if feedback_in.courier_id:
        courier = courier_service.get(db, id=feedback_in.courier_id)
        if not courier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Courier with id {feedback_in.courier_id} not found"
            )

    # Create feedback first
    feedback = customer_feedback_service.create_with_number(
        db, obj_in=feedback_in, organization_id=current_org.id
    )

    # AI sentiment analysis
    sentiment = analyze_sentiment(feedback_in.feedback_text, feedback_in.overall_rating)
    feedback.sentiment = sentiment

    # Auto-categorization (only if category not provided)
    if not feedback_in.category:
        category = auto_categorize_feedback(feedback_in.feedback_text, feedback_in.feedback_type)
        feedback.category = category

    # Mark as complaint if negative sentiment or low rating
    if sentiment == FeedbackSentiment.NEGATIVE or feedback_in.overall_rating <= 2:
        feedback.is_complaint = True

    # Mark as compliment if positive sentiment and high rating
    if sentiment == FeedbackSentiment.POSITIVE and feedback_in.overall_rating >= 4:
        feedback.is_compliment = True

    db.add(feedback)
    db.commit()
    db.refresh(feedback)

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
    feedback = customer_feedback_service.get(db, id=feedback_id)
    if not feedback or feedback.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    feedback = customer_feedback_service.update(db, db_obj=feedback, obj_in=feedback_in)
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
    feedback = customer_feedback_service.get(db, id=feedback_id)
    if not feedback or feedback.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

    if feedback.status == FeedbackStatus.CLOSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot respond to closed feedback"
        )

    # Use template if specified
    response_text = response_data.response_text
    if response_data.use_template:
        template = feedback_template_service.get_by_code(db, template_code=response_data.use_template)
        if template:
            response_text = template.body
            feedback_template_service.increment_usage(db, template_id=template.id)

    # Get current user ID
    responded_by_id = current_user.id if hasattr(current_user, "id") else 1

    feedback = customer_feedback_service.respond(
        db, feedback_id=feedback_id, response_text=response_text, responded_by_id=responded_by_id
    )

    # Update internal notes if provided
    if response_data.internal_notes:
        feedback.internal_notes = response_data.internal_notes
        db.add(feedback)
        db.commit()
        db.refresh(feedback)

    # Send email if configured
    if response_data.send_email and feedback.customer_email:
        send_feedback_response_email(
            customer_email=feedback.customer_email,
            customer_name=feedback.customer_name,
            feedback_number=feedback.feedback_number,
            response_text=response_text
        )

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
    feedback = customer_feedback_service.get(db, id=feedback_id)
    if not feedback or feedback.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

    if feedback.status == FeedbackStatus.CLOSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot resolve closed feedback"
        )

    # Get current user ID
    resolved_by_id = current_user.id if hasattr(current_user, "id") else 1

    feedback = customer_feedback_service.resolve(
        db,
        feedback_id=feedback_id,
        resolution_text=resolution.resolution_text,
        resolved_by_id=resolved_by_id,
        compensation_amount=float(resolution.compensation_amount or 0),
        refund_amount=float(resolution.refund_amount or 0),
        action_taken=resolution.action_taken,
    )

    # Notify customer if resolution.notify_customer is enabled
    if resolution.notify_customer and feedback.customer_email:
        send_feedback_resolution_email(
            customer_email=feedback.customer_email,
            customer_name=feedback.customer_name,
            feedback_number=feedback.feedback_number,
            resolution_text=resolution.resolution_text,
            compensation_amount=float(resolution.compensation_amount or 0),
            refund_amount=float(resolution.refund_amount or 0)
        )

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
    feedback = customer_feedback_service.get(db, id=feedback_id)
    if not feedback or feedback.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

    if feedback.is_escalated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Feedback already escalated"
        )

    feedback = customer_feedback_service.escalate(
        db,
        feedback_id=feedback_id,
        escalated_to_id=escalation.escalated_to_id,
        reason=escalation.escalation_reason,
    )

    # Update priority
    feedback_update = CustomerFeedbackUpdate(priority=escalation.priority)
    feedback = customer_feedback_service.update(db, db_obj=feedback, obj_in=feedback_update)

    # Send escalation notification to the assigned person
    escalated_user = user_service.get(db, id=escalation.escalated_to_id)
    if escalated_user and escalated_user.email:
        send_escalation_notification(
            escalated_to_email=escalated_user.email,
            escalated_to_name=escalated_user.full_name,
            feedback_number=feedback.feedback_number,
            feedback_text=feedback.feedback_text,
            escalation_reason=escalation.escalation_reason,
            customer_name=feedback.customer_name,
            priority=escalation.priority
        )

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
    feedback = customer_feedback_service.get(db, id=feedback_id)
    if not feedback or feedback.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

    if feedback.status == FeedbackStatus.CLOSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Feedback already closed"
        )

    feedback = customer_feedback_service.close(db, feedback_id=feedback_id)
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
    feedback = customer_feedback_service.get(db, id=feedback_id)
    if not feedback or feedback.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

    feedback = customer_feedback_service.schedule_followup(
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
    feedback = customer_feedback_service.get(db, id=feedback_id)
    if not feedback or feedback.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

    if not feedback.requires_followup:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Feedback does not require follow-up"
        )

    feedback = customer_feedback_service.complete_followup(db, feedback_id=feedback_id, notes=notes)
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
    feedbacks = customer_feedback_service.get_by_courier(
        db, courier_id=courier_id, skip=0, limit=10, organization_id=current_org.id
    )
    all_feedbacks = customer_feedback_service.get_by_courier(
        db, courier_id=courier_id, skip=0, limit=1000, organization_id=current_org.id
    )

    total = len(all_feedbacks)
    avg_rating = customer_feedback_service.get_avg_rating_by_courier(
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
    # Calculate date range based on period
    now = datetime.utcnow()
    if period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    elif period == "quarter":
        start_date = now - timedelta(days=90)
    else:  # year
        start_date = now - timedelta(days=365)

    # Base query with organization and date filters
    base_query = db.query(CustomerFeedback).filter(
        CustomerFeedback.organization_id == current_org.id,
        CustomerFeedback.submitted_at >= start_date
    )

    # Get all feedbacks in period
    feedbacks = base_query.all()
    total_feedbacks = len(feedbacks)

    if total_feedbacks == 0:
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
            sentiment_distribution={"positive": 0, "neutral": 0, "negative": 0},
            rating_distribution={"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
            top_categories=[],
        )

    # Calculate average ratings
    overall_ratings = [f.overall_rating for f in feedbacks if f.overall_rating]
    delivery_speed_ratings = [f.delivery_speed_rating for f in feedbacks if f.delivery_speed_rating]
    courier_behavior_ratings = [f.courier_behavior_rating for f in feedbacks if f.courier_behavior_rating]
    package_condition_ratings = [f.package_condition_rating for f in feedbacks if f.package_condition_rating]
    communication_ratings = [f.communication_rating for f in feedbacks if f.communication_rating]

    avg_overall_rating = sum(overall_ratings) / len(overall_ratings) if overall_ratings else 0.0
    avg_delivery_speed = sum(delivery_speed_ratings) / len(delivery_speed_ratings) if delivery_speed_ratings else 0.0
    avg_courier_behavior = sum(courier_behavior_ratings) / len(courier_behavior_ratings) if courier_behavior_ratings else 0.0
    avg_package_condition = sum(package_condition_ratings) / len(package_condition_ratings) if package_condition_ratings else 0.0
    avg_communication = sum(communication_ratings) / len(communication_ratings) if communication_ratings else 0.0

    # Count complaints and compliments
    complaints_count = sum(1 for f in feedbacks if f.is_complaint)
    compliments_count = sum(1 for f in feedbacks if f.is_compliment)

    # Calculate response rate and average response time
    responded_feedbacks = [f for f in feedbacks if f.responded_at]
    response_rate = (len(responded_feedbacks) / total_feedbacks * 100) if total_feedbacks > 0 else 0.0

    response_times = [f.response_time_hours for f in responded_feedbacks if f.response_time_hours]
    avg_response_time = sum(float(rt) for rt in response_times) / len(response_times) if response_times else 0.0

    # Calculate resolution rate and satisfaction
    resolved_feedbacks = [f for f in feedbacks if f.status in [FeedbackStatus.RESOLVED, FeedbackStatus.CLOSED]]
    resolution_rate = (len(resolved_feedbacks) / total_feedbacks * 100) if total_feedbacks > 0 else 0.0

    resolution_satisfactions = [f.resolution_satisfaction for f in resolved_feedbacks if f.resolution_satisfaction]
    avg_resolution_satisfaction = (
        sum(resolution_satisfactions) / len(resolution_satisfactions)
        if resolution_satisfactions else 0.0
    )

    # Calculate escalation rate
    escalated_feedbacks = [f for f in feedbacks if f.is_escalated]
    escalation_rate = (len(escalated_feedbacks) / total_feedbacks * 100) if total_feedbacks > 0 else 0.0

    # Sentiment distribution
    sentiment_distribution = {
        "positive": sum(1 for f in feedbacks if f.sentiment == FeedbackSentiment.POSITIVE),
        "neutral": sum(1 for f in feedbacks if f.sentiment == FeedbackSentiment.NEUTRAL),
        "negative": sum(1 for f in feedbacks if f.sentiment == FeedbackSentiment.NEGATIVE),
    }

    # Rating distribution
    rating_distribution = {
        "1": sum(1 for f in feedbacks if f.overall_rating == 1),
        "2": sum(1 for f in feedbacks if f.overall_rating == 2),
        "3": sum(1 for f in feedbacks if f.overall_rating == 3),
        "4": sum(1 for f in feedbacks if f.overall_rating == 4),
        "5": sum(1 for f in feedbacks if f.overall_rating == 5),
    }

    # Top categories
    category_counts: Dict[str, int] = {}
    for f in feedbacks:
        if f.category:
            category_counts[f.category] = category_counts.get(f.category, 0) + 1

    top_categories = sorted(
        [{"category": k, "count": v} for k, v in category_counts.items()],
        key=lambda x: x["count"],
        reverse=True
    )[:10]

    return FeedbackMetrics(
        period=period,
        total_feedbacks=total_feedbacks,
        avg_overall_rating=round(avg_overall_rating, 2),
        avg_delivery_speed_rating=round(avg_delivery_speed, 2),
        avg_courier_behavior_rating=round(avg_courier_behavior, 2),
        avg_package_condition_rating=round(avg_package_condition, 2),
        avg_communication_rating=round(avg_communication, 2),
        complaints_count=complaints_count,
        compliments_count=compliments_count,
        response_rate=round(response_rate, 2),
        avg_response_time_hours=round(avg_response_time, 2),
        resolution_rate=round(resolution_rate, 2),
        avg_resolution_satisfaction=round(avg_resolution_satisfaction, 2),
        escalation_rate=round(escalation_rate, 2),
        sentiment_distribution=sentiment_distribution,
        rating_distribution=rating_distribution,
        top_categories=top_categories,
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
        templates = feedback_template_service.get_by_type(
            db, template_type=feedback_type, organization_id=current_org.id
        )
    elif sentiment:
        templates = feedback_template_service.get_by_sentiment(
            db, sentiment_type=sentiment, organization_id=current_org.id
        )
    else:
        templates = feedback_template_service.get_active_templates(db, organization_id=current_org.id)
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
    existing = feedback_template_service.get_by_code(
        db, template_code=template_in.template_code, organization_id=current_org.id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Template with code '{template_in.template_code}' already exists",
        )

    template = feedback_template_service.create(db, obj_in=template_in, organization_id=current_org.id)
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
    template = feedback_template_service.get(db, id=template_id)
    if not template or template.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    template = feedback_template_service.update(db, db_obj=template, obj_in=template_in)
    return template


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Delete a feedback template"""
    template = feedback_template_service.get(db, id=template_id)
    if not template or template.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    feedback_template_service.remove(db, id=template_id)
    return None
