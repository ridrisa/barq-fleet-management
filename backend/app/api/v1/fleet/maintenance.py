from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_organization, get_current_user, get_db
from app.models.tenant.organization import Organization
from app.models.user import User
from app.schemas.fleet import (
    MaintenanceCreate,
    MaintenanceList,
    MaintenanceResponse,
    MaintenanceUpdate,
)
from app.services.fleet import maintenance_service, vehicle_service

router = APIRouter()


@router.get("/", response_model=List[MaintenanceList])
def get_maintenance_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    vehicle_id: Optional[int] = None,
):
    """Get maintenance records"""
    if vehicle_id:
        # Verify vehicle belongs to the organization
        vehicle = vehicle_service.get(db, id=vehicle_id)
        if not vehicle or vehicle.organization_id != current_org.id:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        return maintenance_service.get_for_vehicle(
            db, vehicle_id=vehicle_id, skip=skip, limit=limit, organization_id=current_org.id
        )
    return maintenance_service.get_multi(
        db, skip=skip, limit=limit, filters={"organization_id": current_org.id}
    )


@router.get("/scheduled", response_model=List[MaintenanceList])
def get_scheduled_maintenance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """Get scheduled maintenance"""
    return maintenance_service.get_scheduled(
        db, skip=skip, limit=limit, organization_id=current_org.id
    )


@router.get("/overdue", response_model=List[MaintenanceList])
def get_overdue_maintenance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """Get overdue maintenance"""
    return maintenance_service.get_overdue(
        db, skip=skip, limit=limit, organization_id=current_org.id
    )


@router.get("/{maintenance_id}", response_model=MaintenanceResponse)
def get_maintenance(
    maintenance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get maintenance by ID"""
    maintenance = maintenance_service.get(db, id=maintenance_id)
    if not maintenance or maintenance.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    return maintenance


@router.post("/", response_model=MaintenanceResponse, status_code=status.HTTP_201_CREATED)
def create_maintenance(
    maintenance_in: MaintenanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Create new maintenance record"""
    # Verify vehicle belongs to the organization
    vehicle = vehicle_service.get(db, id=maintenance_in.vehicle_id)
    if not vehicle or vehicle.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    return maintenance_service.create(db, obj_in=maintenance_in, organization_id=current_org.id)


@router.put("/{maintenance_id}", response_model=MaintenanceResponse)
def update_maintenance(
    maintenance_id: int,
    maintenance_in: MaintenanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update maintenance record"""
    maintenance = maintenance_service.get(db, id=maintenance_id)
    if not maintenance or maintenance.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Maintenance record not found")

    # If updating vehicle_id, verify it belongs to the organization
    if maintenance_in.vehicle_id:
        vehicle = vehicle_service.get(db, id=maintenance_in.vehicle_id)
        if not vehicle or vehicle.organization_id != current_org.id:
            raise HTTPException(status_code=404, detail="Vehicle not found")

    return maintenance_service.update(db, db_obj=maintenance, obj_in=maintenance_in)


@router.delete("/{maintenance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_maintenance(
    maintenance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Delete maintenance record"""
    maintenance = maintenance_service.get(db, id=maintenance_id)
    if not maintenance or maintenance.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    maintenance_service.delete(db, id=maintenance_id)
    return None
