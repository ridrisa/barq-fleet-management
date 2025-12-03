from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.crud.operations import dispatch_assignment as crud_dispatch
from app.schemas.operations.dispatch import (
    DispatchAssignmentCreate, DispatchAssignmentUpdate, DispatchAssignmentResponse,
    DispatchReassignment, DispatchAcceptance, CourierAvailability,
    DispatchRecommendation, DispatchMetrics
)
from app.core.database import get_db
from app.core.dependencies import get_current_user
from decimal import Decimal

router = APIRouter()


@router.get("/", response_model=List[DispatchAssignmentResponse])
def list_dispatch_assignments(
    skip: int = 0,
    limit: int = 100,
    courier_id: int = Query(None, description="Filter by courier"),
    zone_id: int = Query(None, description="Filter by zone"),
    status: str = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all dispatch assignments with optional filters"""
    if courier_id:
        assignments = crud_dispatch.get_by_courier(db, courier_id=courier_id, skip=skip, limit=limit)
    elif zone_id:
        assignments = crud_dispatch.get_by_zone(db, zone_id=zone_id, skip=skip, limit=limit)
    else:
        assignments = crud_dispatch.get_multi(db, skip=skip, limit=limit)
    return assignments


@router.get("/pending", response_model=List[DispatchAssignmentResponse])
def list_pending_assignments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all pending dispatch assignments ordered by priority

    Business Logic:
    - Returns unassigned deliveries
    - Sorted by priority (URGENT first) then creation time
    - Used by dispatch dashboard
    """
    assignments = crud_dispatch.get_pending(db, skip=skip, limit=limit)
    return assignments


@router.get("/{assignment_id}", response_model=DispatchAssignmentResponse)
def get_dispatch_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific dispatch assignment by ID"""
    assignment = crud_dispatch.get(db, id=assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispatch assignment not found"
        )
    return assignment


@router.post("/", response_model=DispatchAssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_dispatch_assignment(
    assignment_in: DispatchAssignmentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new dispatch assignment

    Business Logic:
    - Validates delivery exists and not already assigned
    - Auto-generates assignment number
    - If courier_id provided, assigns directly
    - If no courier_id, creates PENDING assignment
    - Calculates distance and estimated time if courier assigned
    - Checks courier current load and capacity
    """
    # TODO: Validate delivery exists
    # TODO: Check delivery not already assigned
    # TODO: If courier_id provided, validate courier availability
    # TODO: Calculate distance from courier to pickup
    # TODO: Get courier current load

    assignment = crud_dispatch.create_with_number(db, obj_in=assignment_in)

    # If courier assigned, update status
    if assignment_in.courier_id:
        # TODO: Get current user ID
        assigned_by_id = 1  # Placeholder
        assignment = crud_dispatch.assign_to_courier(
            db,
            assignment_id=assignment.id,
            courier_id=assignment_in.courier_id,
            assigned_by_id=assigned_by_id
        )

    return assignment


@router.put("/{assignment_id}", response_model=DispatchAssignmentResponse)
def update_dispatch_assignment(
    assignment_id: int,
    assignment_in: DispatchAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a dispatch assignment"""
    assignment = crud_dispatch.get(db, id=assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispatch assignment not found"
        )
    assignment = crud_dispatch.update(db, db_obj=assignment, obj_in=assignment_in)
    return assignment


@router.post("/{assignment_id}/assign", response_model=DispatchAssignmentResponse)
def assign_to_courier(
    assignment_id: int,
    courier_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Assign delivery to a specific courier

    Business Logic:
    - Validates courier exists and is available
    - Checks courier current load vs capacity
    - Calculates distance from courier to pickup
    - Estimates completion time
    - Updates status to ASSIGNED
    - Sends notification to courier
    """
    assignment = crud_dispatch.get(db, id=assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispatch assignment not found"
        )

    if assignment.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending assignments can be assigned"
        )

    # TODO: Validate courier availability
    # TODO: Check courier capacity
    # TODO: Calculate distance and time
    # TODO: Send notification

    # Get current user ID
    assigned_by_id = 1  # Placeholder

    assignment = crud_dispatch.assign_to_courier(
        db,
        assignment_id=assignment_id,
        courier_id=courier_id,
        assigned_by_id=assigned_by_id
    )

    return assignment


@router.post("/{assignment_id}/accept", response_model=DispatchAssignmentResponse)
def accept_assignment(
    assignment_id: int,
    acceptance: DispatchAcceptance,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Courier accepts or rejects assignment

    Business Logic:
    - If accepted: updates status to ACCEPTED, courier can start delivery
    - If rejected: updates status to REJECTED, goes back to pending pool
    - Records rejection reason for analytics
    - Increments rejection count
    """
    assignment = crud_dispatch.get(db, id=assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispatch assignment not found"
        )

    if assignment.status != "assigned":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only assigned deliveries can be accepted/rejected"
        )

    if acceptance.accepted:
        assignment = crud_dispatch.accept(db, assignment_id=assignment_id)
    else:
        if not acceptance.rejection_reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rejection reason is required"
            )
        assignment = crud_dispatch.reject(
            db,
            assignment_id=assignment_id,
            rejection_reason=acceptance.rejection_reason
        )

    return assignment


@router.post("/{assignment_id}/start", response_model=DispatchAssignmentResponse)
def start_delivery(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Start delivery execution

    Business Logic:
    - Updates status to IN_PROGRESS
    - Records start time
    - Begins real-time tracking
    """
    assignment = crud_dispatch.get(db, id=assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispatch assignment not found"
        )

    if assignment.status != "accepted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only accepted assignments can be started"
        )

    assignment = crud_dispatch.start(db, assignment_id=assignment_id)
    return assignment


@router.post("/{assignment_id}/complete", response_model=DispatchAssignmentResponse)
def complete_delivery(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Complete delivery assignment

    Business Logic:
    - Updates status to COMPLETED
    - Records completion time
    - Calculates actual duration
    - Calculates performance variance
    - Updates courier metrics
    - Frees courier capacity
    """
    assignment = crud_dispatch.get(db, id=assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispatch assignment not found"
        )

    if assignment.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only in-progress assignments can be completed"
        )

    assignment = crud_dispatch.complete(db, assignment_id=assignment_id)

    # TODO: Update courier metrics
    # TODO: Update zone metrics

    return assignment


@router.post("/{assignment_id}/reassign", response_model=DispatchAssignmentResponse)
def reassign_delivery(
    assignment_id: int,
    reassignment: DispatchReassignment,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Reassign delivery to different courier

    Business Logic:
    - Stores previous courier ID
    - Assigns to new courier
    - Records reassignment reason
    - Marks as reassignment
    - Notifies both couriers
    - Updates load for both couriers
    """
    assignment = crud_dispatch.get(db, id=assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispatch assignment not found"
        )

    # TODO: Validate new courier availability
    # TODO: Notify both couriers

    assignment = crud_dispatch.reassign(
        db,
        assignment_id=assignment_id,
        new_courier_id=reassignment.new_courier_id,
        reason=reassignment.reassignment_reason
    )

    return assignment


@router.get("/couriers/available", response_model=List[CourierAvailability])
def get_available_couriers(
    zone_id: int = Query(None, description="Filter by zone"),
    delivery_id: int = Query(None, description="Check for specific delivery"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of available couriers for dispatch

    Business Logic:
    - Returns couriers who are:
      - Status ACTIVE
      - Current load < max capacity
      - In specified zone (if provided)
    - Includes distance to pickup location
    - Includes current load and rating
    - Sorted by availability and proximity
    """
    # TODO: Implement courier availability logic
    # For now, return placeholder
    return []


@router.post("/recommend", response_model=DispatchRecommendation)
def get_dispatch_recommendation(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get AI-powered dispatch recommendation

    Business Logic:
    - Analyzes available couriers
    - Considers:
      - Distance to pickup
      - Current courier load
      - Courier rating
      - Historical performance
      - Zone coverage
    - Returns recommended courier with confidence score
    - Provides alternative couriers
    """
    # TODO: Implement AI recommendation algorithm
    # For now, return placeholder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Dispatch recommendation algorithm to be implemented"
    )


@router.get("/metrics", response_model=DispatchMetrics)
def get_dispatch_metrics(
    period: str = Query("today", regex="^(today|week|month)$"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get dispatch performance metrics

    Returns:
    - Total assignments
    - Success/rejection rates
    - Average assignment time
    - Average acceptance time
    - Reassignment rate
    - Average courier load
    - Zone coverage rate
    """
    # TODO: Implement metrics calculation
    return DispatchMetrics(
        period=period,
        total_assignments=0,
        successful_assignments=0,
        rejected_assignments=0,
        avg_assignment_time_seconds=0.0,
        avg_acceptance_time_seconds=0.0,
        reassignment_rate=0.0,
        avg_courier_load=0.0,
        zone_coverage_rate=0.0
    )
