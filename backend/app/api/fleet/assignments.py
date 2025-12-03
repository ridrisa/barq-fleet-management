from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.crud.fleet import assignment as crud_assignment
from app.schemas.fleet.assignment import AssignmentCreate, AssignmentResponse, AssignmentUpdate

router = APIRouter()


@router.get("/", response_model=List[AssignmentResponse])
def list_assignments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all vehicle assignments"""
    assignments = crud_assignment.get_multi(db, skip=skip, limit=limit)
    return assignments


@router.get("/{assignment_id}", response_model=AssignmentResponse)
def get_assignment(
    assignment_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Get a specific assignment by ID"""
    assignment = crud_assignment.get(db, id=assignment_id)
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")
    return assignment


@router.post("/", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_assignment(
    assignment_in: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new vehicle assignment"""
    assignment = crud_assignment.create(db, obj_in=assignment_in)
    return assignment


@router.put("/{assignment_id}", response_model=AssignmentResponse)
def update_assignment(
    assignment_id: int,
    assignment_in: AssignmentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update an assignment"""
    assignment = crud_assignment.get(db, id=assignment_id)
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")
    assignment = crud_assignment.update(db, db_obj=assignment, obj_in=assignment_in)
    return assignment


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assignment(
    assignment_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Delete an assignment"""
    assignment = crud_assignment.get(db, id=assignment_id)
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")
    crud_assignment.remove(db, id=assignment_id)
    return None
