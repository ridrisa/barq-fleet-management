from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.crud.fleet.inspection import inspection as crud_inspection
from app.schemas.fleet.inspection import InspectionCreate, InspectionResponse, InspectionUpdate

router = APIRouter()


@router.get("/", response_model=List[InspectionResponse])
def list_inspections(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all inspections"""
    inspections = crud_inspection.get_multi(db, skip=skip, limit=limit)
    return inspections


@router.get("/{inspection_id}", response_model=InspectionResponse)
def get_inspection(
    inspection_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Get a specific inspection by ID"""
    inspection = crud_inspection.get(db, id=inspection_id)
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")
    return inspection


@router.post("/", response_model=InspectionResponse, status_code=status.HTTP_201_CREATED)
def create_inspection(
    inspection_in: InspectionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new inspection"""
    inspection = crud_inspection.create(db, obj_in=inspection_in)
    return inspection


@router.put("/{inspection_id}", response_model=InspectionResponse)
def update_inspection(
    inspection_id: int,
    inspection_in: InspectionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update an inspection"""
    inspection = crud_inspection.get(db, id=inspection_id)
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")
    inspection = crud_inspection.update(db, db_obj=inspection, obj_in=inspection_in)
    return inspection


@router.delete("/{inspection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inspection(
    inspection_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Delete an inspection"""
    inspection = crud_inspection.get(db, id=inspection_id)
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")
    crud_inspection.remove(db, id=inspection_id)
    return None
