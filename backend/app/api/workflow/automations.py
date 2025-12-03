from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.crud.workflow import workflow_automation
from app.schemas.workflow import (
    WorkflowAutomationCreate,
    WorkflowAutomationResponse,
    WorkflowAutomationUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[WorkflowAutomationResponse])
def list_workflow_automations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all workflow automations"""
    automations = workflow_automation.get_multi(db, skip=skip, limit=limit)
    return automations


@router.post("/", response_model=WorkflowAutomationResponse, status_code=201)
def create_workflow_automation(
    automation_in: WorkflowAutomationCreate,
    db: Session = Depends(get_db),
):
    """Create a new workflow automation"""
    automation = workflow_automation.create(db, obj_in=automation_in)
    return automation


@router.get("/{automation_id}", response_model=WorkflowAutomationResponse)
def get_workflow_automation(
    automation_id: int,
    db: Session = Depends(get_db),
):
    """Get a workflow automation by ID"""
    automation = workflow_automation.get(db, id=automation_id)
    if not automation:
        raise HTTPException(status_code=404, detail="Workflow automation not found")
    return automation


@router.put("/{automation_id}", response_model=WorkflowAutomationResponse)
def update_workflow_automation(
    automation_id: int,
    automation_in: WorkflowAutomationUpdate,
    db: Session = Depends(get_db),
):
    """Update a workflow automation"""
    automation = workflow_automation.get(db, id=automation_id)
    if not automation:
        raise HTTPException(status_code=404, detail="Workflow automation not found")

    automation = workflow_automation.update(db, db_obj=automation, obj_in=automation_in)
    return automation


@router.delete("/{automation_id}", status_code=204)
def delete_workflow_automation(
    automation_id: int,
    db: Session = Depends(get_db),
):
    """Delete a workflow automation"""
    automation = workflow_automation.get(db, id=automation_id)
    if not automation:
        raise HTTPException(status_code=404, detail="Workflow automation not found")

    workflow_automation.remove(db, id=automation_id)
    return None
