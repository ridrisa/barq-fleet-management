from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.crud.operations import delivery as crud_delivery
from app.schemas.operations.delivery import DeliveryCreate, DeliveryResponse, DeliveryUpdate

router = APIRouter()


@router.get("/", response_model=List[DeliveryResponse])
def list_deliveries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all deliveries"""
    deliveries = crud_delivery.get_multi(db, skip=skip, limit=limit)
    return deliveries


@router.get("/{delivery_id}", response_model=DeliveryResponse)
def get_delivery(
    delivery_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Get a specific delivery by ID"""
    delivery = crud_delivery.get(db, id=delivery_id)
    if not delivery:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")
    return delivery


@router.post("/", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
def create_delivery(
    delivery_in: DeliveryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new delivery"""
    delivery = crud_delivery.create(db, obj_in=delivery_in)
    return delivery


@router.put("/{delivery_id}", response_model=DeliveryResponse)
def update_delivery(
    delivery_id: int,
    delivery_in: DeliveryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a delivery"""
    delivery = crud_delivery.get(db, id=delivery_id)
    if not delivery:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")
    delivery = crud_delivery.update(db, db_obj=delivery, obj_in=delivery_in)
    return delivery


@router.delete("/{delivery_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_delivery(
    delivery_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Delete a delivery"""
    delivery = crud_delivery.get(db, id=delivery_id)
    if not delivery:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")
    crud_delivery.remove(db, id=delivery_id)
    return None
