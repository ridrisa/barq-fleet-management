from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_organization, get_current_user, get_db
from app.models.tenant.organization import Organization
from app.models.user import User
from app.schemas.fleet import AssignmentCreate, AssignmentList, AssignmentResponse, AssignmentUpdate
from app.services.fleet import assignment_service, courier_service, vehicle_service

router = APIRouter()


@router.get("/", response_model=List[AssignmentList])
def get_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    courier_id: Optional[int] = None,
    vehicle_id: Optional[int] = None,
):
    """Get assignments"""
    filters = {"organization_id": current_org.id}
    if courier_id:
        # Verify courier belongs to the organization
        courier = courier_service.get(db, id=courier_id)
        if not courier or courier.organization_id != current_org.id:
            raise HTTPException(status_code=404, detail="Courier not found")
        filters["courier_id"] = courier_id
    if vehicle_id:
        # Verify vehicle belongs to the organization
        vehicle = vehicle_service.get(db, id=vehicle_id)
        if not vehicle or vehicle.organization_id != current_org.id:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        filters["vehicle_id"] = vehicle_id
    return assignment_service.get_multi(db, skip=skip, limit=limit, filters=filters)


@router.get("/{assignment_id}", response_model=AssignmentResponse)
def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get assignment by ID"""
    assignment = assignment_service.get(db, id=assignment_id)
    if not assignment or assignment.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment


@router.post("/", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_assignment(
    assignment_in: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Create new assignment"""
    # Verify courier belongs to the organization
    courier = courier_service.get(db, id=assignment_in.courier_id)
    if not courier or courier.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Courier not found")

    # Verify vehicle belongs to the organization
    vehicle = vehicle_service.get(db, id=assignment_in.vehicle_id)
    if not vehicle or vehicle.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    return assignment_service.create(db, obj_in=assignment_in, organization_id=current_org.id)


@router.put("/{assignment_id}", response_model=AssignmentResponse)
def update_assignment(
    assignment_id: int,
    assignment_in: AssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update assignment"""
    assignment = assignment_service.get(db, id=assignment_id)
    if not assignment or assignment.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # If updating courier_id, verify it belongs to the organization
    if assignment_in.courier_id:
        courier = courier_service.get(db, id=assignment_in.courier_id)
        if not courier or courier.organization_id != current_org.id:
            raise HTTPException(status_code=404, detail="Courier not found")

    # If updating vehicle_id, verify it belongs to the organization
    if assignment_in.vehicle_id:
        vehicle = vehicle_service.get(db, id=assignment_in.vehicle_id)
        if not vehicle or vehicle.organization_id != current_org.id:
            raise HTTPException(status_code=404, detail="Vehicle not found")

    return assignment_service.update(db, db_obj=assignment, obj_in=assignment_in)


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Delete assignment"""
    assignment = assignment_service.get(db, id=assignment_id)
    if not assignment or assignment.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Assignment not found")
    assignment_service.delete(db, id=assignment_id)
    return None
