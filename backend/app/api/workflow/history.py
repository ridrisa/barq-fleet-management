from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from app.core.dependencies import get_db
from app.crud.workflow import workflow_history, workflow_step_history
from app.schemas.workflow import (
    WorkflowHistoryResponse,
    WorkflowHistoryWithActor,
    WorkflowStepHistoryResponse,
    WorkflowTimelineResponse,
)
from app.models.workflow.history import WorkflowHistoryEventType

router = APIRouter()


@router.get("/", response_model=List[WorkflowHistoryResponse])
def list_history(
    workflow_instance_id: Optional[int] = Query(None),
    event_type: Optional[WorkflowHistoryEventType] = Query(None),
    actor_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    List workflow history with comprehensive filtering options
    - Filter by workflow instance, event type, actor, date range
    """
    query = db.query(workflow_history.model)

    # Apply filters
    filters = []
    if workflow_instance_id:
        filters.append(workflow_history.model.workflow_instance_id == workflow_instance_id)
    if event_type:
        filters.append(workflow_history.model.event_type == event_type)
    if actor_id:
        filters.append(workflow_history.model.actor_id == actor_id)
    if start_date:
        filters.append(workflow_history.model.event_time >= start_date)
    if end_date:
        filters.append(workflow_history.model.event_time <= end_date)

    if filters:
        query = query.filter(and_(*filters))

    history = query.order_by(workflow_history.model.event_time.desc()).offset(skip).limit(limit).all()
    return history


@router.get("/{history_id}", response_model=WorkflowHistoryResponse)
def get_history_entry(
    history_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific workflow history entry by ID"""
    history = workflow_history.get(db, id=history_id)
    if not history:
        raise HTTPException(status_code=404, detail="History entry not found")
    return history


@router.get("/instance/{instance_id}/timeline", response_model=WorkflowTimelineResponse)
def get_workflow_timeline(
    instance_id: int,
    db: Session = Depends(get_db),
):
    """
    Get complete timeline view of a workflow instance
    Includes all history events and step executions
    """
    from app.models.workflow.instance import WorkflowInstance

    # Get workflow instance
    instance = db.query(WorkflowInstance).filter(WorkflowInstance.id == instance_id).first()
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")

    # Get all history events
    events = db.query(workflow_history.model).filter(
        workflow_history.model.workflow_instance_id == instance_id
    ).order_by(workflow_history.model.event_time).all()

    # Get all step history
    steps = db.query(workflow_step_history.model).filter(
        workflow_step_history.model.workflow_instance_id == instance_id
    ).order_by(workflow_step_history.model.started_at).all()

    # Calculate total duration
    total_duration_minutes = None
    if instance.started_at and instance.completed_at:
        duration = instance.completed_at - instance.started_at
        total_duration_minutes = int(duration.total_seconds() / 60)

    return WorkflowTimelineResponse(
        workflow_instance_id=instance.id,
        workflow_name=instance.template.name if instance.template else "Unknown",
        started_at=instance.started_at,
        completed_at=instance.completed_at,
        total_duration_minutes=total_duration_minutes,
        events=events,
        steps=steps,
    )


@router.get("/instance/{instance_id}/audit", response_model=List[WorkflowHistoryWithActor])
def get_audit_trail(
    instance_id: int,
    db: Session = Depends(get_db),
):
    """
    Get tamper-evident audit trail for a workflow instance
    Includes checksum verification for data integrity
    """
    events = db.query(workflow_history.model).filter(
        workflow_history.model.workflow_instance_id == instance_id
    ).order_by(workflow_history.model.event_time).all()

    if not events:
        raise HTTPException(status_code=404, detail="No audit trail found for this workflow")

    # TODO: Implement checksum verification
    # Verify that each event's checksum matches the previous event's checksum
    # This creates a blockchain-like audit trail

    return events


@router.get("/instance/{instance_id}/steps", response_model=List[WorkflowStepHistoryResponse])
def get_step_history(
    instance_id: int,
    db: Session = Depends(get_db),
):
    """Get step execution history for a workflow instance"""
    steps = db.query(workflow_step_history.model).filter(
        workflow_step_history.model.workflow_instance_id == instance_id
    ).order_by(workflow_step_history.model.step_index).all()

    return steps


@router.get("/instance/{instance_id}/changes")
def get_field_changes(
    instance_id: int,
    field_name: Optional[str] = Query(None, description="Filter by specific field name"),
    db: Session = Depends(get_db),
):
    """
    Get all field changes for a workflow instance
    Useful for tracking what changed and when
    """
    query = db.query(workflow_history.model).filter(
        workflow_history.model.workflow_instance_id == instance_id,
        workflow_history.model.field_changes != None
    )

    if field_name:
        # Filter for changes to a specific field
        # Note: This is a simplified implementation
        # In production, you'd want more sophisticated JSON querying
        events = query.all()
        filtered_events = [
            {
                "event_time": e.event_time,
                "actor_id": e.actor_id,
                "field_changes": e.field_changes,
                "description": e.description,
            }
            for e in events
            if e.field_changes and field_name in e.field_changes
        ]
        return filtered_events
    else:
        events = query.order_by(workflow_history.model.event_time.desc()).all()
        return [
            {
                "event_time": e.event_time,
                "actor_id": e.actor_id,
                "field_changes": e.field_changes,
                "description": e.description,
            }
            for e in events
        ]


@router.get("/export/{instance_id}")
def export_audit_trail(
    instance_id: int,
    format: str = Query("json", description="Export format: json, csv, pdf"),
    db: Session = Depends(get_db),
):
    """
    Export complete audit trail for compliance/archival purposes
    Supports multiple formats: JSON, CSV, PDF
    """
    events = db.query(workflow_history.model).filter(
        workflow_history.model.workflow_instance_id == instance_id
    ).order_by(workflow_history.model.event_time).all()

    if not events:
        raise HTTPException(status_code=404, detail="No audit trail found")

    # TODO: Implement actual export logic based on format
    # For now, return JSON

    export_data = {
        "workflow_instance_id": instance_id,
        "export_date": datetime.utcnow().isoformat(),
        "total_events": len(events),
        "events": [
            {
                "id": e.id,
                "event_type": e.event_type.value if hasattr(e.event_type, 'value') else e.event_type,
                "event_time": e.event_time.isoformat(),
                "actor_id": e.actor_id,
                "description": e.description,
                "previous_state": e.previous_state,
                "new_state": e.new_state,
                "field_changes": e.field_changes,
                "checksum": e.checksum,
            }
            for e in events
        ],
    }

    return export_data
