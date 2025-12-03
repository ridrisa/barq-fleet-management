from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.crud.workflow import workflow_instance
from app.schemas.workflow import (
    WorkflowInstanceCreate,
    WorkflowInstanceResponse,
    WorkflowInstanceUpdate,
    WorkflowStatus,
)
from app.services.workflow.execution_service import WorkflowExecutionService

router = APIRouter()


@router.get("/", response_model=List[WorkflowInstanceResponse])
def list_workflow_instances(
    skip: int = 0,
    limit: int = 100,
    status: Optional[WorkflowStatus] = Query(None),
    template_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """List all workflow instances with optional filtering"""
    # For now, using basic CRUD get_multi
    # TODO: Add filtering by status and template_id
    instances = workflow_instance.get_multi(db, skip=skip, limit=limit)
    return instances


@router.post("/", response_model=WorkflowInstanceResponse, status_code=201)
def create_workflow_instance(
    instance_in: WorkflowInstanceCreate,
    db: Session = Depends(get_db),
):
    """Create a new workflow instance"""
    instance = workflow_instance.create(db, obj_in=instance_in)
    return instance


@router.post("/start", response_model=WorkflowInstanceResponse, status_code=201)
def start_workflow(
    template_id: int = Body(...),
    initiated_by: int = Body(...),
    initial_data: Optional[Dict[str, Any]] = Body(None),
    db: Session = Depends(get_db),
):
    """Create and start a new workflow instance from a template"""
    execution_service = WorkflowExecutionService(db)
    instance = execution_service.create_and_start_workflow(
        template_id=template_id,
        initiated_by=initiated_by,
        initial_data=initial_data,
    )
    return instance


@router.get("/{instance_id}", response_model=WorkflowInstanceResponse)
def get_workflow_instance(
    instance_id: int,
    db: Session = Depends(get_db),
):
    """Get a workflow instance by ID"""
    instance = workflow_instance.get(db, id=instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")
    return instance


@router.get("/{instance_id}/status")
def get_workflow_status(
    instance_id: int,
    db: Session = Depends(get_db),
):
    """Get detailed workflow status including progress"""
    execution_service = WorkflowExecutionService(db)
    status = execution_service.get_workflow_status(instance_id)
    return status


@router.put("/{instance_id}", response_model=WorkflowInstanceResponse)
def update_workflow_instance(
    instance_id: int,
    instance_in: WorkflowInstanceUpdate,
    db: Session = Depends(get_db),
):
    """Update a workflow instance"""
    instance = workflow_instance.get(db, id=instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")

    instance = workflow_instance.update(db, db_obj=instance, obj_in=instance_in)
    return instance


@router.post("/{instance_id}/advance", response_model=WorkflowInstanceResponse)
def advance_workflow_step(
    instance_id: int,
    step_data: Optional[Dict[str, Any]] = Body(None),
    db: Session = Depends(get_db),
):
    """Advance workflow to the next step"""
    execution_service = WorkflowExecutionService(db)
    instance = execution_service.advance_workflow(
        instance_id=instance_id,
        step_data=step_data,
    )
    return instance


@router.post("/{instance_id}/transition", response_model=WorkflowInstanceResponse)
def transition_workflow_status(
    instance_id: int,
    new_status: WorkflowStatus = Body(...),
    notes: Optional[str] = Body(None),
    db: Session = Depends(get_db),
):
    """Transition workflow to a new status"""
    execution_service = WorkflowExecutionService(db)
    instance = execution_service.transition_status(
        instance_id=instance_id,
        new_status=new_status,
        notes=notes,
    )
    return instance


@router.post("/{instance_id}/cancel", response_model=WorkflowInstanceResponse)
def cancel_workflow(
    instance_id: int,
    reason: Optional[str] = Body(None),
    db: Session = Depends(get_db),
):
    """Cancel a workflow instance"""
    execution_service = WorkflowExecutionService(db)
    instance = execution_service.cancel_workflow(
        instance_id=instance_id,
        reason=reason,
    )
    return instance


@router.delete("/{instance_id}", status_code=204)
def delete_workflow_instance(
    instance_id: int,
    db: Session = Depends(get_db),
):
    """Delete a workflow instance"""
    instance = workflow_instance.get(db, id=instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")

    workflow_instance.remove(db, id=instance_id)
    return None
