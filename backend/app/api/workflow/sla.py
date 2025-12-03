from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.crud.workflow import workflow_sla, workflow_sla_instance
from app.schemas.workflow import (
    WorkflowSLACreate,
    WorkflowSLAUpdate,
    WorkflowSLAResponse,
    WorkflowSLAInstanceResponse,
)

router = APIRouter()


# SLA Definitions
@router.get("/", response_model=List[WorkflowSLAResponse])
def list_workflow_slas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all workflow SLA definitions"""
    slas = workflow_sla.get_multi(db, skip=skip, limit=limit)
    return slas


@router.post("/", response_model=WorkflowSLAResponse, status_code=201)
def create_workflow_sla(
    sla_in: WorkflowSLACreate,
    db: Session = Depends(get_db),
):
    """Create a new workflow SLA definition"""
    sla = workflow_sla.create(db, obj_in=sla_in)
    return sla


@router.get("/{sla_id}", response_model=WorkflowSLAResponse)
def get_workflow_sla(
    sla_id: int,
    db: Session = Depends(get_db),
):
    """Get a workflow SLA by ID"""
    sla = workflow_sla.get(db, id=sla_id)
    if not sla:
        raise HTTPException(status_code=404, detail="Workflow SLA not found")
    return sla


@router.put("/{sla_id}", response_model=WorkflowSLAResponse)
def update_workflow_sla(
    sla_id: int,
    sla_in: WorkflowSLAUpdate,
    db: Session = Depends(get_db),
):
    """Update a workflow SLA"""
    sla = workflow_sla.get(db, id=sla_id)
    if not sla:
        raise HTTPException(status_code=404, detail="Workflow SLA not found")

    sla = workflow_sla.update(db, db_obj=sla, obj_in=sla_in)
    return sla


@router.delete("/{sla_id}", status_code=204)
def delete_workflow_sla(
    sla_id: int,
    db: Session = Depends(get_db),
):
    """Delete a workflow SLA"""
    sla = workflow_sla.get(db, id=sla_id)
    if not sla:
        raise HTTPException(status_code=404, detail="Workflow SLA not found")

    workflow_sla.remove(db, id=sla_id)
    return None


# SLA Instances
@router.get("/instances", response_model=List[WorkflowSLAInstanceResponse])
def list_sla_instances(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all SLA instances"""
    instances = workflow_sla_instance.get_multi(db, skip=skip, limit=limit)
    return instances


@router.get("/instances/{instance_id}", response_model=WorkflowSLAInstanceResponse)
def get_sla_instance(
    instance_id: int,
    db: Session = Depends(get_db),
):
    """Get an SLA instance by ID"""
    instance = workflow_sla_instance.get(db, id=instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="SLA instance not found")
    return instance
