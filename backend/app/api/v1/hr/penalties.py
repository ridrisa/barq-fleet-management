"""
Penalty Management API for HR module.

Handles CRUD operations for courier penalties/deductions.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_organization, get_current_user
from app.models.tenant.organization import Organization
from app.models.hr.penalty import Penalty, PenaltyType, PenaltyStatus
from app.services.hr.penalty_service import penalty_service
from app.models.fleet.courier import Courier

router = APIRouter()


# Pydantic schemas
class PenaltyCreate(BaseModel):
    """Schema for creating a penalty"""
    courier_id: int = Field(..., description="Courier ID")
    penalty_type: PenaltyType = Field(..., description="Type of penalty")
    amount: Decimal = Field(..., gt=0, description="Penalty amount in SAR")
    reason: str = Field(..., min_length=10, description="Detailed reason for penalty")
    incident_date: Optional[date] = Field(None, description="Date of incident")
    incident_id: Optional[int] = Field(None, description="Related incident ID")
    sla_tracking_id: Optional[int] = Field(None, description="Related SLA tracking ID")
    delivery_id: Optional[int] = Field(None, description="Related delivery ID")
    notes: Optional[str] = Field(None, description="Additional notes")


class PenaltyUpdate(BaseModel):
    """Schema for updating a penalty"""
    penalty_type: Optional[PenaltyType] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    reason: Optional[str] = Field(None, min_length=10)
    incident_date: Optional[date] = None
    notes: Optional[str] = None


class PenaltyApproval(BaseModel):
    """Schema for approving/rejecting a penalty"""
    approved: bool = Field(..., description="True to approve, False to reject")
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection")


class PenaltyAppeal(BaseModel):
    """Schema for appealing a penalty"""
    appeal_reason: str = Field(..., min_length=10, description="Reason for appeal")


class PenaltyAppealResolution(BaseModel):
    """Schema for resolving a penalty appeal"""
    resolution: str = Field(..., min_length=10, description="Resolution details")
    waive: bool = Field(False, description="True to waive the penalty")


class PenaltyResponse(BaseModel):
    """Penalty response schema"""
    id: int
    courier_id: int
    penalty_type: str
    status: str
    amount: float
    reason: str
    incident_date: date
    reference_number: Optional[str] = None
    incident_id: Optional[int] = None
    sla_tracking_id: Optional[int] = None
    delivery_id: Optional[int] = None
    created_by_id: Optional[int] = None
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    appeal_reason: Optional[str] = None
    appeal_resolved_at: Optional[datetime] = None
    appeal_resolution: Optional[str] = None
    salary_id: Optional[int] = None
    applied_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PenaltySummary(BaseModel):
    """Summary statistics for penalties"""
    total_count: int
    total_amount: float
    pending_count: int
    approved_count: int
    applied_count: int
    by_type: dict


@router.get("/", response_model=List[PenaltyResponse])
def list_penalties(
    skip: int = 0,
    limit: int = 100,
    courier_id: Optional[int] = Query(None, description="Filter by courier"),
    penalty_type: Optional[PenaltyType] = Query(None, description="Filter by type"),
    penalty_status: Optional[PenaltyStatus] = Query(None, alias="status", description="Filter by status"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List all penalties with optional filters"""
    penalties = penalty_service.get_multi(
        db,
        organization_id=current_org.id,
        skip=skip,
        limit=limit,
        courier_id=courier_id,
        penalty_type=penalty_type,
        status=penalty_status,
    )
    return penalties


@router.get("/pending", response_model=List[PenaltyResponse])
def list_pending_penalties(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List all pending penalties awaiting approval"""
    penalties = penalty_service.get_pending(
        db,
        organization_id=current_org.id,
        skip=skip,
        limit=limit,
    )
    return penalties


@router.get("/courier/{courier_id}", response_model=List[PenaltyResponse])
def list_courier_penalties(
    courier_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List all penalties for a specific courier"""
    # Validate courier exists
    courier = db.query(Courier).filter(
        Courier.id == courier_id,
        Courier.organization_id == current_org.id,
    ).first()
    if not courier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found",
        )

    penalties = penalty_service.get_by_courier(
        db,
        courier_id=courier_id,
        organization_id=current_org.id,
        skip=skip,
        limit=limit,
    )
    return penalties


@router.get("/courier/{courier_id}/summary", response_model=PenaltySummary)
def get_courier_penalty_summary(
    courier_id: int,
    year: Optional[int] = Query(None, description="Filter by year"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get penalty summary for a courier"""
    penalties = penalty_service.get_by_courier(
        db,
        courier_id=courier_id,
        organization_id=current_org.id,
        skip=0,
        limit=1000,
    )

    # Filter by year/month if specified
    if year:
        penalties = [p for p in penalties if p.incident_date.year == year]
    if month:
        penalties = [p for p in penalties if p.incident_date.month == month]

    # Calculate statistics
    total_amount = sum(float(p.amount) for p in penalties)
    pending_count = len([p for p in penalties if p.status == PenaltyStatus.PENDING])
    approved_count = len([p for p in penalties if p.status == PenaltyStatus.APPROVED])
    applied_count = len([p for p in penalties if p.status == PenaltyStatus.APPLIED])

    # Group by type
    by_type = {}
    for p in penalties:
        type_str = p.penalty_type.value
        if type_str not in by_type:
            by_type[type_str] = {"count": 0, "amount": 0}
        by_type[type_str]["count"] += 1
        by_type[type_str]["amount"] += float(p.amount)

    return PenaltySummary(
        total_count=len(penalties),
        total_amount=total_amount,
        pending_count=pending_count,
        approved_count=approved_count,
        applied_count=applied_count,
        by_type=by_type,
    )


@router.get("/{penalty_id}", response_model=PenaltyResponse)
def get_penalty(
    penalty_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get a specific penalty by ID"""
    penalty = penalty_service.get(db, id=penalty_id)
    if not penalty or penalty.organization_id != current_org.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Penalty not found",
        )
    return penalty


@router.post("/", response_model=PenaltyResponse, status_code=status.HTTP_201_CREATED)
def create_penalty(
    penalty_in: PenaltyCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Create a new penalty

    Business Logic:
    - Validates courier exists
    - Auto-generates reference number
    - Sets status to PENDING
    - Requires approval before being applied to salary
    """
    # Validate courier exists
    courier = db.query(Courier).filter(
        Courier.id == penalty_in.courier_id,
        Courier.organization_id == current_org.id,
    ).first()
    if not courier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found",
        )

    created_by_id = current_user.id if hasattr(current_user, "id") else None

    penalty = penalty_service.create(
        db,
        courier_id=penalty_in.courier_id,
        penalty_type=penalty_in.penalty_type,
        amount=penalty_in.amount,
        reason=penalty_in.reason,
        organization_id=current_org.id,
        incident_date=penalty_in.incident_date,
        incident_id=penalty_in.incident_id,
        sla_tracking_id=penalty_in.sla_tracking_id,
        delivery_id=penalty_in.delivery_id,
        created_by_id=created_by_id,
        notes=penalty_in.notes,
    )
    return penalty


@router.put("/{penalty_id}", response_model=PenaltyResponse)
def update_penalty(
    penalty_id: int,
    penalty_in: PenaltyUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update a penalty (only if pending)"""
    penalty = penalty_service.get(db, id=penalty_id)
    if not penalty or penalty.organization_id != current_org.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Penalty not found",
        )

    if not penalty.is_editable:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot edit penalty that is not in pending status",
        )

    penalty = penalty_service.update(
        db,
        penalty=penalty,
        penalty_type=penalty_in.penalty_type,
        amount=penalty_in.amount,
        reason=penalty_in.reason,
        incident_date=penalty_in.incident_date,
        notes=penalty_in.notes,
    )
    return penalty


@router.post("/{penalty_id}/approve", response_model=PenaltyResponse)
def approve_or_reject_penalty(
    penalty_id: int,
    approval: PenaltyApproval,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Approve or reject a pending penalty"""
    penalty = penalty_service.get(db, id=penalty_id)
    if not penalty or penalty.organization_id != current_org.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Penalty not found",
        )

    if penalty.status != PenaltyStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only approve/reject pending penalties",
        )

    user_id = current_user.id if hasattr(current_user, "id") else 1

    if approval.approved:
        penalty = penalty_service.approve(db, penalty=penalty, approved_by_id=user_id)
    else:
        penalty = penalty_service.reject(
            db,
            penalty=penalty,
            rejected_by_id=user_id,
            rejection_reason=approval.rejection_reason,
        )

    return penalty


@router.post("/{penalty_id}/appeal", response_model=PenaltyResponse)
def appeal_penalty(
    penalty_id: int,
    appeal: PenaltyAppeal,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Appeal a penalty"""
    penalty = penalty_service.get(db, id=penalty_id)
    if not penalty or penalty.organization_id != current_org.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Penalty not found",
        )

    if not penalty.is_appealable:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This penalty cannot be appealed",
        )

    penalty = penalty_service.appeal(db, penalty=penalty, appeal_reason=appeal.appeal_reason)
    return penalty


@router.post("/{penalty_id}/resolve-appeal", response_model=PenaltyResponse)
def resolve_penalty_appeal(
    penalty_id: int,
    resolution: PenaltyAppealResolution,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Resolve a penalty appeal"""
    penalty = penalty_service.get(db, id=penalty_id)
    if not penalty or penalty.organization_id != current_org.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Penalty not found",
        )

    if penalty.status != PenaltyStatus.APPEALED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only resolve appealed penalties",
        )

    user_id = current_user.id if hasattr(current_user, "id") else 1

    penalty = penalty_service.resolve_appeal(
        db,
        penalty=penalty,
        resolution=resolution.resolution,
        waive=resolution.waive,
        resolved_by_id=user_id,
    )
    return penalty


@router.delete("/{penalty_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_penalty(
    penalty_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Delete a penalty (only if pending)"""
    penalty = penalty_service.get(db, id=penalty_id)
    if not penalty or penalty.organization_id != current_org.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Penalty not found",
        )

    if not penalty.is_editable:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete penalty that is not in pending status",
        )

    penalty_service.delete(db, id=penalty_id)
    return None
