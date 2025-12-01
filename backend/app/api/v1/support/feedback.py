"""Customer Feedback API Routes"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.support import FeedbackCategory, FeedbackStatus
from app.schemas.support import (
    FeedbackCreate, FeedbackUpdate, FeedbackResponse,
    FeedbackList, FeedbackRespond, FeedbackStatistics
)
from app.services.support import feedback_service


router = APIRouter()


@router.get("/", response_model=List[FeedbackList])
def get_feedbacks(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[FeedbackCategory] = None,
    status_filter: Optional[FeedbackStatus] = Query(None, alias="status"),
    rating: Optional[int] = Query(None, ge=1, le=5),
    current_user: User = Depends(get_current_user),
):
    """
    Get list of feedback

    Filters:
    - category: Filter by feedback category
    - status: Filter by feedback status
    - rating: Filter by rating (1-5)
    """
    if category:
        return feedback_service.get_by_category(
            db,
            category=category,
            skip=skip,
            limit=limit
        )

    if status_filter:
        return feedback_service.get_by_status(
            db,
            status=status_filter,
            skip=skip,
            limit=limit
        )

    if rating:
        return feedback_service.get_by_rating(
            db,
            rating=rating,
            skip=skip,
            limit=limit
        )

    return feedback_service.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    feedback_in: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit customer feedback"""
    return feedback_service.create(db, obj_in=feedback_in)


@router.get("/statistics", response_model=FeedbackStatistics)
def get_feedback_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get feedback statistics"""
    return feedback_service.get_statistics(db)


@router.get("/positive", response_model=List[FeedbackList])
def get_positive_feedback(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get positive feedback (4-5 stars)"""
    return feedback_service.get_positive_feedback(db, skip=skip, limit=limit)


@router.get("/negative", response_model=List[FeedbackList])
def get_negative_feedback(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get negative feedback (1-2 stars)"""
    return feedback_service.get_negative_feedback(db, skip=skip, limit=limit)


@router.get("/{feedback_id}", response_model=FeedbackResponse)
def get_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get feedback by ID"""
    feedback = feedback_service.get(db, id=feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    return feedback


@router.put("/{feedback_id}", response_model=FeedbackResponse)
def update_feedback(
    feedback_id: int,
    feedback_in: FeedbackUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update feedback"""
    feedback = feedback_service.get(db, id=feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    return feedback_service.update(db, db_obj=feedback, obj_in=feedback_in)


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete feedback"""
    feedback = feedback_service.get(db, id=feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    feedback_service.remove(db, id=feedback_id)


@router.post("/{feedback_id}/respond", response_model=FeedbackResponse)
def respond_to_feedback(
    feedback_id: int,
    respond_data: FeedbackRespond,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Respond to customer feedback"""
    feedback = feedback_service.respond_to_feedback(
        db,
        feedback_id=feedback_id,
        response=respond_data.response,
        responded_by=current_user.id
    )
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    return feedback
