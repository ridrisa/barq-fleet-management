from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.crud.workflow import workflow_trigger
from app.schemas.workflow import (
    WorkflowTriggerCreate,
    WorkflowTriggerResponse,
    WorkflowTriggerUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[WorkflowTriggerResponse])
def list_workflow_triggers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all workflow triggers"""
    triggers = workflow_trigger.get_multi(db, skip=skip, limit=limit)
    return triggers


@router.post("/", response_model=WorkflowTriggerResponse, status_code=201)
def create_workflow_trigger(
    trigger_in: WorkflowTriggerCreate,
    db: Session = Depends(get_db),
):
    """Create a new workflow trigger"""
    trigger = workflow_trigger.create(db, obj_in=trigger_in)
    return trigger


@router.get("/{trigger_id}", response_model=WorkflowTriggerResponse)
def get_workflow_trigger(
    trigger_id: int,
    db: Session = Depends(get_db),
):
    """Get a workflow trigger by ID"""
    trigger = workflow_trigger.get(db, id=trigger_id)
    if not trigger:
        raise HTTPException(status_code=404, detail="Workflow trigger not found")
    return trigger


@router.put("/{trigger_id}", response_model=WorkflowTriggerResponse)
def update_workflow_trigger(
    trigger_id: int,
    trigger_in: WorkflowTriggerUpdate,
    db: Session = Depends(get_db),
):
    """Update a workflow trigger"""
    trigger = workflow_trigger.get(db, id=trigger_id)
    if not trigger:
        raise HTTPException(status_code=404, detail="Workflow trigger not found")

    trigger = workflow_trigger.update(db, db_obj=trigger, obj_in=trigger_in)
    return trigger


@router.delete("/{trigger_id}", status_code=204)
def delete_workflow_trigger(
    trigger_id: int,
    db: Session = Depends(get_db),
):
    """Delete a workflow trigger"""
    trigger = workflow_trigger.get(db, id=trigger_id)
    if not trigger:
        raise HTTPException(status_code=404, detail="Workflow trigger not found")

    workflow_trigger.remove(db, id=trigger_id)
    return None
