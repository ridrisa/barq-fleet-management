from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.fleet import AssignmentCreate, AssignmentUpdate, AssignmentResponse, AssignmentList
from app.services.fleet import assignment_service

router = APIRouter()

@router.get("/", response_model=List[AssignmentList])
def get_assignments(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    courier_id: int = None,
    vehicle_id: int = None,
    current_user: User = Depends(get_current_user),
):
    """Get assignments"""
    filters = {}
    if courier_id:
        filters["courier_id"] = courier_id
    if vehicle_id:
        filters["vehicle_id"] = vehicle_id
    return assignment_service.get_multi(db, skip=skip, limit=limit, filters=filters)

@router.get("/{assignment_id}", response_model=AssignmentResponse)
def get_assignment(assignment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get assignment by ID"""
    assignment = assignment_service.get(db, id=assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment

@router.post("/", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_assignment(assignment_in: AssignmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create new assignment"""
    return assignment_service.create(db, obj_in=assignment_in)

@router.put("/{assignment_id}", response_model=AssignmentResponse)
def update_assignment(assignment_id: int, assignment_in: AssignmentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update assignment"""
    assignment = assignment_service.get(db, id=assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment_service.update(db, db_obj=assignment, obj_in=assignment_in)

@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assignment(assignment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete assignment"""
    assignment = assignment_service.get(db, id=assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    assignment_service.delete(db, id=assignment_id)
    return None
