from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.fleet import MaintenanceCreate, MaintenanceUpdate, MaintenanceResponse, MaintenanceList
from app.services.fleet import maintenance_service

router = APIRouter()

@router.get("/", response_model=List[MaintenanceList])
def get_maintenance_records(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    vehicle_id: int = None,
    current_user: User = Depends(get_current_user),
):
    """Get maintenance records"""
    if vehicle_id:
        return maintenance_service.get_for_vehicle(db, vehicle_id=vehicle_id, skip=skip, limit=limit)
    return maintenance_service.get_multi(db, skip=skip, limit=limit)

@router.get("/scheduled", response_model=List[MaintenanceList])
def get_scheduled_maintenance(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get scheduled maintenance"""
    return maintenance_service.get_scheduled(db, skip=skip, limit=limit)

@router.get("/overdue", response_model=List[MaintenanceList])
def get_overdue_maintenance(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get overdue maintenance"""
    return maintenance_service.get_overdue(db, skip=skip, limit=limit)

@router.get("/{maintenance_id}", response_model=MaintenanceResponse)
def get_maintenance(maintenance_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get maintenance by ID"""
    maintenance = maintenance_service.get(db, id=maintenance_id)
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    return maintenance

@router.post("/", response_model=MaintenanceResponse, status_code=status.HTTP_201_CREATED)
def create_maintenance(maintenance_in: MaintenanceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create new maintenance record"""
    return maintenance_service.create(db, obj_in=maintenance_in)

@router.put("/{maintenance_id}", response_model=MaintenanceResponse)
def update_maintenance(maintenance_id: int, maintenance_in: MaintenanceUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update maintenance record"""
    maintenance = maintenance_service.get(db, id=maintenance_id)
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    return maintenance_service.update(db, db_obj=maintenance, obj_in=maintenance_in)

@router.delete("/{maintenance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_maintenance(maintenance_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete maintenance record"""
    maintenance = maintenance_service.get(db, id=maintenance_id)
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    maintenance_service.delete(db, id=maintenance_id)
    return None
