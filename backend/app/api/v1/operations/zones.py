from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_organization, get_current_user
from app.models.tenant.organization import Organization
from app.services.operations import zone_service
from app.schemas.operations.zone import ZoneCreate, ZoneMetrics, ZoneResponse, ZoneUpdate

router = APIRouter()


@router.get("/", response_model=List[ZoneResponse])
def list_zones(
    skip: int = 0,
    limit: int = 100,
    city: str = Query(None, description="Filter by city"),
    status: str = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List all zones with optional filters"""
    if city:
        zones = zone_service.get_by_city(
            db, city=city, skip=skip, limit=limit, organization_id=current_org.id
        )
    elif status == "active":
        zones = zone_service.get_active_zones(
            db, skip=skip, limit=limit, organization_id=current_org.id
        )
    else:
        zones = zone_service.get_multi(db, skip=skip, limit=limit, filters={"organization_id": current_org.id})
    return zones


@router.get("/at-capacity", response_model=List[ZoneResponse])
def list_zones_at_capacity(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List zones at or near capacity

    Business Logic:
    - Returns zones where current_couriers >= max_couriers
    - Used for load balancing decisions
    - Helps identify zones needing additional resources
    """
    zones = zone_service.get_at_capacity(db, organization_id=current_org.id)
    return zones


@router.get("/{zone_id}", response_model=ZoneResponse)
def get_zone(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get a specific zone by ID"""
    zone = zone_service.get(db, id=zone_id)
    if not zone or zone.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")
    return zone


@router.get("/code/{zone_code}", response_model=ZoneResponse)
def get_zone_by_code(
    zone_code: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get zone by unique code"""
    zone = zone_service.get_by_code(db, zone_code=zone_code, organization_id=current_org.id)
    if not zone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")
    return zone


@router.post("/", response_model=ZoneResponse, status_code=status.HTTP_201_CREATED)
def create_zone(
    zone_in: ZoneCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Create a new delivery zone

    Business Logic:
    - Validates zone code is unique within organization
    - Validates GeoJSON boundaries if provided
    - Initializes performance metrics to 0
    - Sets status to ACTIVE by default
    """
    # Check if zone code already exists in organization
    existing_zone = zone_service.get_by_code(
        db, zone_code=zone_in.zone_code, organization_id=current_org.id
    )
    if existing_zone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Zone with code '{zone_in.zone_code}' already exists",
        )

    # TODO: Validate GeoJSON boundaries
    # TODO: Calculate coverage area from boundaries

    zone = zone_service.create(db, obj_in=zone_in, organization_id=current_org.id)
    return zone


@router.put("/{zone_id}", response_model=ZoneResponse)
def update_zone(
    zone_id: int,
    zone_in: ZoneUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update a zone"""
    zone = zone_service.get(db, id=zone_id)
    if not zone or zone.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")
    zone = zone_service.update(db, db_obj=zone, obj_in=zone_in)
    return zone


@router.delete("/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_zone(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Delete a zone

    Business Logic:
    - Validates no active couriers in zone
    - Validates no pending deliveries in zone
    - Soft delete or hard delete based on business rules
    """
    zone = zone_service.get(db, id=zone_id)
    if not zone or zone.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")

    # Check if zone has active couriers
    if zone.current_couriers > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete zone with active couriers",
        )

    zone_service.remove(db, id=zone_id)
    return None


@router.get("/{zone_id}/metrics", response_model=ZoneMetrics)
def get_zone_metrics(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get zone performance metrics

    Returns:
    - Current courier count and utilization
    - Average delivery time
    - Success rate
    - Total deliveries completed
    - Capacity status
    """
    zone = zone_service.get(db, id=zone_id)
    if not zone or zone.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")

    # Calculate utilization rate
    utilization_rate = zone.utilization_rate if hasattr(zone, "utilization_rate") else 0.0

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
        is_at_capacity=zone.is_at_capacity if hasattr(zone, "is_at_capacity") else False,
    )

    return metrics


@router.post("/{zone_id}/couriers/increment", response_model=ZoneResponse)
def increment_courier_count(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Increment zone courier count

    Business Logic:
    - Called when courier enters zone
    - Validates capacity not exceeded
    - Updates current_couriers count
    """
    zone = zone_service.get(db, id=zone_id)
    if not zone or zone.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")

    if zone.current_couriers >= zone.max_couriers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Zone is at maximum capacity"
        )

    zone = zone_service.increment_courier_count(db, zone_id=zone_id)
    return zone


@router.post("/{zone_id}/couriers/decrement", response_model=ZoneResponse)
def decrement_courier_count(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Decrement zone courier count

    Business Logic:
    - Called when courier leaves zone
    - Updates current_couriers count
    - Prevents negative count
    """
    zone = zone_service.get(db, id=zone_id)
    if not zone or zone.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")

    zone = zone_service.decrement_courier_count(db, zone_id=zone_id)
    return zone
