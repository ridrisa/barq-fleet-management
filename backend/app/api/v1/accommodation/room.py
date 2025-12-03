"""Room Management API Routes"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.accommodation import (
    RoomCreate, RoomUpdate, RoomResponse, RoomStatus
)
from app.services.accommodation import room_service, building_service, bed_service


router = APIRouter()


@router.get("/", response_model=List[RoomResponse])
def get_rooms(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    building_id: Optional[int] = None,
    status: Optional[RoomStatus] = None,
    available_only: bool = False,
    current_user: User = Depends(get_current_user),
):
    """
    Get list of rooms with filtering

    Filters:
    - building_id: Filter by building ID
    - status: Filter by room status (available, occupied, maintenance)
    - available_only: Show only rooms with free beds
    """
    if available_only:
        return room_service.get_available(
            db, building_id=building_id, skip=skip, limit=limit
        )

    if building_id:
        return room_service.get_by_building(
            db, building_id=building_id, skip=skip, limit=limit
        )

    if status:
        return room_service.get_by_status(
            db, status=status, skip=skip, limit=limit
        )

    return room_service.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(
    room_in: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new room"""
    # Verify building exists
    building = building_service.get(db, id=room_in.building_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    # Check if room number already exists in this building
    existing = room_service.get_by_room_number(
        db, building_id=room_in.building_id, room_number=room_in.room_number
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Room '{room_in.room_number}' already exists in this building"
        )

    room = room_service.create(db, obj_in=room_in)

    # Update building statistics
    building_service.update_building_stats(db, building_id=room_in.building_id)

    return room


@router.get("/{room_id}", response_model=RoomResponse)
def get_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get room by ID"""
    room = room_service.get(db, id=room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.put("/{room_id}", response_model=RoomResponse)
def update_room(
    room_id: int,
    room_in: RoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update room"""
    room = room_service.get(db, id=room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # If building_id is being updated, verify new building exists
    if room_in.building_id and room_in.building_id != room.building_id:
        building = building_service.get(db, id=room_in.building_id)
        if not building:
            raise HTTPException(status_code=404, detail="Building not found")

    # Check if room number conflicts
    if room_in.room_number and room_in.room_number != room.room_number:
        building_id = room_in.building_id or room.building_id
        existing = room_service.get_by_room_number(
            db, building_id=building_id, room_number=room_in.room_number
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Room '{room_in.room_number}' already exists in this building"
            )

    old_building_id = room.building_id
    updated_room = room_service.update(db, db_obj=room, obj_in=room_in)

    # Update building statistics for both old and new buildings if changed
    building_service.update_building_stats(db, building_id=old_building_id)
    if room_in.building_id and room_in.building_id != old_building_id:
        building_service.update_building_stats(db, building_id=room_in.building_id)

    return updated_room


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete room"""
    room = room_service.get(db, id=room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Check if room has beds
    beds = bed_service.get_by_room(db, room_id=room_id, limit=1)
    if beds:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete room with existing beds. Delete beds first."
        )

    building_id = room.building_id
    room_service.delete(db, id=room_id)

    # Update building statistics
    building_service.update_building_stats(db, building_id=building_id)

    return None


@router.post("/{room_id}/update-occupancy", response_model=RoomResponse)
def update_room_occupancy(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Recalculate and update room occupancy

    Updates occupied count based on current bed allocations
    """
    room = room_service.update_occupancy(db, room_id=room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    return room


@router.get("/statistics/all", response_model=dict)
def get_room_statistics(
    building_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get room statistics

    Returns:
    - total_rooms: Total number of rooms
    - available_rooms: Rooms with available capacity
    - occupied_rooms: Fully occupied rooms
    - maintenance_rooms: Rooms under maintenance
    - total_capacity: Total bed capacity
    - total_occupied: Total occupied beds
    - occupancy_rate: Percentage of occupied beds
    """
    return room_service.get_statistics(db, building_id=building_id)
