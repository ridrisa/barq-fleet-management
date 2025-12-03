"""Delivery Management API Routes"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.orm import Session
from datetime import date

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.operations.delivery import DeliveryStatus
from app.schemas.operations import (
    DeliveryCreate, DeliveryUpdate, DeliveryResponse
)
from app.services.operations import delivery_service


router = APIRouter()


@router.get("/", response_model=List[DeliveryResponse])
def get_deliveries(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    courier_id: Optional[int] = None,
    status_filter: Optional[DeliveryStatus] = Query(None, alias="status"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    tracking_number: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Get list of deliveries with filtering

    Filters:
    - courier_id: Filter by courier ID
    - status: Filter by delivery status
    - start_date: Filter by start date
    - end_date: Filter by end date
    - tracking_number: Search by tracking number
    """
    # Search by tracking number
    if tracking_number:
        delivery = delivery_service.get_by_tracking_number(
            db, tracking_number=tracking_number
        )
        return [delivery] if delivery else []

    # Filter by courier
    if courier_id:
        return delivery_service.get_by_courier(
            db, courier_id=courier_id, skip=skip, limit=limit
        )

    # Filter by status
    if status_filter:
        return delivery_service.get_by_status(
            db, status=status_filter, skip=skip, limit=limit
        )

    # Filter by date range
    if start_date and end_date:
        return delivery_service.get_deliveries_by_date_range(
            db,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit
        )

    return delivery_service.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
def create_delivery(
    delivery_in: DeliveryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new delivery"""
    # Check if tracking number already exists
    existing = delivery_service.get_by_tracking_number(
        db, tracking_number=delivery_in.tracking_number
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Delivery with this tracking number already exists"
        )

    return delivery_service.create(db, obj_in=delivery_in)


@router.get("/pending", response_model=List[DeliveryResponse])
def get_pending_deliveries(
    db: Session = Depends(get_db),
    courier_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get pending deliveries"""
    return delivery_service.get_pending_deliveries(
        db, courier_id=courier_id, skip=skip, limit=limit
    )


@router.get("/cod", response_model=List[DeliveryResponse])
def get_cod_deliveries(
    db: Session = Depends(get_db),
    courier_id: Optional[int] = None,
    status_filter: Optional[DeliveryStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get deliveries with COD amount"""
    return delivery_service.get_cod_deliveries(
        db,
        courier_id=courier_id,
        status=status_filter,
        skip=skip,
        limit=limit
    )


@router.get("/statistics", response_model=dict)
def get_delivery_statistics(
    db: Session = Depends(get_db),
    courier_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
):
    """Get delivery statistics"""
    return delivery_service.get_statistics(
        db,
        courier_id=courier_id,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/{delivery_id}", response_model=DeliveryResponse)
def get_delivery(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get delivery by ID"""
    delivery = delivery_service.get(db, id=delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery


@router.put("/{delivery_id}", response_model=DeliveryResponse)
def update_delivery(
    delivery_id: int,
    delivery_in: DeliveryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update delivery"""
    delivery = delivery_service.get(db, id=delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    return delivery_service.update(db, db_obj=delivery, obj_in=delivery_in)


@router.delete("/{delivery_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_delivery(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete delivery"""
    delivery = delivery_service.get(db, id=delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    delivery_service.delete(db, id=delivery_id)
    return None


@router.patch("/{delivery_id}/status", response_model=DeliveryResponse)
def update_delivery_status(
    delivery_id: int,
    status_update: DeliveryStatus = Body(...),
    notes: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update delivery status"""
    delivery = delivery_service.update_status(
        db, delivery_id=delivery_id, status=status_update, notes=notes
    )
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery


@router.patch("/{delivery_id}/assign", response_model=DeliveryResponse)
def assign_delivery_to_courier(
    delivery_id: int,
    courier_id: int = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Assign delivery to a courier"""
    delivery = delivery_service.assign_to_courier(
        db, delivery_id=delivery_id, courier_id=courier_id
    )
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery
