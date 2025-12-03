import logging
from typing import List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.crud.operations import handover as crud_handover
from app.crud.fleet import courier as crud_courier
from app.crud.fleet import vehicle as crud_vehicle
from app.schemas.operations.handover import (
    HandoverCreate, HandoverUpdate, HandoverResponse,
    HandoverApproval, HandoverCompletion, HandoverHistory
)
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.fleet.courier import Courier
from app.models.fleet.vehicle import Vehicle
from app.models.fleet.assignment import CourierVehicleAssignment, AssignmentStatus
from app.models.operations.delivery import Delivery, DeliveryStatus

logger = logging.getLogger(__name__)

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

    # Validate from_courier exists
    from_courier = crud_courier.get(db, id=handover_in.from_courier_id)
    if not from_courier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"From courier with ID {handover_in.from_courier_id} not found"
        )

    # Validate to_courier exists
    to_courier = crud_courier.get(db, id=handover_in.to_courier_id)
    if not to_courier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"To courier with ID {handover_in.to_courier_id} not found"
        )

    # Validate vehicle exists (if vehicle handover)
    if handover_in.vehicle_id:
        vehicle = crud_vehicle.get(db, id=handover_in.vehicle_id)
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vehicle with ID {handover_in.vehicle_id} not found"
            )

        # Check vehicle is currently assigned to from_courier
        if from_courier.current_vehicle_id != handover_in.vehicle_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Vehicle {handover_in.vehicle_id} is not currently assigned to courier {handover_in.from_courier_id}"
            )

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
    return None


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
        approved_by_id = current_user.id
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

    # Update vehicle assignment if vehicle is part of handover
    if handover.vehicle_id:
        _update_vehicle_assignment(
            db=db,
            vehicle_id=handover.vehicle_id,
            from_courier_id=handover.from_courier_id,
            to_courier_id=handover.to_courier_id,
            mileage=completion.vehicle_mileage_start
        )

    # Transfer pending deliveries from from_courier to to_courier
    transferred_count = _transfer_pending_deliveries(
        db=db,
        from_courier_id=handover.from_courier_id,
        to_courier_id=handover.to_courier_id
    )

    # Send completion notification (log for now, can integrate with notification service)
    _send_handover_completion_notification(
        handover_number=handover.handover_number,
        from_courier_id=handover.from_courier_id,
        to_courier_id=handover.to_courier_id,
        vehicle_id=handover.vehicle_id,
        transferred_deliveries=transferred_count
    )

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


# ============================================================================
# Helper Functions for Handover Completion
# ============================================================================

def _update_vehicle_assignment(
    db: Session,
    vehicle_id: int,
    from_courier_id: int,
    to_courier_id: int,
    mileage: int = None
) -> None:
    """
    Update vehicle assignment from one courier to another.

    - Ends the current assignment for from_courier
    - Creates a new assignment for to_courier
    - Updates both couriers' current_vehicle_id
    """
    today = date.today()

    # End current assignment for from_courier
    current_assignment = db.query(CourierVehicleAssignment).filter(
        CourierVehicleAssignment.vehicle_id == vehicle_id,
        CourierVehicleAssignment.courier_id == from_courier_id,
        CourierVehicleAssignment.status == AssignmentStatus.ACTIVE
    ).first()

    if current_assignment:
        current_assignment.status = AssignmentStatus.COMPLETED
        current_assignment.end_date = today
        if mileage:
            current_assignment.end_mileage = mileage
        current_assignment.termination_reason = "Handover to another courier"
        db.add(current_assignment)

    # Create new assignment for to_courier
    new_assignment = CourierVehicleAssignment(
        courier_id=to_courier_id,
        vehicle_id=vehicle_id,
        start_date=today,
        start_mileage=mileage,
        assignment_reason="Vehicle handover",
        status=AssignmentStatus.ACTIVE
    )
    db.add(new_assignment)

    # Update couriers' current_vehicle_id
    from_courier = db.query(Courier).filter(Courier.id == from_courier_id).first()
    to_courier = db.query(Courier).filter(Courier.id == to_courier_id).first()

    if from_courier:
        from_courier.current_vehicle_id = None
        db.add(from_courier)

    if to_courier:
        to_courier.current_vehicle_id = vehicle_id
        db.add(to_courier)

    db.commit()

    logger.info(
        f"Vehicle assignment updated: Vehicle {vehicle_id} transferred from "
        f"Courier {from_courier_id} to Courier {to_courier_id}"
    )


def _transfer_pending_deliveries(
    db: Session,
    from_courier_id: int,
    to_courier_id: int
) -> int:
    """
    Transfer all pending and in-transit deliveries from one courier to another.

    Returns the count of transferred deliveries.
    """
    # Find all pending/in-transit deliveries for from_courier
    pending_deliveries = db.query(Delivery).filter(
        Delivery.courier_id == from_courier_id,
        Delivery.status.in_([DeliveryStatus.PENDING, DeliveryStatus.IN_TRANSIT])
    ).all()

    transferred_count = 0
    for delivery in pending_deliveries:
        delivery.courier_id = to_courier_id
        db.add(delivery)
        transferred_count += 1

    if transferred_count > 0:
        db.commit()
        logger.info(
            f"Transferred {transferred_count} deliveries from "
            f"Courier {from_courier_id} to Courier {to_courier_id}"
        )

    return transferred_count


def _send_handover_completion_notification(
    handover_number: str,
    from_courier_id: int,
    to_courier_id: int,
    vehicle_id: int = None,
    transferred_deliveries: int = 0
) -> None:
    """
    Send notification about completed handover.

    Currently logs the notification. Can be extended to integrate with:
    - Push notification service
    - SMS service
    - Email service
    - In-app notifications
    """
    notification_data = {
        "type": "handover_completed",
        "handover_number": handover_number,
        "from_courier_id": from_courier_id,
        "to_courier_id": to_courier_id,
        "vehicle_id": vehicle_id,
        "transferred_deliveries": transferred_deliveries
    }

    logger.info(
        f"Handover {handover_number} completed: "
        f"From Courier {from_courier_id} to Courier {to_courier_id}. "
        f"Vehicle: {vehicle_id or 'N/A'}, "
        f"Deliveries transferred: {transferred_deliveries}"
    )

    # TODO: Integrate with actual notification service when available
    # notification_service.send(
    #     recipients=[from_courier_id, to_courier_id],
    #     template="handover_completed",
    #     data=notification_data
    # )
