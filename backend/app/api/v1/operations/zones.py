from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.crud.operations import zone as crud_zone
from app.schemas.operations.zone import (
    ZoneCreate, ZoneUpdate, ZoneResponse, ZoneMetrics
)
from app.config.database import get_db
from app.core.dependencies import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ZoneResponse])
def list_zones(
    skip: int = 0,
    limit: int = 100,
    city: str = Query(None, description="Filter by city"),
    status: str = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all zones with optional filters"""
    if city:
        zones = crud_zone.get_by_city(db, city=city, skip=skip, limit=limit)
    elif status == "active":
        zones = crud_zone.get_active_zones(db, skip=skip, limit=limit)
    else:
        zones = crud_zone.get_multi(db, skip=skip, limit=limit)
    return zones


@router.get("/at-capacity", response_model=List[ZoneResponse])
def list_zones_at_capacity(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List zones at or near capacity

    Business Logic:
    - Returns zones where current_couriers >= max_couriers
    - Used for load balancing decisions
    - Helps identify zones needing additional resources
    """
    zones = crud_zone.get_at_capacity(db)
    return zones


@router.get("/{zone_id}", response_model=ZoneResponse)
def get_zone(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific zone by ID"""
    zone = crud_zone.get(db, id=zone_id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone not found"
        )
    return zone


@router.get("/code/{zone_code}", response_model=ZoneResponse)
def get_zone_by_code(
    zone_code: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get zone by unique code"""
    zone = crud_zone.get_by_code(db, zone_code=zone_code)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone not found"
        )
    return zone


@router.post("/", response_model=ZoneResponse, status_code=status.HTTP_201_CREATED)
def create_zone(
    zone_in: ZoneCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new delivery zone

    Business Logic:
    - Validates zone code is unique
    - Validates GeoJSON boundaries if provided
    - Initializes performance metrics to 0
    - Sets status to ACTIVE by default
    """
    # Check if zone code already exists
    existing_zone = crud_zone.get_by_code(db, zone_code=zone_in.zone_code)
    if existing_zone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Zone with code '{zone_in.zone_code}' already exists"
        )

    # TODO: Validate GeoJSON boundaries
    # TODO: Calculate coverage area from boundaries

    zone = crud_zone.create(db, obj_in=zone_in)
    return zone


@router.put("/{zone_id}", response_model=ZoneResponse)
def update_zone(
    zone_id: int,
    zone_in: ZoneUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a zone"""
    zone = crud_zone.get(db, id=zone_id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone not found"
        )
    zone = crud_zone.update(db, db_obj=zone, obj_in=zone_in)
    return zone


@router.delete("/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_zone(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a zone

    Business Logic:
    - Validates no active couriers in zone
    - Validates no pending deliveries in zone
    - Soft delete or hard delete based on business rules
    """
    zone = crud_zone.get(db, id=zone_id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone not found"
        )

    # Check if zone has active couriers
    if zone.current_couriers > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete zone with active couriers"
        )

    crud_zone.remove(db, id=zone_id)


@router.get("/{zone_id}/metrics", response_model=ZoneMetrics)
def get_zone_metrics(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get zone performance metrics

    Returns:
    - Current courier count and utilization
    - Average delivery time
    - Success rate
    - Total deliveries completed
    - Capacity status
    """
    zone = crud_zone.get(db, id=zone_id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone not found"
        )

    # Calculate utilization rate
    utilization_rate = zone.utilization_rate if hasattr(zone, 'utilization_rate') else 0.0

    metrics = ZoneMetrics(
        zone_id=zone.id,
        zone_code=zone.zone_code,
        zone_name=zone.zone_name,
        current_couriers=zone.current_couriers,
        max_couriers=zone.max_couriers,
        utilization_rate=utilization_rate,
        avg_delivery_time_minutes=zone.avg_delivery_time_minutes or 0.0,
        total_deliveries_today=0,  # TODO: Calculate from deliveries
        success_rate=zone.success_rate or 0.0,
        is_at_capacity=zone.is_at_capacity if hasattr(zone, 'is_at_capacity') else False
    )

    return metrics


@router.post("/{zone_id}/couriers/increment", response_model=ZoneResponse)
def increment_courier_count(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Increment zone courier count

    Business Logic:
    - Called when courier enters zone
    - Validates capacity not exceeded
    - Updates current_couriers count
    """
    zone = crud_zone.get(db, id=zone_id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone not found"
        )

    if zone.current_couriers >= zone.max_couriers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Zone is at maximum capacity"
        )

    zone = crud_zone.increment_courier_count(db, zone_id=zone_id)
    return zone


@router.post("/{zone_id}/couriers/decrement", response_model=ZoneResponse)
def decrement_courier_count(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Decrement zone courier count

    Business Logic:
    - Called when courier leaves zone
    - Updates current_couriers count
    - Prevents negative count
    """
    zone = crud_zone.get(db, id=zone_id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone not found"
        )

    zone = crud_zone.decrement_courier_count(db, zone_id=zone_id)
    return zone
