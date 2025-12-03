"""Asset Management API Routes"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.orm import Session
from datetime import date

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.hr import (
    AssetCreate, AssetUpdate, AssetResponse, AssetType, AssetStatus
)
from app.services.hr import asset_service


router = APIRouter()


@router.get("/", response_model=List[AssetResponse])
def get_assets(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    courier_id: Optional[int] = None,
    asset_type: Optional[AssetType] = None,
    status: Optional[AssetStatus] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Get list of assets with filtering

    Filters:
    - courier_id: Filter by courier ID
    - asset_type: Filter by asset type (uniform, equipment, vehicle_accessory, document, other)
    - status: Filter by status (assigned, returned, damaged, lost)
    """
    # If courier_id filter is provided
    if courier_id:
        return asset_service.get_by_courier(
            db, courier_id=courier_id, skip=skip, limit=limit
        )

    # Build dynamic filters
    filters = {}
    if asset_type:
        filters["asset_type"] = asset_type
    if status:
        filters["status"] = status

    return asset_service.get_multi(db, skip=skip, limit=limit, filters=filters)


@router.post("/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset(
    asset_in: AssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new asset assignment"""
    return asset_service.create(db, obj_in=asset_in)


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get asset by ID"""
    asset = asset_service.get(db, id=asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: int,
    asset_in: AssetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update asset"""
    asset = asset_service.get(db, id=asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    return asset_service.update(db, db_obj=asset, obj_in=asset_in)


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete asset"""
    asset = asset_service.get(db, id=asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    asset_service.delete(db, id=asset_id)
    return None


@router.get("/courier/{courier_id}", response_model=List[AssetResponse])
def get_courier_assets(
    courier_id: int,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get all assets assigned to a specific courier"""
    return asset_service.get_by_courier(
        db, courier_id=courier_id, skip=skip, limit=limit
    )


@router.post("/{asset_id}/return", response_model=AssetResponse)
def return_asset(
    asset_id: int,
    return_date: Optional[date] = Body(None, embed=True),
    notes: Optional[str] = Body(None, embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark an asset as returned

    Updates the status to 'returned' and records the return date
    """
    asset = asset_service.get(db, id=asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if asset.status == AssetStatus.RETURNED:
        raise HTTPException(
            status_code=400,
            detail="Asset has already been returned"
        )

    updated_asset = asset_service.return_asset(
        db,
        asset_id=asset_id,
        return_date=return_date or date.today(),
        notes=notes
    )

    return updated_asset


@router.post("/{asset_id}/mark-damaged", response_model=AssetResponse)
def mark_asset_damaged(
    asset_id: int,
    damage_date: Optional[date] = Body(None, embed=True),
    notes: Optional[str] = Body(None, embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark an asset as damaged

    Updates the status to 'damaged' and records damage details
    """
    asset = asset_service.get(db, id=asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if asset.status != AssetStatus.ASSIGNED:
        raise HTTPException(
            status_code=400,
            detail="Can only mark assigned assets as damaged"
        )

    updated_asset = asset_service.mark_damaged(
        db,
        asset_id=asset_id,
        damage_date=damage_date or date.today(),
        notes=notes
    )

    return updated_asset


@router.post("/{asset_id}/mark-lost", response_model=AssetResponse)
def mark_asset_lost(
    asset_id: int,
    lost_date: Optional[date] = Body(None, embed=True),
    notes: Optional[str] = Body(None, embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark an asset as lost

    Updates the status to 'lost' and records loss details
    """
    asset = asset_service.get(db, id=asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if asset.status != AssetStatus.ASSIGNED:
        raise HTTPException(
            status_code=400,
            detail="Can only mark assigned assets as lost"
        )

    updated_asset = asset_service.mark_lost(
        db,
        asset_id=asset_id,
        lost_date=lost_date or date.today(),
        notes=notes
    )

    return updated_asset


@router.get("/statistics", response_model=dict)
def get_asset_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get asset statistics

    Returns:
    - total: Total number of assets
    - assigned: Number of currently assigned assets
    - returned: Number of returned assets
    - damaged: Number of damaged assets
    - lost: Number of lost assets
    - by_type: Breakdown by asset type
    """
    return asset_service.get_statistics(db)
