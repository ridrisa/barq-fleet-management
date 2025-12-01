from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.fleet import VehicleLogCreate, VehicleLogUpdate, VehicleLogResponse, VehicleLogList
from app.services.fleet import vehicle_log_service

router = APIRouter()

@router.get("/", response_model=List[VehicleLogList])
def get_vehicle_logs(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    vehicle_id: int = None,
    courier_id: int = None,
    current_user: User = Depends(get_current_user),
):
    """Get vehicle logs"""
    if vehicle_id:
        return vehicle_log_service.get_logs_for_vehicle(db, vehicle_id=vehicle_id, skip=skip, limit=limit)
    elif courier_id:
        return vehicle_log_service.get_logs_for_courier(db, courier_id=courier_id, skip=skip, limit=limit)
    return vehicle_log_service.get_multi(db, skip=skip, limit=limit)

@router.get("/{log_id}", response_model=VehicleLogResponse)
def get_vehicle_log(log_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get vehicle log by ID"""
    log = vehicle_log_service.get(db, id=log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Vehicle log not found")
    return log

@router.post("/", response_model=VehicleLogResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle_log(log_in: VehicleLogCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create new vehicle log"""
    return vehicle_log_service.create(db, obj_in=log_in)

@router.put("/{log_id}", response_model=VehicleLogResponse)
def update_vehicle_log(log_id: int, log_in: VehicleLogUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update vehicle log"""
    log = vehicle_log_service.get(db, id=log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Vehicle log not found")
    return vehicle_log_service.update(db, db_obj=log, obj_in=log_in)

@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle_log(log_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete vehicle log"""
    log = vehicle_log_service.get(db, id=log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Vehicle log not found")
    vehicle_log_service.delete(db, id=log_id)
    return None
