"""Workflow Template API Routes"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.workflow import (
    WorkflowTemplateCreate, WorkflowTemplateUpdate, WorkflowTemplateResponse
)
from app.services.workflow import template_service


router = APIRouter()


@router.get("/", response_model=List[WorkflowTemplateResponse])
def get_templates(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Get list of workflow templates with filtering

    Filters:
    - is_active: Filter by active status
    - category: Filter by category
    """
    # If active filter is provided
    if is_active is True:
        return template_service.get_active(db, skip=skip, limit=limit)

    # If category filter is provided
    if category:
        return template_service.get_by_category(db, category=category, skip=skip, limit=limit)

    # Build dynamic filters
    filters = {}
    if is_active is not None:
        filters["is_active"] = is_active

    return template_service.get_multi(db, skip=skip, limit=limit, filters=filters)


@router.post("/", response_model=WorkflowTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template(
    template_in: WorkflowTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new workflow template"""
    return template_service.create(db, obj_in=template_in)


@router.get("/{template_id}", response_model=WorkflowTemplateResponse)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get workflow template by ID"""
    template = template_service.get(db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Workflow template not found")
    return template


@router.put("/{template_id}", response_model=WorkflowTemplateResponse)
def update_template(
    template_id: int,
    template_in: WorkflowTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update workflow template"""
    template = template_service.get(db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Workflow template not found")

    return template_service.update(db, db_obj=template, obj_in=template_in)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete workflow template"""
    template = template_service.get(db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Workflow template not found")

    template_service.delete(db, id=template_id)
    return None


@router.post("/{template_id}/activate", response_model=WorkflowTemplateResponse)
def activate_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Activate a workflow template"""
    template = template_service.activate_template(db, template_id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Workflow template not found")

    return template


@router.post("/{template_id}/deactivate", response_model=WorkflowTemplateResponse)
def deactivate_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deactivate a workflow template"""
    template = template_service.deactivate_template(db, template_id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Workflow template not found")

    return template


@router.get("/categories/list", response_model=List[str])
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all unique template categories"""
    return template_service.get_categories(db)


@router.get("/statistics/summary", response_model=dict)
def get_template_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get workflow template statistics

    Returns:
    - total: Total number of templates
    - active: Number of active templates
    - inactive: Number of inactive templates
    - categories: Number of unique categories
    """
    return template_service.get_statistics(db)
