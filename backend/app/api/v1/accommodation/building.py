"""Building Management API Routes"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.accommodation import BuildingCreate, BuildingResponse, BuildingUpdate
from app.services.accommodation import building_service, room_service

router = APIRouter()


@router.get("/", response_model=List[BuildingResponse])
def get_buildings(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Get list of buildings with optional search

    Filters:
    - search: Search term for name or address
    """
    if search:
        return building_service.search_buildings(db, search_term=search, skip=skip, limit=limit)

    return building_service.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=BuildingResponse, status_code=status.HTTP_201_CREATED)
def create_building(
    building_in: BuildingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new building"""
    # Check if building with same name already exists
    existing = building_service.get_by_name(db, name=building_in.name)
    if existing:
        raise HTTPException(
            status_code=400, detail=f"Building with name '{building_in.name}' already exists"
        )

    return building_service.create(db, obj_in=building_in)


@router.get("/{building_id}", response_model=BuildingResponse)
def get_building(
    building_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get building by ID"""
    building = building_service.get(db, id=building_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    return building


@router.put("/{building_id}", response_model=BuildingResponse)
def update_building(
    building_id: int,
    building_in: BuildingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update building"""
    building = building_service.get(db, id=building_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    # Check if name is being updated and if it conflicts
    if building_in.name and building_in.name != building.name:
        existing = building_service.get_by_name(db, name=building_in.name)
        if existing:
            raise HTTPException(
                status_code=400, detail=f"Building with name '{building_in.name}' already exists"
            )

    return building_service.update(db, db_obj=building, obj_in=building_in)


@router.delete("/{building_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_building(
    building_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete building"""
    building = building_service.get(db, id=building_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    # Check if building has rooms
    rooms = room_service.get_by_building(db, building_id=building_id, limit=1)
    if rooms:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete building with existing rooms. Delete rooms first.",
        )

    building_service.delete(db, id=building_id)
    return None


@router.get("/{building_id}/statistics", response_model=dict)
def get_building_statistics(
    building_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get statistics for a specific building

    Returns:
    - building_id: Building ID
    - building_name: Building name
    - total_rooms: Total number of rooms
    - total_capacity: Total bed capacity
    - address: Building address
    """
    building = building_service.get(db, id=building_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    return building_service.get_statistics(db, building_id=building_id)


@router.post("/{building_id}/update-stats", response_model=BuildingResponse)
def update_building_stats(
    building_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Recalculate and update building statistics

    Updates total_rooms and total_capacity based on current room data
    """
    building = building_service.update_building_stats(db, building_id=building_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    return building


@router.get("/statistics/all", response_model=dict)
def get_all_buildings_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get statistics for all buildings

    Returns:
    - total_buildings: Total number of buildings
    - total_rooms: Total number of rooms across all buildings
    - total_capacity: Total bed capacity across all buildings
    - average_capacity_per_building: Average capacity per building
    """
    return building_service.get_statistics(db)
