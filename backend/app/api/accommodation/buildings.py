from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.crud.accommodation import building as crud_building
from app.schemas.accommodation.building import BuildingCreate, BuildingUpdate, BuildingResponse
from app.core.database import get_db
from app.core.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[BuildingResponse])
def list_buildings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all buildings"""
    buildings = crud_building.get_multi(db, skip=skip, limit=limit)
    return buildings

@router.get("/{building_id}", response_model=BuildingResponse)
def get_building(
    building_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific building by ID"""
    building = crud_building.get(db, id=building_id)
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found"
        )
    return building

@router.post("/", response_model=BuildingResponse, status_code=status.HTTP_201_CREATED)
def create_building(
    building_in: BuildingCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new building"""
    building = crud_building.create(db, obj_in=building_in)
    return building

@router.put("/{building_id}", response_model=BuildingResponse)
def update_building(
    building_id: int,
    building_in: BuildingUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a building"""
    building = crud_building.get(db, id=building_id)
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found"
        )
    building = crud_building.update(db, db_obj=building, obj_in=building_in)
    return building

@router.delete("/{building_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_building(
    building_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a building"""
    building = crud_building.get(db, id=building_id)
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found"
        )
    crud_building.remove(db, id=building_id)
    return None
