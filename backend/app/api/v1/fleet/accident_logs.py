from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_organization, get_current_user, get_db
from app.models.tenant.organization import Organization
from app.models.user import User
from app.schemas.fleet import (
    AccidentLogCreate,
    AccidentLogList,
    AccidentLogResponse,
    AccidentLogUpdate,
)
from app.services.fleet import accident_log_service, courier_service, vehicle_service

router = APIRouter()


@router.get("/", response_model=List[AccidentLogList])
def get_accident_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    vehicle_id: Optional[int] = None,
    courier_id: Optional[int] = None,
):
    """Get accident logs"""
    if vehicle_id:
        # Verify vehicle belongs to the organization
        vehicle = vehicle_service.get(db, id=vehicle_id)
        if not vehicle or vehicle.organization_id != current_org.id:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        return accident_log_service.get_for_vehicle(
            db, vehicle_id=vehicle_id, skip=skip, limit=limit, organization_id=current_org.id
        )
    elif courier_id:
        # Verify courier belongs to the organization
        courier = courier_service.get(db, id=courier_id)
        if not courier or courier.organization_id != current_org.id:
            raise HTTPException(status_code=404, detail="Courier not found")
        return accident_log_service.get_for_courier(
            db, courier_id=courier_id, skip=skip, limit=limit, organization_id=current_org.id
        )
    return accident_log_service.get_multi(
        db, skip=skip, limit=limit, filters={"organization_id": current_org.id}
    )


@router.get("/open", response_model=List[AccidentLogList])
def get_open_accidents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """Get open accident cases"""
    return accident_log_service.get_open_cases(
        db, skip=skip, limit=limit, organization_id=current_org.id
    )


@router.get("/{accident_id}", response_model=AccidentLogResponse)
def get_accident_log(
    accident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get accident log by ID"""
    accident = accident_log_service.get(db, id=accident_id)
    if not accident or accident.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Accident log not found")
    return accident


@router.post("/", response_model=AccidentLogResponse, status_code=status.HTTP_201_CREATED)
def create_accident_log(
    accident_in: AccidentLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Create new accident log"""
    # Verify vehicle belongs to the organization if provided
    if accident_in.vehicle_id:
        vehicle = vehicle_service.get(db, id=accident_in.vehicle_id)
        if not vehicle or vehicle.organization_id != current_org.id:
            raise HTTPException(status_code=404, detail="Vehicle not found")

    # Verify courier belongs to the organization if provided
    if accident_in.courier_id:
        courier = courier_service.get(db, id=accident_in.courier_id)
        if not courier or courier.organization_id != current_org.id:
            raise HTTPException(status_code=404, detail="Courier not found")

    return accident_log_service.create(db, obj_in=accident_in, organization_id=current_org.id)


@router.put("/{accident_id}", response_model=AccidentLogResponse)
def update_accident_log(
    accident_id: int,
    accident_in: AccidentLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update accident log"""
    accident = accident_log_service.get(db, id=accident_id)
    if not accident or accident.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Accident log not found")

    # If updating vehicle_id, verify it belongs to the organization
    if accident_in.vehicle_id:
        vehicle = vehicle_service.get(db, id=accident_in.vehicle_id)
        if not vehicle or vehicle.organization_id != current_org.id:
            raise HTTPException(status_code=404, detail="Vehicle not found")

    # If updating courier_id, verify it belongs to the organization
    if accident_in.courier_id:
        courier = courier_service.get(db, id=accident_in.courier_id)
        if not courier or courier.organization_id != current_org.id:
            raise HTTPException(status_code=404, detail="Courier not found")

    return accident_log_service.update(db, db_obj=accident, obj_in=accident_in)


@router.delete("/{accident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_accident_log(
    accident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Delete accident log"""
    accident = accident_log_service.get(db, id=accident_id)
    if not accident or accident.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Accident log not found")
    accident_log_service.delete(db, id=accident_id)
    return None
