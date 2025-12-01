from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from app.crud.fleet.fuel_log import fuel_log as crud_fuel_log
from app.schemas.fleet.fuel_log import FuelLogCreate, FuelLogUpdate, FuelLogResponse, FuelLogSummary
from app.config.database import get_db
from app.core.dependencies import get_current_user
from app.models.fleet.fuel_log import FuelLog

router = APIRouter()

@router.get("/", response_model=List[FuelLogResponse])
def list_fuel_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all fuel logs"""
    fuel_logs = crud_fuel_log.get_multi(db, skip=skip, limit=limit)
    return fuel_logs

@router.get("/summary", response_model=FuelLogSummary)
def get_fuel_logs_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get fuel consumption summary"""
    result = db.query(
        func.sum(FuelLog.fuel_quantity).label('total_fuel_quantity'),
        func.sum(FuelLog.fuel_cost).label('total_fuel_cost'),
        func.avg(FuelLog.cost_per_liter).label('average_cost_per_liter'),
        func.count(FuelLog.id).label('log_count')
    ).first()

    # Calculate total distance (difference between max and min odometer readings)
    odometer_result = db.query(
        func.max(FuelLog.odometer_reading).label('max_odometer'),
        func.min(FuelLog.odometer_reading).label('min_odometer')
    ).first()

    total_distance = Decimal('0.0')
    if odometer_result.max_odometer and odometer_result.min_odometer:
        total_distance = Decimal(str(odometer_result.max_odometer)) - Decimal(str(odometer_result.min_odometer))

    total_fuel_quantity = Decimal(str(result.total_fuel_quantity or 0))
    average_consumption = Decimal('0.0')
    if total_fuel_quantity > 0 and total_distance > 0:
        average_consumption = total_distance / total_fuel_quantity

    return FuelLogSummary(
        total_fuel_quantity=total_fuel_quantity,
        total_fuel_cost=Decimal(str(result.total_fuel_cost or 0)),
        average_cost_per_liter=Decimal(str(result.average_cost_per_liter or 0)),
        total_distance=total_distance,
        average_consumption=average_consumption,
        log_count=result.log_count or 0
    )

@router.get("/{fuel_log_id}", response_model=FuelLogResponse)
def get_fuel_log(
    fuel_log_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific fuel log by ID"""
    fuel_log = crud_fuel_log.get(db, id=fuel_log_id)
    if not fuel_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fuel log not found"
        )
    return fuel_log

@router.post("/", response_model=FuelLogResponse, status_code=status.HTTP_201_CREATED)
def create_fuel_log(
    fuel_log_in: FuelLogCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new fuel log"""
    fuel_log = crud_fuel_log.create(db, obj_in=fuel_log_in)
    return fuel_log

@router.put("/{fuel_log_id}", response_model=FuelLogResponse)
def update_fuel_log(
    fuel_log_id: int,
    fuel_log_in: FuelLogUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a fuel log"""
    fuel_log = crud_fuel_log.get(db, id=fuel_log_id)
    if not fuel_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fuel log not found"
        )
    fuel_log = crud_fuel_log.update(db, db_obj=fuel_log, obj_in=fuel_log_in)
    return fuel_log

@router.delete("/{fuel_log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fuel_log(
    fuel_log_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a fuel log"""
    fuel_log = crud_fuel_log.get(db, id=fuel_log_id)
    if not fuel_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fuel log not found"
        )
    crud_fuel_log.remove(db, id=fuel_log_id)
