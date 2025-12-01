from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.crud.operations import sla_definition, sla_tracking
from app.schemas.operations.sla import (
    SLADefinitionCreate, SLADefinitionUpdate, SLADefinitionResponse,
    SLATrackingCreate, SLATrackingUpdate, SLATrackingResponse,
    SLABreachReport, SLAComplianceReport, SLAType
)
from app.config.database import get_db
from app.core.dependencies import get_current_user

router = APIRouter()


# SLA Definitions Endpoints
@router.get("/definitions", response_model=List[SLADefinitionResponse])
def list_sla_definitions(
    skip: int = 0,
    limit: int = 100,
    sla_type: SLAType = Query(None, description="Filter by type"),
    zone_id: int = Query(None, description="Filter by zone"),
    active_only: bool = Query(True, description="Show only active SLAs"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all SLA definitions"""
    if sla_type:
        definitions = sla_definition.get_by_type(db, sla_type=sla_type)
    elif zone_id:
        definitions = sla_definition.get_by_zone(db, zone_id=zone_id)
    elif active_only:
        definitions = sla_definition.get_active_slas(db)
    else:
        definitions = sla_definition.get_multi(db, skip=skip, limit=limit)
    return definitions


@router.get("/definitions/{definition_id}", response_model=SLADefinitionResponse)
def get_sla_definition(
    definition_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific SLA definition by ID"""
    definition = sla_definition.get(db, id=definition_id)
    if not definition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SLA definition not found"
        )
    return definition


@router.post("/definitions", response_model=SLADefinitionResponse, status_code=status.HTTP_201_CREATED)
def create_sla_definition(
    definition_in: SLADefinitionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new SLA definition

    Business Logic:
    - Validates SLA code is unique
    - Sets target values and thresholds
    - Defines penalty for breaches
    - Applies to specific zones/service types/customer tiers
    - Sets effective date range
    """
    existing = sla_definition.get_by_code(db, sla_code=definition_in.sla_code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SLA definition with code '{definition_in.sla_code}' already exists"
        )

    # TODO: Validate zone exists if specified

    definition = sla_definition.create(db, obj_in=definition_in)
    return definition


@router.put("/definitions/{definition_id}", response_model=SLADefinitionResponse)
def update_sla_definition(
    definition_id: int,
    definition_in: SLADefinitionUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an SLA definition"""
    definition = sla_definition.get(db, id=definition_id)
    if not definition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SLA definition not found"
        )
    definition = sla_definition.update(db, db_obj=definition, obj_in=definition_in)
    return definition


# SLA Tracking Endpoints
@router.get("/tracking", response_model=List[SLATrackingResponse])
def list_sla_tracking(
    skip: int = 0,
    limit: int = 100,
    status: str = Query(None, description="Filter by status"),
    delivery_id: int = Query(None, description="Filter by delivery"),
    courier_id: int = Query(None, description="Filter by courier"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all SLA tracking records"""
    if delivery_id:
        trackings = sla_tracking.get_by_delivery(db, delivery_id=delivery_id)
    elif courier_id:
        trackings = sla_tracking.get_by_courier(db, courier_id=courier_id, skip=skip, limit=limit)
    elif status == "active":
        trackings = sla_tracking.get_active(db, skip=skip, limit=limit)
    elif status == "at_risk":
        trackings = sla_tracking.get_at_risk(db, skip=skip, limit=limit)
    elif status == "breached":
        trackings = sla_tracking.get_breached(db, skip=skip, limit=limit)
    else:
        trackings = sla_tracking.get_multi(db, skip=skip, limit=limit)
    return trackings


@router.get("/tracking/active", response_model=List[SLATrackingResponse])
def list_active_sla_tracking(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all active SLA tracking records

    Business Logic:
    - Returns SLAs currently being monitored
    - Status = ACTIVE
    - Not yet completed or breached
    """
    trackings = sla_tracking.get_active(db, skip=skip, limit=limit)
    return trackings


@router.get("/tracking/at-risk", response_model=List[SLATrackingResponse])
def list_at_risk_sla_tracking(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List SLAs at risk of being breached

    Business Logic:
    - Returns SLAs approaching deadline
    - Status = AT_RISK
    - Past warning threshold
    - Requires immediate attention
    - Sorted by target completion time (closest first)
    """
    trackings = sla_tracking.get_at_risk(db, skip=skip, limit=limit)
    return trackings


@router.get("/tracking/breached", response_model=List[SLATrackingResponse])
def list_breached_sla_tracking(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List breached SLAs

    Business Logic:
    - Returns SLAs that have been breached
    - Status = BREACHED or is_breached = True
    - Includes breach duration and severity
    - Used for penalty calculation and reporting
    - Sorted by breach time (most recent first)
    """
    trackings = sla_tracking.get_breached(db, skip=skip, limit=limit)
    return trackings


@router.get("/tracking/{tracking_id}", response_model=SLATrackingResponse)
def get_sla_tracking(
    tracking_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific SLA tracking record by ID"""
    tracking = sla_tracking.get(db, id=tracking_id)
    if not tracking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SLA tracking not found"
        )
    return tracking


@router.post("/tracking", response_model=SLATrackingResponse, status_code=status.HTTP_201_CREATED)
def create_sla_tracking(
    tracking_in: SLATrackingCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Start tracking SLA for a delivery/route/incident

    Business Logic:
    - Auto-generates tracking number
    - Links to SLA definition
    - Sets start time and target completion time
    - Calculates warning threshold
    - Monitors compliance in real-time
    - Status set to ACTIVE
    """
    # TODO: Validate SLA definition exists
    # TODO: Validate subject (delivery/route/courier/incident) exists

    tracking = sla_tracking.create_with_number(db, obj_in=tracking_in)
    return tracking


@router.put("/tracking/{tracking_id}", response_model=SLATrackingResponse)
def update_sla_tracking(
    tracking_id: int,
    tracking_in: SLATrackingUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update SLA tracking record"""
    tracking = sla_tracking.get(db, id=tracking_id)
    if not tracking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SLA tracking not found"
        )
    tracking = sla_tracking.update(db, db_obj=tracking, obj_in=tracking_in)
    return tracking


@router.post("/tracking/{tracking_id}/breach", response_model=SLATrackingResponse)
def report_sla_breach(
    tracking_id: int,
    breach: SLABreachReport,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Report SLA breach

    Business Logic:
    - Updates status to BREACHED
    - Records breach time and reason
    - Calculates breach duration
    - Sets breach severity (minor/major/critical)
    - Applies penalty if configured
    - Triggers escalation if required
    - Sends breach notifications
    """
    tracking = sla_tracking.get(db, id=tracking_id)
    if not tracking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SLA tracking not found"
        )

    if tracking.is_breached:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SLA already marked as breached"
        )

    # Mark as breached
    tracking = sla_tracking.mark_as_breached(
        db,
        tracking_id=tracking_id,
        breach_reason=breach.breach_reason,
        severity=breach.breach_severity
    )

    # Escalate if requested
    if breach.escalate and breach.escalated_to_id:
        tracking = sla_tracking.escalate(
            db,
            tracking_id=tracking_id,
            escalated_to_id=breach.escalated_to_id
        )

    # TODO: Apply penalty
    # TODO: Send notifications
    # TODO: Trigger escalation workflow

    return tracking


@router.post("/tracking/{tracking_id}/complete", response_model=SLATrackingResponse)
def complete_sla_tracking(
    tracking_id: int,
    actual_value: float,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Complete SLA tracking (successfully met)

    Business Logic:
    - Updates status to MET
    - Records actual completion time
    - Calculates variance from target
    - Calculates compliance score
    - Closes tracking record
    """
    tracking = sla_tracking.get(db, id=tracking_id)
    if not tracking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SLA tracking not found"
        )

    if tracking.status not in ["active", "at_risk"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only active or at-risk SLAs can be completed"
        )

    tracking = sla_tracking.mark_as_met(
        db,
        tracking_id=tracking_id,
        actual_value=actual_value
    )

    return tracking


@router.post("/tracking/{tracking_id}/escalate", response_model=SLATrackingResponse)
def escalate_sla_tracking(
    tracking_id: int,
    escalated_to_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Escalate SLA tracking to supervisor/manager

    Business Logic:
    - Marks as escalated
    - Assigns to escalation handler
    - Triggers escalation notifications
    - Requires immediate action
    """
    tracking = sla_tracking.get(db, id=tracking_id)
    if not tracking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SLA tracking not found"
        )

    tracking = sla_tracking.escalate(
        db,
        tracking_id=tracking_id,
        escalated_to_id=escalated_to_id
    )

    return tracking


@router.get("/compliance/report", response_model=SLAComplianceReport)
def get_compliance_report(
    sla_type: SLAType = Query(None, description="Filter by SLA type"),
    period: str = Query("month", regex="^(week|month|quarter|year)$"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get SLA compliance report

    Returns:
    - Total SLAs tracked
    - SLAs met vs breached
    - Compliance rate percentage
    - Average variance
    - Total penalties applied
    - Top breach reasons
    - Trend analysis
    - Performance by zone/courier
    """
    # TODO: Implement comprehensive compliance reporting
    # For now, return placeholder
    from decimal import Decimal

    return SLAComplianceReport(
        period=period,
        sla_type=sla_type or SLAType.DELIVERY_TIME,
        total_tracked=0,
        total_met=0,
        total_breached=0,
        total_at_risk=0,
        compliance_rate=0.0,
        avg_variance_percentage=0.0,
        total_penalties=Decimal("0.0"),
        top_breach_reasons=[]
    )
