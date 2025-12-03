from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from app.crud.fleet import vehicle as crud_vehicle
from app.schemas.fleet.vehicle import VehicleCreate, VehicleUpdate, VehicleResponse
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.fleet.vehicle import Vehicle

router = APIRouter()

@router.get("/", response_model=List[VehicleResponse])
def list_vehicles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all vehicles"""
    vehicles = crud_vehicle.get_multi(db, skip=skip, limit=limit)
    return vehicles

@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific vehicle by ID"""
    vehicle = crud_vehicle.get(db, id=vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    return vehicle

@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    vehicle_in: VehicleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new vehicle"""
    vehicle = crud_vehicle.create(db, obj_in=vehicle_in)
    return vehicle

@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: int,
    vehicle_in: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a vehicle"""
    vehicle = crud_vehicle.get(db, id=vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    vehicle = crud_vehicle.update(db, db_obj=vehicle, obj_in=vehicle_in)
    return vehicle

@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a vehicle"""
    vehicle = crud_vehicle.get(db, id=vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    crud_vehicle.remove(db, id=vehicle_id)
    return None


def model_to_dict(obj):
    """Convert SQLAlchemy model to dict, handling datetime and enum serialization."""
    if obj is None:
        return None
    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        # Handle datetime objects
        if hasattr(value, 'isoformat'):
            value = value.isoformat()
        # Handle enum objects
        elif hasattr(value, 'value'):
            value = value.value
        result[column.name] = value
    return result


@router.get("/{vehicle_id}/history", response_model=Dict[str, Any])
def get_vehicle_history(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get complete history for a vehicle including maintenance, fuel logs, accidents, etc.

    Uses eager loading (selectinload) to avoid N+1 query problem by fetching
    all related records in a single query instead of separate queries.
    """
    # Use eager loading to fetch vehicle with all related records in one query
    vehicle = db.query(Vehicle).options(
        selectinload(Vehicle.maintenance_records),
        selectinload(Vehicle.fuel_logs),
        selectinload(Vehicle.accident_logs),
        selectinload(Vehicle.vehicle_logs),
        selectinload(Vehicle.assignment_history)
    ).filter(Vehicle.id == vehicle_id).first()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )

    # Sort related records by created_at descending (done in Python since
    # we already loaded them with eager loading)
    maintenance_records = sorted(
        vehicle.maintenance_records,
        key=lambda x: x.created_at or x.id,
        reverse=True
    )
    fuel_logs = sorted(
        vehicle.fuel_logs,
        key=lambda x: x.created_at or x.id,
        reverse=True
    )
    accident_logs = sorted(
        vehicle.accident_logs,
        key=lambda x: x.created_at or x.id,
        reverse=True
    )
    vehicle_logs = sorted(
        vehicle.vehicle_logs,
        key=lambda x: x.created_at or x.id,
        reverse=True
    )
    assignments = sorted(
        vehicle.assignment_history,
        key=lambda x: x.created_at or x.id,
        reverse=True
    )

    return {
        "vehicle": model_to_dict(vehicle),
        "maintenance_records": [model_to_dict(r) for r in maintenance_records],
        "fuel_logs": [model_to_dict(r) for r in fuel_logs],
        "accident_logs": [model_to_dict(r) for r in accident_logs],
        "vehicle_logs": [model_to_dict(r) for r in vehicle_logs],
        "assignments": [model_to_dict(r) for r in assignments]
    }
