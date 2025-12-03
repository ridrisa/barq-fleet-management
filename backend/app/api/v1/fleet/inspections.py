from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_organization, get_current_user, get_db
from app.models.tenant.organization import Organization
from app.models.user import User
from app.schemas.fleet import InspectionCreate, InspectionList, InspectionResponse, InspectionUpdate
from app.services.fleet import inspection_service, vehicle_service

router = APIRouter()


@router.get("/", response_model=List[InspectionList])
def get_inspections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    vehicle_id: Optional[int] = None,
):
    """Get inspections"""
    if vehicle_id:
        # Verify vehicle belongs to the organization
        vehicle = vehicle_service.get(db, id=vehicle_id)
        if not vehicle or vehicle.organization_id != current_org.id:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        return inspection_service.get_for_vehicle(
            db, vehicle_id=vehicle_id, skip=skip, limit=limit, organization_id=current_org.id
        )
    return inspection_service.get_multi(
        db, skip=skip, limit=limit, filters={"organization_id": current_org.id}
    )


@router.get("/failed", response_model=List[InspectionList])
def get_failed_inspections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get failed inspections"""
    return inspection_service.get_failed_inspections(
        db, skip=skip, limit=limit, organization_id=current_org.id
    )


@router.get("/follow-up", response_model=List[InspectionList])
def get_follow_up_inspections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get inspections requiring follow-up"""
    return inspection_service.get_requiring_follow_up(
        db, skip=skip, limit=limit, organization_id=current_org.id
    )


@router.get("/{inspection_id}", response_model=InspectionResponse)
def get_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get inspection by ID"""
    inspection = inspection_service.get(db, id=inspection_id)
    if not inspection or inspection.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return inspection


@router.post("/", response_model=InspectionResponse, status_code=status.HTTP_201_CREATED)
def create_inspection(
    inspection_in: InspectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Create new inspection"""
    # Verify vehicle belongs to the organization
    vehicle = vehicle_service.get(db, id=inspection_in.vehicle_id)
    if not vehicle or vehicle.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    return inspection_service.create(db, obj_in=inspection_in, organization_id=current_org.id)


@router.put("/{inspection_id}", response_model=InspectionResponse)
def update_inspection(
    inspection_id: int,
    inspection_in: InspectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update inspection"""
    inspection = inspection_service.get(db, id=inspection_id)
    if not inspection or inspection.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Inspection not found")

    # If updating vehicle_id, verify it belongs to the organization
    if inspection_in.vehicle_id:
        vehicle = vehicle_service.get(db, id=inspection_in.vehicle_id)
        if not vehicle or vehicle.organization_id != current_org.id:
            raise HTTPException(status_code=404, detail="Vehicle not found")

    return inspection_service.update(db, db_obj=inspection, obj_in=inspection_in)


@router.delete("/{inspection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Delete inspection"""
    inspection = inspection_service.get(db, id=inspection_id)
    if not inspection or inspection.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Inspection not found")
    inspection_service.delete(db, id=inspection_id)
    return None
