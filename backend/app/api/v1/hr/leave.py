"""Leave Management API Routes"""

import logging
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_organization, get_current_user, get_db
from app.models.tenant.organization import Organization
from app.models.user import User
from app.models.workflow.trigger import TriggerEventType
from app.schemas.hr import LeaveCreate, LeaveResponse, LeaveStatus, LeaveType, LeaveUpdate
from app.services.hr import leave_service
from app.services.workflow import event_trigger_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[LeaveResponse])
def get_leaves(
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[LeaveStatus] = None,
    leave_type: Optional[LeaveType] = None,
    courier_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Get list of leave requests with filtering

    Filters:
    - status: Filter by leave status (pending, approved, rejected, cancelled)
    - leave_type: Filter by leave type (annual, sick, emergency, unpaid)
    - courier_id: Filter by courier ID
    - start_date, end_date: Filter by date range
    """
    # If date range is provided
    if start_date and end_date:
        return leave_service.get_by_date_range(
            db,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit,
            organization_id=current_org.id,
        )

    # If status filter is provided
    if status:
        return leave_service.get_by_status(
            db, status=status, skip=skip, limit=limit, organization_id=current_org.id
        )

    # If courier_id filter is provided
    if courier_id:
        return leave_service.get_by_courier(
            db, courier_id=courier_id, skip=skip, limit=limit, organization_id=current_org.id
        )

    # Build dynamic filters
    filters = {"organization_id": current_org.id}
    if leave_type:
        filters["leave_type"] = leave_type

    return leave_service.get_multi(db, skip=skip, limit=limit, filters=filters)


@router.post("/", response_model=LeaveResponse, status_code=status.HTTP_201_CREATED)
def create_leave(
    leave_in: LeaveCreate,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_user),
):
    """Create new leave request - automatically triggers approval workflow if configured"""
    # Add organization_id to the create data
    create_data = leave_in.model_dump() if hasattr(leave_in, "model_dump") else leave_in.dict()
    create_data["organization_id"] = current_org.id

    # Create the leave request
    leave = leave_service.create(db, obj_in=create_data)

    # Trigger workflow for leave approval
    try:
        workflow_instance = event_trigger_service.trigger_workflow_for_entity(
            db,
            entity_type="leave",
            entity_id=leave.id,
            event_type=TriggerEventType.RECORD_CREATED,
            entity_data={
                "courier_id": leave.courier_id,
                "leave_type": leave.leave_type.value if leave.leave_type else None,
                "start_date": str(leave.start_date) if leave.start_date else None,
                "end_date": str(leave.end_date) if leave.end_date else None,
                "reason": leave.reason,
                "status": leave.status.value if leave.status else "pending",
                "organization_id": current_org.id,
            },
            initiated_by=current_user.id,
        )
        if workflow_instance:
            logger.info(f"Workflow {workflow_instance.id} triggered for leave {leave.id}")
    except Exception as e:
        # Log but don't fail the leave creation
        logger.warning(f"Failed to trigger workflow for leave {leave.id}: {e}")

    return leave


@router.get("/{leave_id}", response_model=LeaveResponse)
def get_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_user),
):
    """Get leave request by ID"""
    leave = leave_service.get(db, id=leave_id)
    if not leave or leave.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Leave request not found")
    return leave


@router.put("/{leave_id}", response_model=LeaveResponse)
def update_leave(
    leave_id: int,
    leave_in: LeaveUpdate,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_user),
):
    """Update leave request"""
    leave = leave_service.get(db, id=leave_id)
    if not leave or leave.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Leave request not found")

    return leave_service.update(db, db_obj=leave, obj_in=leave_in)


@router.delete("/{leave_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_user),
):
    """Delete leave request"""
    leave = leave_service.get(db, id=leave_id)
    if not leave or leave.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Leave request not found")

    leave_service.delete(db, id=leave_id)
    return None


@router.get("/courier/{courier_id}", response_model=List[LeaveResponse])
def get_courier_leaves(
    courier_id: int,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    """Get all leave requests for a specific courier"""
    return leave_service.get_by_courier(
        db, courier_id=courier_id, skip=skip, limit=limit, organization_id=current_org.id
    )


@router.post("/{leave_id}/approve", response_model=LeaveResponse)
def approve_leave(
    leave_id: int,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_user),
):
    """Approve a leave request"""
    # Verify leave belongs to organization before approving
    existing_leave = leave_service.get(db, id=leave_id)
    if not existing_leave or existing_leave.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Leave request not found")

    leave = leave_service.approve_leave(
        db, leave_id=leave_id, approved_by=current_user.id, notes=notes
    )
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")

    return leave


@router.post("/{leave_id}/reject", response_model=LeaveResponse)
def reject_leave(
    leave_id: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_user),
):
    """Reject a leave request"""
    # Verify leave belongs to organization before rejecting
    existing_leave = leave_service.get(db, id=leave_id)
    if not existing_leave or existing_leave.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Leave request not found")

    leave = leave_service.reject_leave(
        db, leave_id=leave_id, approved_by=current_user.id, reason=reason
    )
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")

    return leave


@router.get("/statistics", response_model=dict)
def get_leave_statistics(
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_user),
):
    """
    Get leave statistics

    Returns:
    - total: Total number of leave requests
    - pending: Number of pending requests
    - approved: Number of approved requests
    - rejected: Number of rejected requests
    """
    return leave_service.get_statistics(db, organization_id=current_org.id)
