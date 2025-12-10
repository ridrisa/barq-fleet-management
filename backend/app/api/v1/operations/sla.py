from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_organization, get_current_user
from app.models.tenant.organization import Organization
from app.services.operations import sla_definition_service, sla_tracking_service
from app.schemas.operations.sla import (
    SLABreachReport,
    SLAComplianceReport,
    SLADefinitionCreate,
    SLADefinitionResponse,
    SLADefinitionUpdate,
    SLATrackingCreate,
    SLATrackingResponse,
    SLATrackingUpdate,
    SLAType,
)

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
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List all SLA definitions"""
    if sla_type:
        definitions = sla_definition_service.get_by_type(
            db, sla_type=sla_type, organization_id=current_org.id
        )
    elif zone_id:
        definitions = sla_definition_service.get_by_zone(
            db, zone_id=zone_id, organization_id=current_org.id
        )
    elif active_only:
        definitions = sla_definition_service.get_active_slas(db, organization_id=current_org.id)
    else:
        definitions = sla_definition_service.get_multi(
            db, skip=skip, limit=limit, organization_id=current_org.id
        )
    return definitions


@router.get("/definitions/{definition_id}", response_model=SLADefinitionResponse)
def get_sla_definition(
    definition_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get a specific SLA definition by ID"""
    definition = sla_definition_service.get(db, id=definition_id)
    if not definition or definition.organization_id != current_org.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="SLA definition not found"
        )
    return definition


@router.post(
    "/definitions", response_model=SLADefinitionResponse, status_code=status.HTTP_201_CREATED
)
def create_sla_definition(
    definition_in: SLADefinitionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Create a new SLA definition

    Business Logic:
    - Validates SLA code is unique within organization
    - Sets target values and thresholds
    - Defines penalty for breaches
    - Applies to specific zones/service types/customer tiers
    - Sets effective date range
    """
    existing = sla_definition_service.get_by_code(
        db, sla_code=definition_in.sla_code, organization_id=current_org.id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SLA definition with code '{definition_in.sla_code}' already exists",
        )

    # TODO: Validate zone exists if specified

    definition = sla_definition_service.create(db, obj_in=definition_in, organization_id=current_org.id)
    return definition


@router.put("/definitions/{definition_id}", response_model=SLADefinitionResponse)
def update_sla_definition(
    definition_id: int,
    definition_in: SLADefinitionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update an SLA definition"""
    definition = sla_definition_service.get(db, id=definition_id)
    if not definition or definition.organization_id != current_org.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="SLA definition not found"
        )
    definition = sla_definition_service.update(db, db_obj=definition, obj_in=definition_in)
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
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List all SLA tracking records"""
    if delivery_id:
        trackings = sla_tracking_service.get_by_delivery(
            db, delivery_id=delivery_id, organization_id=current_org.id
        )
    elif courier_id:
        trackings = sla_tracking_service.get_by_courier(
            db, courier_id=courier_id, skip=skip, limit=limit, organization_id=current_org.id
        )
    elif status == "active":
        trackings = sla_tracking_service.get_active(
            db, skip=skip, limit=limit, organization_id=current_org.id
        )
    elif status == "at_risk":
        trackings = sla_tracking_service.get_at_risk(
            db, skip=skip, limit=limit, organization_id=current_org.id
        )
    elif status == "breached":
        trackings = sla_tracking_service.get_breached(
            db, skip=skip, limit=limit, organization_id=current_org.id
        )
    else:
        trackings = sla_tracking_service.get_multi(
            db, skip=skip, limit=limit, organization_id=current_org.id
        )
    return trackings


@router.get("/tracking/active", response_model=List[SLATrackingResponse])
def list_active_sla_tracking(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List all active SLA tracking records

    Business Logic:
    - Returns SLAs currently being monitored
    - Status = ACTIVE
    - Not yet completed or breached
    """
    trackings = sla_tracking_service.get_active(db, skip=skip, limit=limit, organization_id=current_org.id)
    return trackings


@router.get("/tracking/at-risk", response_model=List[SLATrackingResponse])
def list_at_risk_sla_tracking(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List SLAs at risk of being breached

    Business Logic:
    - Returns SLAs approaching deadline
    - Status = AT_RISK
    - Past warning threshold
    - Requires immediate attention
    - Sorted by target completion time (closest first)
    """
    trackings = sla_tracking_service.get_at_risk(db, skip=skip, limit=limit, organization_id=current_org.id)
    return trackings


@router.get("/tracking/breached", response_model=List[SLATrackingResponse])
def list_breached_sla_tracking(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List breached SLAs

    Business Logic:
    - Returns SLAs that have been breached
    - Status = BREACHED or is_breached = True
    - Includes breach duration and severity
    - Used for penalty calculation and reporting
    - Sorted by breach time (most recent first)
    """
    trackings = sla_tracking_service.get_breached(
        db, skip=skip, limit=limit, organization_id=current_org.id
    )
    return trackings


@router.get("/tracking/{tracking_id}", response_model=SLATrackingResponse)
def get_sla_tracking(
    tracking_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get a specific SLA tracking record by ID"""
    tracking = sla_tracking_service.get(db, id=tracking_id)
    if not tracking or tracking.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SLA tracking not found")
    return tracking


@router.post("/tracking", response_model=SLATrackingResponse, status_code=status.HTTP_201_CREATED)
def create_sla_tracking(
    tracking_in: SLATrackingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
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

    tracking = sla_tracking_service.create_with_number(
        db, obj_in=tracking_in, organization_id=current_org.id
    )
    return tracking


@router.put("/tracking/{tracking_id}", response_model=SLATrackingResponse)
def update_sla_tracking(
    tracking_id: int,
    tracking_in: SLATrackingUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update SLA tracking record"""
    tracking = sla_tracking_service.get(db, id=tracking_id)
    if not tracking or tracking.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SLA tracking not found")
    tracking = sla_tracking_service.update(db, db_obj=tracking, obj_in=tracking_in)
    return tracking


@router.post("/tracking/{tracking_id}/breach", response_model=SLATrackingResponse)
def report_sla_breach(
    tracking_id: int,
    breach: SLABreachReport,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
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
    tracking = sla_tracking_service.get(db, id=tracking_id)
    if not tracking or tracking.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SLA tracking not found")

    if tracking.is_breached:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="SLA already marked as breached"
        )

    # Mark as breached
    tracking = sla_tracking_service.mark_as_breached(
        db,
        tracking_id=tracking_id,
        breach_reason=breach.breach_reason,
        severity=breach.breach_severity,
    )

    # Escalate if requested
    if breach.escalate and breach.escalated_to_id:
        tracking = sla_tracking_service.escalate(
            db, tracking_id=tracking_id, escalated_to_id=breach.escalated_to_id
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
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Complete SLA tracking (successfully met)

    Business Logic:
    - Updates status to MET
    - Records actual completion time
    - Calculates variance from target
    - Calculates compliance score
    - Closes tracking record
    """
    tracking = sla_tracking_service.get(db, id=tracking_id)
    if not tracking or tracking.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SLA tracking not found")

    if tracking.status not in ["active", "at_risk"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only active or at-risk SLAs can be completed",
        )

    tracking = sla_tracking_service.mark_as_met(db, tracking_id=tracking_id, actual_value=actual_value)

    return tracking


@router.post("/tracking/{tracking_id}/escalate", response_model=SLATrackingResponse)
def escalate_sla_tracking(
    tracking_id: int,
    escalated_to_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Escalate SLA tracking to supervisor/manager

    Business Logic:
    - Marks as escalated
    - Assigns to escalation handler
    - Triggers escalation notifications
    - Requires immediate action
    """
    tracking = sla_tracking_service.get(db, id=tracking_id)
    if not tracking or tracking.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SLA tracking not found")

    tracking = sla_tracking_service.escalate(db, tracking_id=tracking_id, escalated_to_id=escalated_to_id)

    return tracking


@router.get("/compliance/report", response_model=SLAComplianceReport)
def get_compliance_report(
    sla_type: SLAType = Query(None, description="Filter by SLA type"),
    period: str = Query("month", regex="^(week|month|quarter|year)$"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
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
    from datetime import datetime, timedelta
    from decimal import Decimal
    from sqlalchemy import func
    from app.models.operations.sla import SLATracking

    # Calculate date range
    now = datetime.utcnow()
    if period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    elif period == "quarter":
        start_date = now - timedelta(days=90)
    else:  # year
        start_date = now - timedelta(days=365)

    # Base query
    base_query = db.query(SLATracking).filter(
        SLATracking.organization_id == current_org.id,
        SLATracking.start_time >= start_date,
    )

    if sla_type:
        base_query = base_query.filter(SLATracking.sla_type == sla_type.value)

    # Calculate metrics
    total_tracked = base_query.count()
    total_met = base_query.filter(SLATracking.status == "met").count()
    total_breached = base_query.filter(SLATracking.is_breached == True).count()
    total_at_risk = base_query.filter(SLATracking.status == "at_risk").count()

    # Compliance rate
    compliance_rate = (total_met / total_tracked * 100) if total_tracked > 0 else 0.0

    # Average variance (for met SLAs)
    met_records = base_query.filter(
        SLATracking.status == "met",
        SLATracking.actual_value.isnot(None),
        SLATracking.target_value.isnot(None),
    ).all()

    avg_variance = 0.0
    if met_records:
        variances = []
        for r in met_records:
            if r.target_value and r.actual_value:
                variance = ((float(r.actual_value) - float(r.target_value)) / float(r.target_value)) * 100
                variances.append(variance)
        if variances:
            avg_variance = sum(variances) / len(variances)

    # Total penalties
    total_penalties = db.query(func.sum(SLATracking.penalty_amount)).filter(
        SLATracking.organization_id == current_org.id,
        SLATracking.start_time >= start_date,
        SLATracking.penalty_amount.isnot(None),
    ).scalar() or Decimal("0.0")

    # Top breach reasons
    breach_reasons = db.query(
        SLATracking.breach_reason,
        func.count(SLATracking.id).label("count")
    ).filter(
        SLATracking.organization_id == current_org.id,
        SLATracking.start_time >= start_date,
        SLATracking.is_breached == True,
        SLATracking.breach_reason.isnot(None),
    ).group_by(SLATracking.breach_reason).order_by(func.count(SLATracking.id).desc()).limit(5).all()

    top_breach_reasons = [{"reason": r[0], "count": r[1]} for r in breach_reasons]

    return SLAComplianceReport(
        period=period,
        sla_type=sla_type or SLAType.DELIVERY_TIME,
        total_tracked=total_tracked,
        total_met=total_met,
        total_breached=total_breached,
        total_at_risk=total_at_risk,
        compliance_rate=compliance_rate,
        avg_variance_percentage=avg_variance,
        total_penalties=Decimal(str(total_penalties)),
        top_breach_reasons=top_breach_reasons,
    )
