from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.fleet.fuel_log import FuelLogCreate, FuelLogResponse, FuelLogSummary, FuelLogUpdate
from app.services.fleet import fuel_log_service

router = APIRouter()


@router.get("/", response_model=List[FuelLogResponse])
def list_fuel_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all fuel logs"""
    fuel_logs = fuel_log_service.get_multi(db, skip=skip, limit=limit)
    return fuel_logs


@router.get("/summary", response_model=FuelLogSummary)
def get_fuel_logs_summary(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Get fuel consumption summary"""
    return fuel_log_service.get_summary(db)


@router.get("/{fuel_log_id}", response_model=FuelLogResponse)
def get_fuel_log(
    fuel_log_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Get a specific fuel log by ID"""
    fuel_log = fuel_log_service.get(db, id=fuel_log_id)
    if not fuel_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fuel log not found")
    return fuel_log


@router.post("/", response_model=FuelLogResponse, status_code=status.HTTP_201_CREATED)
def create_fuel_log(
    fuel_log_in: FuelLogCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new fuel log"""
    fuel_log = fuel_log_service.create(db, obj_in=fuel_log_in)
    return fuel_log


@router.put("/{fuel_log_id}", response_model=FuelLogResponse)
def update_fuel_log(
    fuel_log_id: int,
    fuel_log_in: FuelLogUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a fuel log"""
    fuel_log = fuel_log_service.get(db, id=fuel_log_id)
    if not fuel_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fuel log not found")
    fuel_log = fuel_log_service.update(db, db_obj=fuel_log, obj_in=fuel_log_in)
    return fuel_log


@router.delete("/{fuel_log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fuel_log(
    fuel_log_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Delete a fuel log"""
    fuel_log = fuel_log_service.get(db, id=fuel_log_id)
    if not fuel_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fuel log not found")
    fuel_log_service.delete(db, id=fuel_log_id)
    return None
