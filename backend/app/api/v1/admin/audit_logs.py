"""Admin Audit Logs API"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.core.dependencies import get_db, get_current_superuser
from app.models.user import User
from app.models.audit_log import AuditLog, AuditAction
from app.schemas.audit_log import AuditLogResponse, AuditLogSummary

router = APIRouter()


@router.get("/", response_model=List[AuditLogResponse])
def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    action: Optional[AuditAction] = Query(None),
    user_id: Optional[int] = Query(None),
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    ip_address: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    List audit logs with comprehensive filtering options.

    Requires superuser permission.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **action**: Filter by action type (create, update, delete, etc.)
    - **user_id**: Filter by user who performed the action
    - **resource_type**: Filter by resource type (e.g., "courier", "vehicle")
    - **resource_id**: Filter by specific resource ID
    - **start_date**: Filter logs created after this date
    - **end_date**: Filter logs created before this date
    - **ip_address**: Filter by IP address
    - **search**: Search in description and username
    """
    query = db.query(AuditLog)

    # Apply filters
    if action:
        query = query.filter(AuditLog.action == action)

    if user_id:
        query = query.filter(AuditLog.user_id == user_id)

    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)

    if resource_id:
        query = query.filter(AuditLog.resource_id == resource_id)

    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)

    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)

    if ip_address:
        query = query.filter(AuditLog.ip_address == ip_address)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (AuditLog.description.ilike(search_pattern)) |
            (AuditLog.username.ilike(search_pattern))
        )

    # Order by most recent first and apply pagination
    logs = query.order_by(desc(AuditLog.created_at)).offset(skip).limit(limit).all()

    return logs


@router.get("/summary", response_model=AuditLogSummary)
def get_audit_logs_summary(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get summary statistics for audit logs.

    Requires superuser permission.

    Returns:
    - Total number of logs
    - Breakdown by action type
    - Breakdown by resource type
    - Top 10 most active users
    - 10 most recent activities
    """
    query = db.query(AuditLog)

    # Apply date filters
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)

    # Total logs
    total_logs = query.count()

    # Actions breakdown
    actions_breakdown = {}
    action_counts = (
        query.with_entities(AuditLog.action, func.count(AuditLog.id))
        .group_by(AuditLog.action)
        .all()
    )
    for action, count in action_counts:
        actions_breakdown[action.value] = count

    # Resources breakdown
    resources_breakdown = {}
    resource_counts = (
        query.with_entities(AuditLog.resource_type, func.count(AuditLog.id))
        .group_by(AuditLog.resource_type)
        .order_by(desc(func.count(AuditLog.id)))
        .limit(10)
        .all()
    )
    for resource, count in resource_counts:
        resources_breakdown[resource] = count

    # Top users
    top_users = []
    user_counts = (
        query.filter(AuditLog.user_id.isnot(None))
        .with_entities(
            AuditLog.user_id,
            AuditLog.username,
            func.count(AuditLog.id).label('activity_count')
        )
        .group_by(AuditLog.user_id, AuditLog.username)
        .order_by(desc('activity_count'))
        .limit(10)
        .all()
    )
    for user_id, username, count in user_counts:
        top_users.append({
            "user_id": user_id,
            "username": username or "Unknown",
            "activity_count": count
        })

    # Recent activities
    recent_activities = (
        query.order_by(desc(AuditLog.created_at))
        .limit(10)
        .all()
    )

    return AuditLogSummary(
        total_logs=total_logs,
        actions_breakdown=actions_breakdown,
        resources_breakdown=resources_breakdown,
        top_users=top_users,
        recent_activities=recent_activities,
    )


@router.get("/{audit_log_id}", response_model=AuditLogResponse)
def get_audit_log(
    audit_log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get a specific audit log by ID.

    Requires superuser permission.

    Returns detailed information about a single audit log entry including
    old and new values for changes.
    """
    audit_log = db.query(AuditLog).filter(AuditLog.id == audit_log_id).first()
    if not audit_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit log with id {audit_log_id} not found"
        )
    return audit_log


@router.get("/resource/{resource_type}/{resource_id}", response_model=List[AuditLogResponse])
def get_resource_audit_trail(
    resource_type: str,
    resource_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get complete audit trail for a specific resource.

    Requires superuser permission.

    Returns all audit logs related to a specific resource, ordered by most recent first.
    Useful for tracking the complete history of changes to an entity.

    - **resource_type**: Type of resource (e.g., "courier", "vehicle")
    - **resource_id**: ID of the resource
    """
    logs = (
        db.query(AuditLog)
        .filter(
            AuditLog.resource_type == resource_type,
            AuditLog.resource_id == resource_id
        )
        .order_by(desc(AuditLog.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    return logs


@router.get("/actions/types", response_model=List[str])
def list_action_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get list of all available action types.

    Requires superuser permission.

    Useful for UI dropdowns and filtering options.
    """
    return [action.value for action in AuditAction]


@router.get("/resources/types", response_model=List[str])
def list_resource_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get list of all resource types that have audit logs.

    Requires superuser permission.

    Useful for UI dropdowns and filtering options.
    """
    resource_types = (
        db.query(AuditLog.resource_type)
        .distinct()
        .order_by(AuditLog.resource_type)
        .all()
    )
    return [rt[0] for rt in resource_types]
