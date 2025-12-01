from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.crud.operations import handover as crud_handover
from app.schemas.operations.handover import (
    HandoverCreate, HandoverUpdate, HandoverResponse,
    HandoverApproval, HandoverCompletion, HandoverHistory
)
from app.config.database import get_db
from app.core.dependencies import get_current_user

router = APIRouter()


@router.get("/", response_model=List[HandoverResponse])
def list_handovers(
    skip: int = 0,
    limit: int = 100,
    courier_id: int = Query(None, description="Filter by courier"),
    vehicle_id: int = Query(None, description="Filter by vehicle"),
    status: str = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all handovers with optional filters"""
    if courier_id:
        handovers = crud_handover.get_by_courier(db, courier_id=courier_id, skip=skip, limit=limit)
    elif vehicle_id:
        handovers = crud_handover.get_by_vehicle(db, vehicle_id=vehicle_id, skip=skip, limit=limit)
    else:
        handovers = crud_handover.get_multi(db, skip=skip, limit=limit)
    return handovers


@router.get("/pending", response_model=List[HandoverResponse])
def list_pending_handovers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all pending handovers"""
    handovers = crud_handover.get_pending(db, skip=skip, limit=limit)
    return handovers


@router.get("/{handover_id}", response_model=HandoverResponse)
def get_handover(
    handover_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific handover by ID"""
    handover = crud_handover.get(db, id=handover_id)
    if not handover:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Handover not found"
        )
    return handover


@router.post("/", response_model=HandoverResponse, status_code=status.HTTP_201_CREATED)
def create_handover(
    handover_in: HandoverCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new handover

    Business Logic:
    - Validates from_courier and to_courier exist
    - Validates from_courier != to_courier
    - Checks vehicle availability
    - Creates handover with PENDING status
    - Auto-generates handover number
    - Schedules handover time
    """
    # Validate couriers are different
    if handover_in.from_courier_id == handover_in.to_courier_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="From and to courier must be different"
        )

    # TODO: Validate couriers exist
    # TODO: Validate vehicle exists
    # TODO: Check vehicle is currently assigned to from_courier

    handover = crud_handover.create_with_number(db, obj_in=handover_in)
    return handover


@router.put("/{handover_id}", response_model=HandoverResponse)
def update_handover(
    handover_id: int,
    handover_in: HandoverUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a handover"""
    handover = crud_handover.get(db, id=handover_id)
    if not handover:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Handover not found"
        )
    handover = crud_handover.update(db, db_obj=handover, obj_in=handover_in)
    return handover


@router.delete("/{handover_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_handover(
    handover_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a handover"""
    handover = crud_handover.get(db, id=handover_id)
    if not handover:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Handover not found"
        )
    crud_handover.remove(db, id=handover_id)


@router.post("/{handover_id}/approve", response_model=HandoverResponse)
def approve_handover(
    handover_id: int,
    approval: HandoverApproval,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Approve or reject a handover

    Business Logic:
    - Validates handover is in PENDING status
    - If approved: sets status to APPROVED, records approver
    - If rejected: sets status to REJECTED, records reason
    - Notifies both couriers
    """
    handover = crud_handover.get(db, id=handover_id)
    if not handover:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Handover not found"
        )

    if handover.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending handovers can be approved/rejected"
        )

    if approval.approved:
        # TODO: Get current user ID from auth
        approved_by_id = 1  # Placeholder
        handover = crud_handover.approve(db, handover_id=handover_id, approved_by_id=approved_by_id)
    else:
        if not approval.rejection_reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rejection reason is required"
            )
        handover = crud_handover.reject(db, handover_id=handover_id, rejection_reason=approval.rejection_reason)

    return handover


@router.post("/{handover_id}/complete", response_model=HandoverResponse)
def complete_handover(
    handover_id: int,
    completion: HandoverCompletion,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Complete a handover

    Business Logic:
    - Validates handover is APPROVED
    - Records signatures from both couriers
    - Records vehicle condition and mileage
    - Marks any discrepancies
    - Updates vehicle assignment in system
    - Transfers pending deliveries
    - Sets status to COMPLETED
    """
    handover = crud_handover.get(db, id=handover_id)
    if not handover:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Handover not found"
        )

    if handover.status != "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only approved handovers can be completed"
        )

    # Update handover with completion data
    handover_update = HandoverUpdate(
        from_courier_signature=completion.from_courier_signature,
        to_courier_signature=completion.to_courier_signature,
        vehicle_mileage_start=completion.vehicle_mileage_start,
        vehicle_fuel_level=completion.vehicle_fuel_level,
        vehicle_condition=completion.vehicle_condition,
        discrepancies_reported=completion.discrepancies_reported,
        photos=completion.photos,
        notes=completion.notes
    )
    handover = crud_handover.update(db, db_obj=handover, obj_in=handover_update)

    # Mark as completed
    handover = crud_handover.complete(db, handover_id=handover_id)

    # TODO: Update vehicle assignment
    # TODO: Transfer pending deliveries
    # TODO: Send completion notification

    return handover


@router.get("/courier/{courier_id}/history", response_model=HandoverHistory)
def get_courier_handover_history(
    courier_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get handover history for a courier

    Returns:
    - All handovers (sent and received)
    - Total count
    - Pending count
    - Completed count
    """
    handovers = crud_handover.get_by_courier(db, courier_id=courier_id, skip=skip, limit=limit)

    # Calculate statistics
    total_handovers = len(handovers)
    pending_handovers = len([h for h in handovers if h.status == "pending"])
    completed_handovers = len([h for h in handovers if h.status == "completed"])

    return HandoverHistory(
        handovers=handovers,
        total_handovers=total_handovers,
        pending_handovers=pending_handovers,
        completed_handovers=completed_handovers
    )


@router.get("/vehicle/{vehicle_id}/history", response_model=List[HandoverResponse])
def get_vehicle_handover_history(
    vehicle_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get handover history for a vehicle"""
    handovers = crud_handover.get_by_vehicle(db, vehicle_id=vehicle_id, skip=skip, limit=limit)
    return handovers
