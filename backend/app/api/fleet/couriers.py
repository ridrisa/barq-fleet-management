from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.crud.fleet import courier as crud_courier
from app.schemas.fleet.courier import CourierCreate, CourierUpdate, CourierResponse
from app.core.database import get_db
from app.core.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[CourierResponse])
def list_couriers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all couriers"""
    couriers = crud_courier.get_multi(db, skip=skip, limit=limit)
    return couriers

@router.get("/{courier_id}", response_model=CourierResponse)
def get_courier(
    courier_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific courier by ID"""
    courier = crud_courier.get(db, id=courier_id)
    if not courier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found"
        )
    return courier

@router.post("/", response_model=CourierResponse, status_code=status.HTTP_201_CREATED)
def create_courier(
    courier_in: CourierCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new courier"""
    courier = crud_courier.create(db, obj_in=courier_in)
    return courier

@router.put("/{courier_id}", response_model=CourierResponse)
def update_courier(
    courier_id: int,
    courier_in: CourierUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a courier"""
    courier = crud_courier.get(db, id=courier_id)
    if not courier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found"
        )
    courier = crud_courier.update(db, db_obj=courier, obj_in=courier_in)
    return courier

@router.delete("/{courier_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_courier(
    courier_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a courier"""
    courier = crud_courier.get(db, id=courier_id)
    if not courier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found"
        )
    crud_courier.remove(db, id=courier_id)
    return None
