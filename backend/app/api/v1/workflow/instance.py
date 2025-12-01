"""Workflow Instance API Routes"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.workflow import (
    WorkflowInstanceCreate, WorkflowInstanceUpdate, WorkflowInstanceResponse,
    WorkflowStatus
)
from app.services.workflow import instance_service


router = APIRouter()


@router.get("/", response_model=List[WorkflowInstanceResponse])
def get_instances(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[WorkflowStatus] = None,
    template_id: Optional[int] = None,
    initiated_by: Optional[int] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Get list of workflow instances with filtering

    Filters:
    - status: Filter by workflow status
    - template_id: Filter by template ID
    - initiated_by: Filter by initiator user ID
    """
    # If status filter is provided
    if status:
        return instance_service.get_by_status(db, status=status, skip=skip, limit=limit)

    # If template_id filter is provided
    if template_id:
        return instance_service.get_by_template(db, template_id=template_id, skip=skip, limit=limit)

    # If initiated_by filter is provided
    if initiated_by:
        return instance_service.get_by_initiator(db, user_id=initiated_by, skip=skip, limit=limit)

    return instance_service.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=WorkflowInstanceResponse, status_code=status.HTTP_201_CREATED)
def create_instance(
    instance_in: WorkflowInstanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new workflow instance"""
    return instance_service.create(db, obj_in=instance_in)


@router.get("/{instance_id}", response_model=WorkflowInstanceResponse)
def get_instance(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get workflow instance by ID"""
    instance = instance_service.get(db, id=instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")
    return instance


@router.put("/{instance_id}", response_model=WorkflowInstanceResponse)
def update_instance(
    instance_id: int,
    instance_in: WorkflowInstanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update workflow instance"""
    instance = instance_service.get(db, id=instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")

    return instance_service.update(db, db_obj=instance, obj_in=instance_in)


@router.delete("/{instance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_instance(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete workflow instance"""
    instance = instance_service.get(db, id=instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")

    instance_service.delete(db, id=instance_id)
    return None


@router.post("/{instance_id}/start", response_model=WorkflowInstanceResponse)
def start_workflow(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start a workflow instance"""
    instance = instance_service.start_workflow(db, instance_id=instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")

    return instance


@router.post("/{instance_id}/complete-step", response_model=WorkflowInstanceResponse)
def complete_step(
    instance_id: int,
    step_data: Optional[Dict[str, Any]] = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Complete current step and move to next"""
    instance = instance_service.complete_step(
        db, instance_id=instance_id, step_data=step_data
    )
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")

    return instance


@router.post("/{instance_id}/complete", response_model=WorkflowInstanceResponse)
def complete_workflow(
    instance_id: int,
    notes: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Complete a workflow instance"""
    instance = instance_service.complete_workflow(
        db, instance_id=instance_id, notes=notes
    )
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")

    return instance


@router.post("/{instance_id}/cancel", response_model=WorkflowInstanceResponse)
def cancel_workflow(
    instance_id: int,
    reason: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel a workflow instance"""
    instance = instance_service.cancel_workflow(
        db, instance_id=instance_id, reason=reason
    )
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")

    return instance


@router.post("/{instance_id}/submit-approval", response_model=WorkflowInstanceResponse)
def submit_for_approval(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit workflow instance for approval"""
    instance = instance_service.submit_for_approval(db, instance_id=instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")

    return instance


@router.post("/{instance_id}/approve", response_model=WorkflowInstanceResponse)
def approve_workflow(
    instance_id: int,
    notes: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve a workflow instance"""
    instance = instance_service.approve_workflow(
        db, instance_id=instance_id, notes=notes
    )
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")

    return instance


@router.post("/{instance_id}/reject", response_model=WorkflowInstanceResponse)
def reject_workflow(
    instance_id: int,
    reason: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reject a workflow instance"""
    instance = instance_service.reject_workflow(
        db, instance_id=instance_id, reason=reason
    )
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")

    return instance


@router.get("/user/{user_id}", response_model=List[WorkflowInstanceResponse])
def get_user_workflows(
    user_id: int,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get all workflow instances initiated by a specific user"""
    return instance_service.get_by_initiator(
        db, user_id=user_id, skip=skip, limit=limit
    )


@router.get("/statistics/summary", response_model=dict)
def get_instance_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get workflow instance statistics

    Returns:
    - total: Total number of instances
    - draft: Number of draft instances
    - in_progress: Number of in-progress instances
    - pending_approval: Number of pending approval instances
    - approved: Number of approved instances
    - completed: Number of completed instances
    - rejected: Number of rejected instances
    - cancelled: Number of cancelled instances
    """
    return instance_service.get_statistics(db)
