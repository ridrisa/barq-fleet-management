from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.workflow import workflow_template
from app.schemas.workflow import (
    WorkflowTemplateCreate,
    WorkflowTemplateUpdate,
    WorkflowTemplateResponse,
)

router = APIRouter()


@router.get("/", response_model=List[WorkflowTemplateResponse])
def list_workflow_templates(
    skip: int = 0,
    limit: int = 100,
    category: str = Query(None),
    is_active: bool = Query(None),
    db: Session = Depends(get_db),
):
    """List all workflow templates with optional filtering"""
    # For now, using basic CRUD get_multi
    # TODO: Add filtering by category and is_active
    templates = workflow_template.get_multi(db, skip=skip, limit=limit)
    return templates


@router.post("/", response_model=WorkflowTemplateResponse, status_code=201)
def create_workflow_template(
    template_in: WorkflowTemplateCreate,
    db: Session = Depends(get_db),
):
    """Create a new workflow template"""
    template = workflow_template.create(db, obj_in=template_in)
    return template


@router.get("/{template_id}", response_model=WorkflowTemplateResponse)
def get_workflow_template(
    template_id: int,
    db: Session = Depends(get_db),
):
    """Get a workflow template by ID"""
    template = workflow_template.get(db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Workflow template not found")
    return template


@router.put("/{template_id}", response_model=WorkflowTemplateResponse)
def update_workflow_template(
    template_id: int,
    template_in: WorkflowTemplateUpdate,
    db: Session = Depends(get_db),
):
    """Update a workflow template"""
    template = workflow_template.get(db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Workflow template not found")

    template = workflow_template.update(db, db_obj=template, obj_in=template_in)
    return template


@router.delete("/{template_id}", status_code=204)
def delete_workflow_template(
    template_id: int,
    db: Session = Depends(get_db),
):
    """Delete a workflow template"""
    template = workflow_template.get(db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Workflow template not found")

    workflow_template.remove(db, id=template_id)
    return None


@router.post("/{template_id}/clone", response_model=WorkflowTemplateResponse)
def clone_workflow_template(
    template_id: int,
    name: str = Query(..., description="Name for the cloned template"),
    db: Session = Depends(get_db),
):
    """Clone an existing workflow template"""
    template = workflow_template.get(db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Workflow template not found")

    # Create clone
    cloned_template = workflow_template.create(
        db,
        obj_in=WorkflowTemplateCreate(
            name=name,
            description=f"Cloned from: {template.name}",
            steps=template.steps,
            category=template.category,
            estimated_duration=template.estimated_duration,
            is_active=False,  # Start as inactive
        ),
    )

    return cloned_template


@router.patch("/{template_id}/activate", response_model=WorkflowTemplateResponse)
def activate_workflow_template(
    template_id: int,
    db: Session = Depends(get_db),
):
    """Activate a workflow template"""
    template = workflow_template.get(db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Workflow template not found")

    template = workflow_template.update(
        db, db_obj=template, obj_in={"is_active": True}
    )
    return template


@router.patch("/{template_id}/deactivate", response_model=WorkflowTemplateResponse)
def deactivate_workflow_template(
    template_id: int,
    db: Session = Depends(get_db),
):
    """Deactivate a workflow template"""
    template = workflow_template.get(db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Workflow template not found")

    template = workflow_template.update(
        db, db_obj=template, obj_in={"is_active": False}
    )
    return template
