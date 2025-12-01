"""Bed Management API Routes"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.accommodation import (
    BedCreate, BedUpdate, BedResponse, BedStatus
)
from app.services.accommodation import bed_service, room_service


router = APIRouter()


@router.get("/", response_model=List[BedResponse])
def get_beds(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    room_id: Optional[int] = None,
    status: Optional[BedStatus] = None,
    available_only: bool = False,
    current_user: User = Depends(get_current_user),
):
    """
    Get list of beds with filtering

    Filters:
    - room_id: Filter by room ID
    - status: Filter by bed status (available, occupied, reserved)
    - available_only: Show only available beds
    """
    if available_only:
        return bed_service.get_available(
            db, room_id=room_id, skip=skip, limit=limit
        )

    if room_id:
        return bed_service.get_by_room(
            db, room_id=room_id, skip=skip, limit=limit
        )

    if status:
        return bed_service.get_by_status(
            db, status=status, skip=skip, limit=limit
        )

    return bed_service.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=BedResponse, status_code=status.HTTP_201_CREATED)
def create_bed(
    bed_in: BedCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new bed"""
    # Verify room exists
    room = room_service.get(db, id=bed_in.room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Check if bed number already exists in this room
    existing = bed_service.get_by_bed_number(
        db, room_id=bed_in.room_id, bed_number=bed_in.bed_number
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Bed number {bed_in.bed_number} already exists in this room"
        )

    bed = bed_service.create(db, obj_in=bed_in)

    # Update room occupancy
    room_service.update_occupancy(db, room_id=bed_in.room_id)

    return bed


@router.get("/{bed_id}", response_model=BedResponse)
def get_bed(
    bed_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get bed by ID"""
    bed = bed_service.get(db, id=bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail="Bed not found")
    return bed


@router.put("/{bed_id}", response_model=BedResponse)
def update_bed(
    bed_id: int,
    bed_in: BedUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update bed"""
    bed = bed_service.get(db, id=bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail="Bed not found")

    # If room_id is being updated, verify new room exists
    if bed_in.room_id and bed_in.room_id != bed.room_id:
        room = room_service.get(db, id=bed_in.room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")

    # Check if bed number conflicts
    if bed_in.bed_number and bed_in.bed_number != bed.bed_number:
        room_id = bed_in.room_id or bed.room_id
        existing = bed_service.get_by_bed_number(
            db, room_id=room_id, bed_number=bed_in.bed_number
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Bed number {bed_in.bed_number} already exists in this room"
            )

    old_room_id = bed.room_id
    updated_bed = bed_service.update(db, db_obj=bed, obj_in=bed_in)

    # Update room occupancy for both old and new rooms if changed
    room_service.update_occupancy(db, room_id=old_room_id)
    if bed_in.room_id and bed_in.room_id != old_room_id:
        room_service.update_occupancy(db, room_id=bed_in.room_id)

    return updated_bed


@router.delete("/{bed_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bed(
    bed_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete bed"""
    bed = bed_service.get(db, id=bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail="Bed not found")

    # Check if bed is currently allocated
    if bed.status == BedStatus.OCCUPIED:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete occupied bed. Release allocation first."
        )

    room_id = bed.room_id
    bed_service.delete(db, id=bed_id)

    # Update room occupancy
    room_service.update_occupancy(db, room_id=room_id)

    return None


@router.post("/{bed_id}/reserve", response_model=BedResponse)
def reserve_bed(
    bed_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Reserve a bed

    Changes bed status from available to reserved
    """
    bed = bed_service.reserve_bed(db, bed_id=bed_id)
    if not bed:
        raise HTTPException(
            status_code=400,
            detail="Bed not found or not available for reservation"
        )

    return bed


@router.post("/{bed_id}/release", response_model=BedResponse)
def release_bed(
    bed_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Release a bed

    Changes bed status to available
    """
    bed = bed_service.release_bed(db, bed_id=bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail="Bed not found")

    # Update room occupancy
    room_service.update_occupancy(db, room_id=bed.room_id)

    return bed


@router.get("/statistics/all", response_model=dict)
def get_bed_statistics(
    room_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get bed statistics

    Returns:
    - total_beds: Total number of beds
    - available: Available beds
    - occupied: Occupied beds
    - reserved: Reserved beds
    - availability_rate: Percentage of available beds
    """
    return bed_service.get_statistics(db, room_id=room_id)
