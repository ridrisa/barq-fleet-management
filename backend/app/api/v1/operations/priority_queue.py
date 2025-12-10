from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_organization, get_current_user
from app.services.operations import priority_queue_service
from app.models.tenant.organization import Organization
from app.schemas.operations.priority_queue import (
    PriorityQueueEntryCreate,
    PriorityQueueEntryEscalate,
    PriorityQueueEntryResponse,
    PriorityQueueEntryUpdate,
    QueueMetrics,
    QueuePosition,
    QueuePriority,
)

router = APIRouter()


@router.get("/", response_model=List[PriorityQueueEntryResponse])
def list_queue_entries(
    skip: int = 0,
    limit: int = 100,
    priority: QueuePriority = Query(None, description="Filter by priority"),
    zone_id: int = Query(None, description="Filter by zone"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List all queue entries ordered by priority

    Returns entries sorted by:
    1. Total priority score (descending)
    2. Queue time (ascending - older first)
    """
    if priority:
        entries = priority_queue_service.get_by_priority(
            db, priority=priority, skip=skip, limit=limit, organization_id=current_org.id
        )
    elif zone_id:
        entries = priority_queue_service.get_by_zone(
            db, zone_id=zone_id, skip=skip, limit=limit, organization_id=current_org.id
        )
    else:
        entries = priority_queue_service.get_queued(db, skip=skip, limit=limit, organization_id=current_org.id)
    return entries


@router.get("/urgent", response_model=List[PriorityQueueEntryResponse])
def list_urgent_entries(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List urgent and critical queue entries

    Business Logic:
    - Returns CRITICAL and URGENT priority entries
    - Used for immediate attention dashboard
    - Sorted by SLA deadline (closest first)
    """
    entries = priority_queue_service.get_urgent(db, organization_id=current_org.id)
    return entries


@router.get("/at-risk", response_model=List[PriorityQueueEntryResponse])
def list_at_risk_entries(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List entries at risk of SLA breach

    Business Logic:
    - Returns entries past warning threshold
    - Warning threshold = SLA deadline - buffer time
    - Requires immediate action
    - Triggers escalation if not assigned soon
    """
    entries = priority_queue_service.get_at_risk(db, organization_id=current_org.id)
    return entries


@router.get("/escalated", response_model=List[PriorityQueueEntryResponse])
def list_escalated_entries(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List escalated queue entries

    Business Logic:
    - Returns entries that have been escalated
    - Requires supervisor/manager attention
    - May have exceeded normal assignment attempts
    """
    entries = priority_queue_service.get_escalated(db, organization_id=current_org.id)
    return entries


@router.get("/{entry_id}", response_model=PriorityQueueEntryResponse)
def get_queue_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get a specific queue entry by ID"""
    entry = priority_queue_service.get(db, id=entry_id)
    if not entry or entry.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Queue entry not found")
    return entry


@router.get("/delivery/{delivery_id}", response_model=PriorityQueueEntryResponse)
def get_entry_by_delivery(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get queue entry for a specific delivery"""
    entry = priority_queue_service.get_by_delivery(db, delivery_id=delivery_id, organization_id=current_org.id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Queue entry not found for this delivery"
        )
    return entry


@router.post("/", response_model=PriorityQueueEntryResponse, status_code=status.HTTP_201_CREATED)
def create_queue_entry(
    entry_in: PriorityQueueEntryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Add delivery to priority queue

    Business Logic:
    - Auto-generates queue number
    - Calculates total priority score from:
      - Base priority score
      - Time factor (urgency)
      - Customer tier score
      - SLA factor score
    - Calculates warning threshold
    - Sets initial queue position
    - Updates all queue positions
    """
    # Check if delivery already in queue within organization
    existing = priority_queue_service.get_by_delivery(
        db, delivery_id=entry_in.delivery_id, organization_id=current_org.id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Delivery already in queue"
        )

    # TODO: Validate delivery exists
    # TODO: Validate zone exists if provided

    entry = priority_queue_service.create_with_number(db, obj_in=entry_in, organization_id=current_org.id)
    return entry


@router.put("/{entry_id}", response_model=PriorityQueueEntryResponse)
def update_queue_entry(
    entry_id: int,
    entry_in: PriorityQueueEntryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update a queue entry

    Business Logic:
    - Can update priority, preferences, constraints
    - Recalculates queue position if priority changed
    - Cannot update if already assigned
    """
    entry = priority_queue_service.get(db, id=entry_id)
    if not entry or entry.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Queue entry not found")

    if entry.status not in ["queued", "processing"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update entry that is already assigned or completed",
        )

    entry = priority_queue_service.update(db, db_obj=entry, obj_in=entry_in)
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_queue_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Delete a queue entry"""
    entry = priority_queue_service.get(db, id=entry_id)
    if not entry or entry.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Queue entry not found")
    priority_queue_service.delete(db, id=entry_id)
    return None


@router.post("/{entry_id}/process", response_model=PriorityQueueEntryResponse)
def mark_as_processing(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Mark entry as being processed for assignment

    Business Logic:
    - Updates status to PROCESSING
    - Records processing start time
    - Prevents multiple processors from picking same entry
    - Updates queue positions
    """
    entry = priority_queue_service.get(db, id=entry_id)
    if not entry or entry.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Queue entry not found")

    if entry.status != "queued":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only queued entries can be marked as processing",
        )

    entry = priority_queue_service.mark_as_processing(db, entry_id=entry_id)
    return entry


@router.post("/{entry_id}/assign", response_model=PriorityQueueEntryResponse)
def mark_as_assigned(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Mark entry as assigned to courier

    Business Logic:
    - Updates status to ASSIGNED
    - Records assignment time
    - Calculates time spent in queue
    - Removes from active queue
    - Updates remaining queue positions
    """
    entry = priority_queue_service.get(db, id=entry_id)
    if not entry or entry.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Queue entry not found")

    if entry.status not in ["queued", "processing"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only queued or processing entries can be assigned",
        )

    entry = priority_queue_service.mark_as_assigned(db, entry_id=entry_id)
    return entry


@router.post("/{entry_id}/complete", response_model=PriorityQueueEntryResponse)
def mark_as_completed(
    entry_id: int,
    sla_met: bool,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Mark entry as completed

    Business Logic:
    - Updates status to COMPLETED
    - Records completion time
    - Records SLA compliance
    - If SLA not met, calculates breach duration
    - Used for reporting and analytics
    """
    entry = priority_queue_service.get(db, id=entry_id)
    if not entry or entry.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Queue entry not found")

    entry = priority_queue_service.mark_as_completed(db, entry_id=entry_id, sla_met=sla_met)
    return entry


@router.post("/{entry_id}/expire", response_model=PriorityQueueEntryResponse)
def mark_as_expired(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Mark entry as expired (SLA breached while in queue)

    Business Logic:
    - Updates status to EXPIRED
    - Records expiration time
    - Calculates SLA breach duration
    - Triggers escalation
    - Requires immediate action
    """
    entry = priority_queue_service.get(db, id=entry_id)
    if not entry or entry.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Queue entry not found")

    if entry.status != "queued":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only queued entries can be marked as expired",
        )

    entry = priority_queue_service.mark_as_expired(db, entry_id=entry_id)
    return entry


@router.post("/{entry_id}/escalate", response_model=PriorityQueueEntryResponse)
def escalate_entry(
    entry_id: int,
    escalation: PriorityQueueEntryEscalate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Escalate queue entry to supervisor/manager

    Business Logic:
    - Marks entry as escalated
    - Records escalation reason
    - Assigns to escalation handler
    - Can optionally boost priority
    - Sends escalation notifications
    """
    entry = priority_queue_service.get(db, id=entry_id)
    if not entry or entry.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Queue entry not found")

    # Escalate the entry
    entry = priority_queue_service.escalate(
        db,
        entry_id=entry_id,
        reason=escalation.escalation_reason,
        escalated_to_id=escalation.escalated_to_id,
    )

    # Optionally update priority
    if escalation.new_priority:
        entry_update = PriorityQueueEntryUpdate(priority=escalation.new_priority)
        entry = priority_queue_service.update(db, db_obj=entry, obj_in=entry_update)

    return entry


@router.get("/delivery/{delivery_id}/position", response_model=QueuePosition)
def get_queue_position(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get current position in queue for a delivery

    Returns:
    - Current position number
    - Total entries in queue
    - Estimated wait time
    - Priority level
    - SLA risk status
    """
    entry = priority_queue_service.get_by_delivery(db, delivery_id=delivery_id, organization_id=current_org.id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not in queue")

    # Get total queued count
    all_queued = priority_queue_service.get_queued(db, skip=0, limit=10000, organization_id=current_org.id)
    total_in_queue = len(all_queued)

    position = QueuePosition(
        delivery_id=delivery_id,
        queue_number=entry.queue_number,
        current_position=entry.queue_position or 0,
        total_in_queue=total_in_queue,
        estimated_wait_minutes=entry.estimated_wait_time_minutes or 0,
        priority=entry.priority,
        is_at_risk=entry.is_at_risk if hasattr(entry, "is_at_risk") else False,
    )

    return position


@router.get("/metrics", response_model=QueueMetrics)
def get_queue_metrics(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get priority queue metrics

    Returns:
    - Total entries by status
    - Average wait time
    - Average processing time
    - SLA compliance rate
    - Escalation rate
    - Entries by priority distribution
    """
    # TODO: Calculate comprehensive metrics with organization_id filter
    # For now, return placeholder
    return QueueMetrics(
        total_entries=0,
        queued_entries=0,
        processing_entries=0,
        assigned_entries=0,
        completed_entries=0,
        expired_entries=0,
        avg_wait_time_minutes=0.0,
        avg_processing_time_minutes=0.0,
        sla_compliance_rate=0.0,
        escalation_rate=0.0,
        entries_by_priority={},
    )
