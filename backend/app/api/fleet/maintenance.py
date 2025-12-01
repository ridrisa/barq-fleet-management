from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.crud.fleet.maintenance import maintenance as crud_maintenance
from app.schemas.fleet.maintenance import MaintenanceCreate, MaintenanceUpdate, MaintenanceResponse
from app.config.database import get_db
from app.core.dependencies import get_current_user
from app.models.fleet.maintenance import VehicleMaintenance, MaintenanceStatus

router = APIRouter()

@router.get("/", response_model=List[MaintenanceResponse])
def list_maintenance(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all maintenance records"""
    maintenance_records = crud_maintenance.get_multi(db, skip=skip, limit=limit)
    return maintenance_records

@router.get("/upcoming", response_model=List[MaintenanceResponse])
def get_upcoming_maintenance(
    days: int = Query(30, ge=1, le=365, description="Number of days to look ahead"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get upcoming maintenance scheduled within the specified number of days"""
    today = date.today()
    future_date = today + timedelta(days=days)

    upcoming = db.query(VehicleMaintenance).filter(
        VehicleMaintenance.scheduled_date >= today,
        VehicleMaintenance.scheduled_date <= future_date,
        VehicleMaintenance.status.in_([MaintenanceStatus.SCHEDULED, MaintenanceStatus.IN_PROGRESS])
    ).order_by(VehicleMaintenance.scheduled_date).all()

    return upcoming

@router.get("/{maintenance_id}", response_model=MaintenanceResponse)
def get_maintenance(
    maintenance_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific maintenance record by ID"""
    maintenance = crud_maintenance.get(db, id=maintenance_id)
    if not maintenance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance record not found"
        )
    return maintenance

@router.post("/", response_model=MaintenanceResponse, status_code=status.HTTP_201_CREATED)
def create_maintenance(
    maintenance_in: MaintenanceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new maintenance record"""
    maintenance = crud_maintenance.create(db, obj_in=maintenance_in)
    return maintenance

@router.put("/{maintenance_id}", response_model=MaintenanceResponse)
def update_maintenance(
    maintenance_id: int,
    maintenance_in: MaintenanceUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a maintenance record"""
    maintenance = crud_maintenance.get(db, id=maintenance_id)
    if not maintenance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance record not found"
        )
    maintenance = crud_maintenance.update(db, db_obj=maintenance, obj_in=maintenance_in)
    return maintenance

@router.delete("/{maintenance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_maintenance(
    maintenance_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a maintenance record"""
    maintenance = crud_maintenance.get(db, id=maintenance_id)
    if not maintenance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance record not found"
        )
    crud_maintenance.remove(db, id=maintenance_id)
