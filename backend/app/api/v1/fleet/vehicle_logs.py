from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_organization, get_current_user, get_db
from app.models.tenant.organization import Organization
from app.models.user import User
from app.schemas.fleet import VehicleLogCreate, VehicleLogList, VehicleLogResponse, VehicleLogUpdate
from app.services.fleet import courier_service, vehicle_log_service, vehicle_service

router = APIRouter()


@router.get("/", response_model=List[VehicleLogList])
def get_vehicle_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    vehicle_id: Optional[int] = None,
    courier_id: Optional[int] = None,
):
    """Get vehicle logs"""
    if vehicle_id:
        # Verify vehicle belongs to the organization
        vehicle = vehicle_service.get(db, id=vehicle_id)
        if not vehicle or vehicle.organization_id != current_org.id:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        return vehicle_log_service.get_logs_for_vehicle(
            db, vehicle_id=vehicle_id, skip=skip, limit=limit, organization_id=current_org.id
        )
    elif courier_id:
        # Verify courier belongs to the organization
        courier = courier_service.get(db, id=courier_id)
        if not courier or courier.organization_id != current_org.id:
            raise HTTPException(status_code=404, detail="Courier not found")
        return vehicle_log_service.get_logs_for_courier(
            db, courier_id=courier_id, skip=skip, limit=limit, organization_id=current_org.id
        )
    return vehicle_log_service.get_multi(
        db, skip=skip, limit=limit, filters={"organization_id": current_org.id}
    )


@router.get("/{log_id}", response_model=VehicleLogResponse)
def get_vehicle_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get vehicle log by ID"""
    log = vehicle_log_service.get(db, id=log_id)
    if not log or log.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Vehicle log not found")
    return log


@router.post("/", response_model=VehicleLogResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle_log(
    log_in: VehicleLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Create new vehicle log"""
    # Verify vehicle belongs to the organization
    vehicle = vehicle_service.get(db, id=log_in.vehicle_id)
    if not vehicle or vehicle.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # Verify courier belongs to the organization if provided
    if log_in.courier_id:
        courier = courier_service.get(db, id=log_in.courier_id)
        if not courier or courier.organization_id != current_org.id:
            raise HTTPException(status_code=404, detail="Courier not found")

    return vehicle_log_service.create(db, obj_in=log_in, organization_id=current_org.id)


@router.put("/{log_id}", response_model=VehicleLogResponse)
def update_vehicle_log(
    log_id: int,
    log_in: VehicleLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update vehicle log"""
    log = vehicle_log_service.get(db, id=log_id)
    if not log or log.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Vehicle log not found")

    # If updating vehicle_id, verify it belongs to the organization
    if log_in.vehicle_id:
        vehicle = vehicle_service.get(db, id=log_in.vehicle_id)
        if not vehicle or vehicle.organization_id != current_org.id:
            raise HTTPException(status_code=404, detail="Vehicle not found")

    # If updating courier_id, verify it belongs to the organization
    if log_in.courier_id:
        courier = courier_service.get(db, id=log_in.courier_id)
        if not courier or courier.organization_id != current_org.id:
            raise HTTPException(status_code=404, detail="Courier not found")

    return vehicle_log_service.update(db, db_obj=log, obj_in=log_in)


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Delete vehicle log"""
    log = vehicle_log_service.get(db, id=log_id)
    if not log or log.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Vehicle log not found")
    vehicle_log_service.delete(db, id=log_id)
    return None
