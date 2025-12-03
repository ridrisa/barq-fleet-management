from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.crud.fleet.vehicle_log import vehicle_log as crud_vehicle_log
from app.schemas.fleet.vehicle_log import VehicleLogCreate, VehicleLogResponse, VehicleLogUpdate

router = APIRouter()


@router.get("/", response_model=List[VehicleLogResponse])
def list_vehicle_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all vehicle logs"""
    vehicle_logs = crud_vehicle_log.get_multi(db, skip=skip, limit=limit)
    return vehicle_logs


@router.get("/{vehicle_log_id}", response_model=VehicleLogResponse)
def get_vehicle_log(
    vehicle_log_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Get a specific vehicle log by ID"""
    vehicle_log = crud_vehicle_log.get(db, id=vehicle_log_id)
    if not vehicle_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle log not found")
    return vehicle_log


@router.post("/", response_model=VehicleLogResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle_log(
    vehicle_log_in: VehicleLogCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new vehicle log"""
    vehicle_log = crud_vehicle_log.create(db, obj_in=vehicle_log_in)
    return vehicle_log


@router.put("/{vehicle_log_id}", response_model=VehicleLogResponse)
def update_vehicle_log(
    vehicle_log_id: int,
    vehicle_log_in: VehicleLogUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a vehicle log"""
    vehicle_log = crud_vehicle_log.get(db, id=vehicle_log_id)
    if not vehicle_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle log not found")
    vehicle_log = crud_vehicle_log.update(db, db_obj=vehicle_log, obj_in=vehicle_log_in)
    return vehicle_log


@router.delete("/{vehicle_log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle_log(
    vehicle_log_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Delete a vehicle log"""
    vehicle_log = crud_vehicle_log.get(db, id=vehicle_log_id)
    if not vehicle_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle log not found")
    crud_vehicle_log.remove(db, id=vehicle_log_id)
    return None
