"""COD Management API Routes"""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_organization, get_current_user, get_db
from app.models.operations.cod import CODStatus
from app.models.tenant.organization import Organization
from app.models.user import User
from app.schemas.operations import CODCreate, CODResponse, CODUpdate
from app.services.operations import cod_service

router = APIRouter()


@router.get("/", response_model=List[CODResponse])
def get_cod_transactions(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    courier_id: Optional[int] = None,
    status_filter: Optional[CODStatus] = Query(None, alias="status"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """
    Get list of COD transactions with filtering

    Filters:
    - courier_id: Filter by courier ID
    - status: Filter by COD status
    - start_date, end_date: Filter by collection date range
    """
    # Filter by status
    if status_filter:
        return cod_service.get_by_status(
            db, status=status_filter, skip=skip, limit=limit, organization_id=current_org.id
        )

    # Filter by date range
    if start_date and end_date:
        return cod_service.get_by_date_range(
            db,
            start_date=start_date,
            end_date=end_date,
            courier_id=courier_id,
            skip=skip,
            limit=limit,
            organization_id=current_org.id,
        )

    # Filter by courier
    if courier_id:
        return cod_service.get_by_courier(
            db, courier_id=courier_id, skip=skip, limit=limit, organization_id=current_org.id
        )

    return cod_service.get_multi(db, skip=skip, limit=limit, filters={"organization_id": current_org.id})


@router.post("/", response_model=CODResponse, status_code=status.HTTP_201_CREATED)
def create_cod_transaction(
    cod_in: CODCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Create new COD transaction"""
    return cod_service.create(db, obj_in=cod_in, organization_id=current_org.id)


@router.get("/pending", response_model=List[CODResponse])
def get_pending_cod(
    db: Session = Depends(get_db),
    courier_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get pending COD transactions"""
    return cod_service.get_pending(
        db, courier_id=courier_id, skip=skip, limit=limit, organization_id=current_org.id
    )


@router.get("/statistics", response_model=dict)
def get_cod_statistics(
    db: Session = Depends(get_db),
    courier_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get COD statistics"""
    return cod_service.get_statistics(
        db,
        courier_id=courier_id,
        start_date=start_date,
        end_date=end_date,
        organization_id=current_org.id,
    )


@router.get("/balance/{courier_id}", response_model=dict)
def get_courier_cod_balance(
    courier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get courier's COD balance"""
    return cod_service.get_courier_balance(
        db, courier_id=courier_id, organization_id=current_org.id
    )


@router.get("/{cod_id}", response_model=CODResponse)
def get_cod_transaction(
    cod_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get COD transaction by ID"""
    cod = cod_service.get(db, id=cod_id)
    if not cod or cod.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="COD transaction not found")
    return cod


@router.put("/{cod_id}", response_model=CODResponse)
def update_cod_transaction(
    cod_id: int,
    cod_in: CODUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update COD transaction"""
    cod = cod_service.get(db, id=cod_id)
    if not cod or cod.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="COD transaction not found")

    return cod_service.update(db, db_obj=cod, obj_in=cod_in)


@router.delete("/{cod_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cod_transaction(
    cod_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Delete COD transaction"""
    cod = cod_service.get(db, id=cod_id)
    if not cod or cod.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="COD transaction not found")

    cod_service.delete(db, id=cod_id)
    return None


@router.patch("/{cod_id}/collect", response_model=CODResponse)
def mark_cod_as_collected(
    cod_id: int,
    reference_number: Optional[str] = Body(None),
    notes: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Mark COD as collected"""
    # Verify COD belongs to organization
    existing = cod_service.get(db, id=cod_id)
    if not existing or existing.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="COD transaction not found")

    cod = cod_service.mark_as_collected(
        db, cod_id=cod_id, reference_number=reference_number, notes=notes
    )
    if not cod:
        raise HTTPException(status_code=404, detail="COD transaction not found")
    return cod


@router.patch("/{cod_id}/deposit", response_model=CODResponse)
def mark_cod_as_deposited(
    cod_id: int,
    deposit_date: Optional[date] = Body(None),
    reference_number: Optional[str] = Body(None),
    notes: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Mark COD as deposited"""
    # Verify COD belongs to organization
    existing = cod_service.get(db, id=cod_id)
    if not existing or existing.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="COD transaction not found")

    cod = cod_service.mark_as_deposited(
        db, cod_id=cod_id, deposit_date=deposit_date, reference_number=reference_number, notes=notes
    )
    if not cod:
        raise HTTPException(status_code=404, detail="COD transaction not found")
    return cod


@router.patch("/{cod_id}/reconcile", response_model=CODResponse)
def mark_cod_as_reconciled(
    cod_id: int,
    notes: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Mark COD as reconciled"""
    # Verify COD belongs to organization
    existing = cod_service.get(db, id=cod_id)
    if not existing or existing.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="COD transaction not found")

    cod = cod_service.mark_as_reconciled(db, cod_id=cod_id, notes=notes)
    if not cod:
        raise HTTPException(status_code=404, detail="COD transaction not found")
    return cod


@router.post("/bulk-deposit", response_model=dict)
def bulk_deposit_cod(
    cod_ids: List[int] = Body(...),
    deposit_date: Optional[date] = Body(None),
    reference_number: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Mark multiple COD transactions as deposited"""
    # Verify all CODs belong to organization
    for cod_id in cod_ids:
        existing = cod_service.get(db, id=cod_id)
        if not existing or existing.organization_id != current_org.id:
            raise HTTPException(status_code=404, detail=f"COD transaction {cod_id} not found")

    updated_count = cod_service.bulk_deposit(
        db, cod_ids=cod_ids, deposit_date=deposit_date, reference_number=reference_number
    )
    return {
        "message": f"Successfully deposited {updated_count} COD transactions",
        "updated_count": updated_count,
    }


@router.post("/settle/{courier_id}", response_model=dict)
def settle_courier_cod(
    courier_id: int,
    deposit_date: Optional[date] = Body(None),
    reference_number: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Settle all pending and collected COD for a courier"""
    return cod_service.settle_courier_cod(
        db,
        courier_id=courier_id,
        deposit_date=deposit_date,
        reference_number=reference_number,
        organization_id=current_org.id,
    )
