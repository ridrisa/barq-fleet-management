"""Bed Allocation API Routes"""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.accommodation import AllocationCreate, AllocationResponse, AllocationUpdate
from app.services.accommodation import allocation_service

router = APIRouter()


@router.get("/", response_model=List[AllocationResponse])
def get_allocations(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    courier_id: Optional[int] = None,
    bed_id: Optional[int] = None,
    active_only: bool = False,
    current_user: User = Depends(get_current_user),
):
    """
    Get list of allocations with filtering

    Filters:
    - courier_id: Filter by courier ID
    - bed_id: Filter by bed ID
    - active_only: Show only active (not released) allocations
    """
    if active_only:
        return allocation_service.get_active(
            db, courier_id=courier_id, bed_id=bed_id, skip=skip, limit=limit
        )

    if courier_id:
        return allocation_service.get_by_courier(db, courier_id=courier_id, skip=skip, limit=limit)

    if bed_id:
        return allocation_service.get_by_bed(db, bed_id=bed_id, skip=skip, limit=limit)

    return allocation_service.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=AllocationResponse, status_code=status.HTTP_201_CREATED)
def create_allocation(
    allocation_in: AllocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create new bed allocation

    Allocates a bed to a courier. The bed must be available and the courier
    must not already have an active allocation.
    """
    allocation = allocation_service.allocate_bed(db, allocation_data=allocation_in)
    if not allocation:
        raise HTTPException(
            status_code=400,
            detail="Cannot allocate bed. Either bed is not available or courier already has an active allocation.",
        )

    return allocation


@router.get("/{allocation_id}", response_model=AllocationResponse)
def get_allocation(
    allocation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get allocation by ID"""
    allocation = allocation_service.get(db, id=allocation_id)
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
    return allocation


@router.put("/{allocation_id}", response_model=AllocationResponse)
def update_allocation(
    allocation_id: int,
    allocation_in: AllocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update allocation"""
    allocation = allocation_service.get(db, id=allocation_id)
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")

    return allocation_service.update(db, db_obj=allocation, obj_in=allocation_in)


@router.delete("/{allocation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_allocation(
    allocation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete allocation"""
    allocation = allocation_service.get(db, id=allocation_id)
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")

    allocation_service.delete(db, id=allocation_id)
    return None


@router.get("/courier/{courier_id}/active", response_model=AllocationResponse)
def get_courier_active_allocation(
    courier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get current active allocation for a courier

    Returns the active (not released) allocation for the specified courier
    """
    allocation = allocation_service.get_active_by_courier(db, courier_id=courier_id)
    if not allocation:
        raise HTTPException(status_code=404, detail="No active allocation found for this courier")
    return allocation


@router.get("/bed/{bed_id}/active", response_model=AllocationResponse)
def get_bed_active_allocation(
    bed_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get current active allocation for a bed

    Returns the active (not released) allocation for the specified bed
    """
    allocation = allocation_service.get_active_by_bed(db, bed_id=bed_id)
    if not allocation:
        raise HTTPException(status_code=404, detail="No active allocation found for this bed")
    return allocation


@router.post("/{allocation_id}/release", response_model=AllocationResponse)
def release_allocation(
    allocation_id: int,
    release_date: Optional[date] = Body(None, embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Release a bed allocation

    Marks the allocation as released and frees up the bed.
    If release_date is not provided, today's date will be used.
    """
    allocation = allocation_service.get(db, id=allocation_id)
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")

    if allocation.release_date:
        raise HTTPException(status_code=400, detail="Allocation has already been released")

    updated_allocation = allocation_service.release_allocation(
        db, allocation_id=allocation_id, release_date=release_date or date.today()
    )

    return updated_allocation


@router.get("/statistics/all", response_model=dict)
def get_allocation_statistics(
    courier_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get allocation statistics

    Returns:
    - total_allocations: Total number of allocations
    - active_allocations: Currently active allocations
    - completed_allocations: Released allocations
    - average_stay_duration_days: Average stay duration in days
    """
    return allocation_service.get_statistics(db, courier_id=courier_id)
