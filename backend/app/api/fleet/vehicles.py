from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.crud.fleet import vehicle as crud_vehicle
from app.schemas.fleet.vehicle import VehicleCreate, VehicleUpdate, VehicleResponse
from app.config.database import get_db
from app.core.dependencies import get_current_user

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
    """Get complete history for a vehicle including maintenance, fuel logs, accidents, etc."""
    # Verify vehicle exists
    vehicle = crud_vehicle.get(db, id=vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )

    # Get all related records
    from app.models.fleet.maintenance import VehicleMaintenance
    from app.models.fleet.fuel_log import FuelLog
    from app.models.fleet.accident_log import AccidentLog
    from app.models.fleet.vehicle_log import VehicleLog
    from app.models.fleet.assignment import CourierVehicleAssignment

    maintenance_records = db.query(VehicleMaintenance).filter(
        VehicleMaintenance.vehicle_id == vehicle_id
    ).order_by(VehicleMaintenance.created_at.desc()).all()

    fuel_logs = db.query(FuelLog).filter(
        FuelLog.vehicle_id == vehicle_id
    ).order_by(FuelLog.created_at.desc()).all()

    accident_logs = db.query(AccidentLog).filter(
        AccidentLog.vehicle_id == vehicle_id
    ).order_by(AccidentLog.created_at.desc()).all()

    vehicle_logs = db.query(VehicleLog).filter(
        VehicleLog.vehicle_id == vehicle_id
    ).order_by(VehicleLog.created_at.desc()).all()

    assignments = db.query(CourierVehicleAssignment).filter(
        CourierVehicleAssignment.vehicle_id == vehicle_id
    ).order_by(CourierVehicleAssignment.created_at.desc()).all()

    return {
        "vehicle": model_to_dict(vehicle),
        "maintenance_records": [model_to_dict(r) for r in maintenance_records],
        "fuel_logs": [model_to_dict(r) for r in fuel_logs],
        "accident_logs": [model_to_dict(r) for r in accident_logs],
        "vehicle_logs": [model_to_dict(r) for r in vehicle_logs],
        "assignments": [model_to_dict(r) for r in assignments]
    }
