from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date
from app.crud.operations import quality_metric, quality_inspection
from app.schemas.operations.quality import (
    QualityMetricCreate, QualityMetricUpdate, QualityMetricResponse,
    QualityInspectionCreate, QualityInspectionUpdate, QualityInspectionResponse,
    QualityInspectionComplete, QualityReport, QualityMetricType
)
from app.core.database import get_db
from app.core.dependencies import get_current_user

router = APIRouter()


# Quality Metrics Endpoints
@router.get("/metrics", response_model=List[QualityMetricResponse])
def list_quality_metrics(
    skip: int = 0,
    limit: int = 100,
    metric_type: QualityMetricType = Query(None, description="Filter by type"),
    active_only: bool = Query(True, description="Show only active metrics"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all quality metrics"""
    if metric_type:
        metrics = quality_metric.get_by_type(db, metric_type=metric_type)
    elif active_only:
        metrics = quality_metric.get_active_metrics(db)
    else:
        metrics = quality_metric.get_multi(db, skip=skip, limit=limit)
    return metrics


@router.get("/metrics/critical", response_model=List[QualityMetricResponse])
def list_critical_metrics(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List critical quality metrics"""
    metrics = quality_metric.get_critical_metrics(db)
    return metrics


@router.post("/metrics", response_model=QualityMetricResponse, status_code=status.HTTP_201_CREATED)
def create_quality_metric(
    metric_in: QualityMetricCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new quality metric

    Business Logic:
    - Validates metric code is unique
    - Sets thresholds and targets
    - Defines weight for overall quality score
    - Marks as critical if applicable
    """
    existing = quality_metric.get_by_code(db, metric_code=metric_in.metric_code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Metric with code '{metric_in.metric_code}' already exists"
        )

    metric = quality_metric.create(db, obj_in=metric_in)
    return metric


@router.put("/metrics/{metric_id}", response_model=QualityMetricResponse)
def update_quality_metric(
    metric_id: int,
    metric_in: QualityMetricUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a quality metric"""
    metric = quality_metric.get(db, id=metric_id)
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quality metric not found"
        )
    metric = quality_metric.update(db, db_obj=metric, obj_in=metric_in)
    return metric


# Quality Inspections Endpoints
@router.get("/inspections", response_model=List[QualityInspectionResponse])
def list_inspections(
    skip: int = 0,
    limit: int = 100,
    courier_id: int = Query(None, description="Filter by courier"),
    vehicle_id: int = Query(None, description="Filter by vehicle"),
    status: str = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all quality inspections"""
    if courier_id:
        inspections = quality_inspection.get_by_courier(db, courier_id=courier_id, skip=skip, limit=limit)
    elif vehicle_id:
        inspections = quality_inspection.get_by_vehicle(db, vehicle_id=vehicle_id, skip=skip, limit=limit)
    else:
        inspections = quality_inspection.get_multi(db, skip=skip, limit=limit)
    return inspections


@router.get("/inspections/failed", response_model=List[QualityInspectionResponse])
def list_failed_inspections(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all failed inspections

    Business Logic:
    - Returns inspections that did not pass
    - Used for corrective action tracking
    - Sorted by inspection date (most recent first)
    """
    inspections = quality_inspection.get_failed_inspections(db, skip=skip, limit=limit)
    return inspections


@router.get("/inspections/followup", response_model=List[QualityInspectionResponse])
def list_followup_required(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List inspections requiring follow-up

    Business Logic:
    - Returns inspections with requires_followup = True
    - Excludes already completed follow-ups
    - Requires action from quality team
    """
    inspections = quality_inspection.get_requiring_followup(db)
    return inspections


@router.get("/inspections/scheduled/{target_date}", response_model=List[QualityInspectionResponse])
def list_scheduled_inspections(
    target_date: date,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List inspections scheduled for a specific date"""
    inspections = quality_inspection.get_scheduled_for_date(db, target_date=target_date)
    return inspections


@router.get("/inspections/{inspection_id}", response_model=QualityInspectionResponse)
def get_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific inspection by ID"""
    inspection = quality_inspection.get(db, id=inspection_id)
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection not found"
        )
    return inspection


@router.post("/inspections", response_model=QualityInspectionResponse, status_code=status.HTTP_201_CREATED)
def create_inspection(
    inspection_in: QualityInspectionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Schedule a new quality inspection

    Business Logic:
    - Auto-generates inspection number
    - Sets status to SCHEDULED
    - Validates subject (courier/vehicle/delivery) exists
    - Assigns inspector if provided
    - Sets scheduled date
    """
    # TODO: Validate courier/vehicle/delivery exists
    # TODO: Validate inspector exists

    inspection = quality_inspection.create_with_number(db, obj_in=inspection_in)
    return inspection


@router.put("/inspections/{inspection_id}", response_model=QualityInspectionResponse)
def update_inspection(
    inspection_id: int,
    inspection_in: QualityInspectionUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an inspection"""
    inspection = quality_inspection.get(db, id=inspection_id)
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection not found"
        )
    inspection = quality_inspection.update(db, db_obj=inspection, obj_in=inspection_in)
    return inspection


@router.post("/inspections/{inspection_id}/complete", response_model=QualityInspectionResponse)
def complete_inspection(
    inspection_id: int,
    completion: QualityInspectionComplete,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Complete a quality inspection

    Business Logic:
    - Records overall quality score
    - Marks as passed/failed
    - Documents findings and violations
    - Provides recommendations
    - Schedules follow-up if required
    - Updates status to COMPLETED/PASSED/FAILED
    """
    inspection = quality_inspection.get(db, id=inspection_id)
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection not found"
        )

    if inspection.status not in ["scheduled", "in_progress"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only scheduled or in-progress inspections can be completed"
        )

    # Update inspection with completion data
    inspection_update = QualityInspectionUpdate(
        overall_score=completion.overall_score,
        passed=completion.passed,
        findings=completion.findings,
        violations_count=completion.violations_count,
        recommendations=completion.recommendations,
        requires_followup=completion.requires_followup,
        followup_date=completion.followup_date,
        corrective_actions=completion.corrective_actions,
        photos=completion.photos,
        attachments=completion.attachments,
        inspector_notes=completion.inspector_notes
    )
    inspection = quality_inspection.update(db, db_obj=inspection, obj_in=inspection_update)

    # Mark as completed
    inspection = quality_inspection.complete_inspection(
        db,
        inspection_id=inspection_id,
        score=float(completion.overall_score),
        passed=completion.passed
    )

    return inspection


@router.get("/report", response_model=QualityReport)
def get_quality_report(
    start_date: date = Query(None),
    end_date: date = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get quality control report

    Returns:
    - Total inspections conducted
    - Pass/fail rates
    - Average quality score
    - Critical violations
    - Pending follow-ups
    - Top violation types
    - Trend analysis
    """
    # TODO: Implement comprehensive reporting
    # For now, return placeholder
    return QualityReport(
        period=f"{start_date} to {end_date}" if start_date and end_date else "All time",
        total_inspections=0,
        passed_inspections=0,
        failed_inspections=0,
        pass_rate=0.0,
        avg_overall_score=0.0,
        critical_violations=0,
        pending_followups=0,
        top_violations=[]
    )
