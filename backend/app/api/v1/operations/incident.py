"""Incident Management API Routes"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.orm import Session
from datetime import date

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.operations.incident import IncidentType, IncidentStatus
from app.schemas.operations import (
    IncidentCreate, IncidentUpdate, IncidentResponse
)
from app.services.operations import incident_service


router = APIRouter()


@router.get("/", response_model=List[IncidentResponse])
def get_incidents(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    courier_id: Optional[int] = None,
    vehicle_id: Optional[int] = None,
    incident_type: Optional[IncidentType] = None,
    status_filter: Optional[IncidentStatus] = Query(None, alias="status"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Get list of incidents with filtering

    Filters:
    - courier_id: Filter by courier ID
    - vehicle_id: Filter by vehicle ID
    - incident_type: Filter by incident type
    - status: Filter by incident status
    - start_date, end_date: Filter by incident date range
    """
    # Filter by type
    if incident_type:
        return incident_service.get_by_type(
            db, incident_type=incident_type, skip=skip, limit=limit
        )

    # Filter by status
    if status_filter:
        return incident_service.get_by_status(
            db, status=status_filter, skip=skip, limit=limit
        )

    # Filter by date range
    if start_date and end_date:
        return incident_service.get_by_date_range(
            db,
            start_date=start_date,
            end_date=end_date,
            courier_id=courier_id,
            vehicle_id=vehicle_id,
            skip=skip,
            limit=limit
        )

    # Filter by courier
    if courier_id:
        return incident_service.get_by_courier(
            db, courier_id=courier_id, skip=skip, limit=limit
        )

    # Filter by vehicle
    if vehicle_id:
        return incident_service.get_by_vehicle(
            db, vehicle_id=vehicle_id, skip=skip, limit=limit
        )

    return incident_service.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
def create_incident(
    incident_in: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new incident"""
    return incident_service.create(db, obj_in=incident_in)


@router.get("/open", response_model=List[IncidentResponse])
def get_open_incidents(
    db: Session = Depends(get_db),
    courier_id: Optional[int] = None,
    vehicle_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get open incidents (reported or investigating)"""
    return incident_service.get_open_incidents(
        db,
        courier_id=courier_id,
        vehicle_id=vehicle_id,
        skip=skip,
        limit=limit
    )


@router.get("/recent", response_model=List[IncidentResponse])
def get_recent_incidents(
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365),
    courier_id: Optional[int] = None,
    vehicle_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get recent incidents within specified days"""
    return incident_service.get_recent_incidents(
        db,
        days=days,
        courier_id=courier_id,
        vehicle_id=vehicle_id,
        skip=skip,
        limit=limit
    )


@router.get("/high-cost", response_model=List[IncidentResponse])
def get_high_cost_incidents(
    db: Session = Depends(get_db),
    min_cost: int = Query(1000, ge=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get incidents with high costs"""
    return incident_service.get_high_cost_incidents(
        db, min_cost=min_cost, skip=skip, limit=limit
    )


@router.get("/statistics", response_model=dict)
def get_incident_statistics(
    db: Session = Depends(get_db),
    courier_id: Optional[int] = None,
    vehicle_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
):
    """Get incident statistics"""
    return incident_service.get_statistics(
        db,
        courier_id=courier_id,
        vehicle_id=vehicle_id,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get incident by ID"""
    incident = incident_service.get(db, id=incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.put("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: int,
    incident_in: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update incident"""
    incident = incident_service.get(db, id=incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incident_service.update(db, db_obj=incident, obj_in=incident_in)


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete incident"""
    incident = incident_service.get(db, id=incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident_service.delete(db, id=incident_id)
    return None


@router.patch("/{incident_id}/status", response_model=IncidentResponse)
def update_incident_status(
    incident_id: int,
    status_update: IncidentStatus = Body(...),
    resolution: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update incident status"""
    incident = incident_service.update_status(
        db,
        incident_id=incident_id,
        status=status_update,
        resolution=resolution
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.patch("/{incident_id}/resolve", response_model=IncidentResponse)
def resolve_incident(
    incident_id: int,
    resolution: str = Body(...),
    cost: Optional[int] = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark incident as resolved"""
    incident = incident_service.resolve_incident(
        db,
        incident_id=incident_id,
        resolution=resolution,
        cost=cost
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.patch("/{incident_id}/close", response_model=IncidentResponse)
def close_incident(
    incident_id: int,
    resolution: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Close incident"""
    incident = incident_service.close_incident(
        db,
        incident_id=incident_id,
        resolution=resolution
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident
