"""Support Tickets API Routes"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.support import TicketCategory, TicketPriority, TicketStatus, EscalationLevel
from app.schemas.support import (
    TicketCreate, TicketCreateFromTemplate, TicketUpdate, TicketResponse, TicketList,
    TicketAssign, TicketResolve, TicketEscalate, TicketMerge, TicketBulkAction,
    TicketSLAConfig, TicketStatistics, TicketWithRelations,
    TicketReplyCreate, TicketReplyResponse,
    TicketTemplateCreate, TicketTemplateUpdate, TicketTemplateResponse,
    CannedResponseCreate, CannedResponseUpdate, CannedResponseResponse
)
from app.services.support import (
    ticket_service, ticket_reply_service,
    ticket_template_service, canned_response_service
)


router = APIRouter()


@router.get("/", response_model=List[TicketList])
def get_tickets(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[TicketCategory] = None,
    priority: Optional[TicketPriority] = None,
    status_filter: Optional[TicketStatus] = Query(None, alias="status"),
    courier_id: Optional[int] = None,
    assigned_to: Optional[int] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Get list of tickets with filtering

    Filters:
    - category: Filter by ticket category
    - priority: Filter by priority level
    - status: Filter by ticket status
    - courier_id: Filter by courier ID
    - assigned_to: Filter by assigned user ID
    """
    if category:
        return ticket_service.get_by_category(db, category=category, skip=skip, limit=limit)

    if priority:
        return ticket_service.get_by_priority(db, priority=priority, skip=skip, limit=limit)

    if status_filter:
        return ticket_service.get_by_status(db, status=status_filter, skip=skip, limit=limit)

    if courier_id:
        return ticket_service.get_by_courier(db, courier_id=courier_id, skip=skip, limit=limit)

    if assigned_to:
        return ticket_service.get_by_assignee(db, user_id=assigned_to, skip=skip, limit=limit)

    return ticket_service.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket_in: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new support ticket"""
    return ticket_service.create_with_user(db, obj_in=ticket_in, user_id=current_user.id)


@router.get("/statistics", response_model=TicketStatistics)
def get_ticket_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get ticket statistics"""
    return ticket_service.get_statistics(db)


@router.get("/open", response_model=List[TicketList])
def get_open_tickets(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get all open tickets (open, in_progress, pending)"""
    return ticket_service.get_open_tickets(db, skip=skip, limit=limit)


@router.get("/my-tickets", response_model=List[TicketList])
def get_my_tickets(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get tickets created by current user"""
    return ticket_service.get_by_creator(db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/assigned-to-me", response_model=List[TicketList])
def get_assigned_tickets(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get tickets assigned to current user"""
    return ticket_service.get_by_assignee(db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get ticket by ID"""
    ticket = ticket_service.get(db, id=ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    return ticket


@router.put("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    ticket_in: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update ticket"""
    ticket = ticket_service.get(db, id=ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    return ticket_service.update(db, db_obj=ticket, obj_in=ticket_in)


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete ticket"""
    ticket = ticket_service.get(db, id=ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    ticket_service.remove(db, id=ticket_id)


@router.post("/{ticket_id}/assign", response_model=TicketResponse)
def assign_ticket(
    ticket_id: int,
    assign_data: TicketAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Assign ticket to a user"""
    ticket = ticket_service.get(db, id=ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    return ticket_service.assign_ticket(
        db,
        ticket_id=ticket_id,
        user_id=assign_data.assigned_to
    )


@router.post("/{ticket_id}/resolve", response_model=TicketResponse)
def resolve_ticket(
    ticket_id: int,
    resolve_data: TicketResolve,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark ticket as resolved"""
    ticket = ticket_service.get(db, id=ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    return ticket_service.resolve_ticket(
        db,
        ticket_id=ticket_id,
        resolution=resolve_data.resolution
    )


@router.post("/{ticket_id}/close", response_model=TicketResponse)
def close_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Close ticket"""
    ticket = ticket_service.get(db, id=ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    return ticket_service.close_ticket(db, ticket_id=ticket_id)


@router.post("/{ticket_id}/reopen", response_model=TicketResponse)
def reopen_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reopen a closed ticket"""
    ticket = ticket_service.get(db, id=ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    return ticket_service.reopen_ticket(db, ticket_id=ticket_id)


@router.get("/{ticket_id}/replies", response_model=List[TicketReplyResponse])
def get_ticket_replies(
    ticket_id: int,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get all replies for a ticket"""
    ticket = ticket_service.get(db, id=ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    return ticket_reply_service.get_by_ticket(
        db,
        ticket_id=ticket_id,
        skip=skip,
        limit=limit
    )


@router.post("/{ticket_id}/replies", response_model=TicketReplyResponse, status_code=status.HTTP_201_CREATED)
def create_ticket_reply(
    ticket_id: int,
    reply_in: TicketReplyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a reply to a ticket"""
    ticket = ticket_service.get(db, id=ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    # Record first response if this is the first reply
    ticket_service.record_first_response(db, ticket_id=ticket_id)

    # Set ticket_id from URL
    reply_in.ticket_id = ticket_id
    return ticket_reply_service.create(db, obj_in=reply_in)


# =============================================================================
# SLA Management Endpoints
# =============================================================================

@router.post("/{ticket_id}/sla", response_model=TicketResponse)
def set_ticket_sla(
    ticket_id: int,
    sla_config: TicketSLAConfig,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Set SLA deadline for a ticket"""
    ticket = ticket_service.set_sla(db, ticket_id=ticket_id, sla_hours=sla_config.sla_hours)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    return ticket


@router.get("/sla/breached", response_model=List[TicketList])
def get_sla_breached_tickets(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get tickets that have breached SLA"""
    return ticket_service.get_sla_breached_tickets(db, skip=skip, limit=limit)


@router.get("/sla/at-risk", response_model=List[TicketList])
def get_sla_at_risk_tickets(
    db: Session = Depends(get_db),
    hours_threshold: int = Query(2, ge=1, le=24, description="Hours threshold to consider at risk"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get tickets at risk of breaching SLA within threshold hours"""
    return ticket_service.get_sla_at_risk_tickets(
        db, hours_threshold=hours_threshold, skip=skip, limit=limit
    )


# =============================================================================
# Escalation Endpoints
# =============================================================================

@router.post("/{ticket_id}/escalate", response_model=TicketResponse)
def escalate_ticket(
    ticket_id: int,
    escalate_data: TicketEscalate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Escalate a ticket to a higher level"""
    ticket = ticket_service.escalate_ticket(
        db,
        ticket_id=ticket_id,
        escalation_level=escalate_data.escalation_level,
        reason=escalate_data.reason,
        escalated_by=current_user.id,
        assign_to=escalate_data.assign_to
    )
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    return ticket


@router.post("/{ticket_id}/de-escalate", response_model=TicketResponse)
def de_escalate_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove escalation from a ticket"""
    ticket = ticket_service.de_escalate_ticket(db, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    return ticket


@router.get("/escalated", response_model=List[TicketList])
def get_escalated_tickets(
    db: Session = Depends(get_db),
    level: Optional[EscalationLevel] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get all escalated tickets, optionally filtered by level"""
    return ticket_service.get_escalated_tickets(db, level=level, skip=skip, limit=limit)


# =============================================================================
# Merge Endpoints
# =============================================================================

@router.post("/merge", response_model=TicketResponse)
def merge_tickets(
    merge_data: TicketMerge,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Merge multiple tickets into a target ticket"""
    target_ticket = ticket_service.merge_tickets(
        db,
        source_ticket_ids=merge_data.source_ticket_ids,
        target_ticket_id=merge_data.target_ticket_id
    )
    if not target_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target ticket not found"
        )

    # Add merge note as a reply if provided
    if merge_data.merge_note:
        ticket_reply_service.create(
            db,
            obj_in={
                "ticket_id": target_ticket.id,
                "message": f"Merged tickets: {merge_data.source_ticket_ids}\n\n{merge_data.merge_note}",
                "is_internal": True,
                "user_id": current_user.id
            }
        )

    return target_ticket


@router.get("/{ticket_id}/merged", response_model=List[TicketList])
def get_merged_tickets(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all tickets merged into a target ticket"""
    return ticket_service.get_merged_tickets(db, target_ticket_id=ticket_id)


# =============================================================================
# Bulk Operations Endpoints
# =============================================================================

@router.post("/bulk", status_code=status.HTTP_200_OK)
def bulk_ticket_action(
    bulk_data: TicketBulkAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Perform bulk operations on multiple tickets"""
    action = bulk_data.action.lower()

    if action == "assign" and bulk_data.assigned_to:
        count = ticket_service.bulk_assign(
            db, ticket_ids=bulk_data.ticket_ids, assigned_to=bulk_data.assigned_to
        )
        return {"action": action, "affected_tickets": count}

    elif action == "change_status" and bulk_data.status:
        count = ticket_service.bulk_change_status(
            db, ticket_ids=bulk_data.ticket_ids, status=bulk_data.status
        )
        return {"action": action, "affected_tickets": count}

    elif action == "change_priority" and bulk_data.priority:
        count = ticket_service.bulk_change_priority(
            db, ticket_ids=bulk_data.ticket_ids, priority=bulk_data.priority
        )
        return {"action": action, "affected_tickets": count}

    elif action == "close":
        count = ticket_service.bulk_close(db, ticket_ids=bulk_data.ticket_ids)
        return {"action": action, "affected_tickets": count}

    elif action == "delete":
        count = ticket_service.bulk_delete(db, ticket_ids=bulk_data.ticket_ids)
        return {"action": action, "affected_tickets": count}

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action: {action}. Supported actions: assign, change_status, change_priority, close, delete"
        )


# =============================================================================
# Search and Filter Endpoints
# =============================================================================

@router.get("/search", response_model=List[TicketList])
def search_tickets(
    q: str = Query(..., min_length=2, description="Search query"),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Search tickets by subject, description, ticket ID, or tags"""
    return ticket_service.search_tickets(db, query=q, skip=skip, limit=limit)


@router.get("/unassigned", response_model=List[TicketList])
def get_unassigned_tickets(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get all unassigned tickets"""
    return ticket_service.get_unassigned_tickets(db, skip=skip, limit=limit)


@router.get("/department/{department}", response_model=List[TicketList])
def get_tickets_by_department(
    department: str,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get tickets by department"""
    return ticket_service.get_by_department(db, department=department, skip=skip, limit=limit)


# =============================================================================
# Template Endpoints
# =============================================================================

@router.get("/templates", response_model=List[TicketTemplateResponse])
def get_ticket_templates(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
):
    """Get ticket templates"""
    if active_only:
        return ticket_template_service.get_active_templates(db, skip=skip, limit=limit)
    return ticket_template_service.get_multi(db, skip=skip, limit=limit)


@router.post("/templates", response_model=TicketTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_ticket_template(
    template_in: TicketTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new ticket template"""
    # Check if name already exists
    existing = ticket_template_service.get_by_name(db, name=template_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template with this name already exists"
        )
    return ticket_template_service.create_template(
        db, obj_in=template_in, created_by=current_user.id
    )


@router.get("/templates/{template_id}", response_model=TicketTemplateResponse)
def get_ticket_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a ticket template by ID"""
    template = ticket_template_service.get(db, id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    return template


@router.put("/templates/{template_id}", response_model=TicketTemplateResponse)
def update_ticket_template(
    template_id: int,
    template_in: TicketTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a ticket template"""
    template = ticket_template_service.get(db, id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    return ticket_template_service.update(db, db_obj=template, obj_in=template_in)


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a ticket template"""
    template = ticket_template_service.get(db, id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    ticket_template_service.delete(db, id=template_id)


@router.post("/from-template", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket_from_template(
    template_data: TicketCreateFromTemplate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a ticket from a template"""
    overrides = {}
    if template_data.subject:
        overrides['subject'] = template_data.subject
    if template_data.description:
        overrides['description'] = template_data.description
    if template_data.courier_id:
        overrides['courier_id'] = template_data.courier_id
    if template_data.custom_fields:
        overrides['custom_fields'] = template_data.custom_fields

    ticket = ticket_template_service.create_ticket_from_template(
        db,
        template_id=template_data.template_id,
        created_by=current_user.id,
        overrides=overrides if overrides else None
    )
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    return ticket


# =============================================================================
# Canned Response Endpoints
# =============================================================================

@router.get("/canned-responses", response_model=List[CannedResponseResponse])
def get_canned_responses(
    db: Session = Depends(get_db),
    category: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get canned responses, optionally filtered by category"""
    if category:
        return canned_response_service.get_by_category(
            db, category=category, skip=skip, limit=limit
        )
    return canned_response_service.get_active_responses(db, skip=skip, limit=limit)


@router.post("/canned-responses", response_model=CannedResponseResponse, status_code=status.HTTP_201_CREATED)
def create_canned_response(
    response_in: CannedResponseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new canned response"""
    # Check if shortcut already exists
    if response_in.shortcut:
        existing = canned_response_service.get_by_shortcut(db, shortcut=response_in.shortcut)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Canned response with this shortcut already exists"
            )
    return canned_response_service.create_response(
        db, obj_in=response_in, created_by=current_user.id
    )


@router.get("/canned-responses/categories")
def get_canned_response_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get list of canned response categories with counts"""
    return canned_response_service.get_categories(db)


@router.get("/canned-responses/search", response_model=List[CannedResponseResponse])
def search_canned_responses(
    q: str = Query(..., min_length=2, description="Search query"),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Search canned responses by title or content"""
    return canned_response_service.search_responses(db, query=q, skip=skip, limit=limit)


@router.get("/canned-responses/{response_id}", response_model=CannedResponseResponse)
def get_canned_response(
    response_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a canned response by ID"""
    response = canned_response_service.get(db, id=response_id)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Canned response not found"
        )
    return response


@router.put("/canned-responses/{response_id}", response_model=CannedResponseResponse)
def update_canned_response(
    response_id: int,
    response_in: CannedResponseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a canned response"""
    response = canned_response_service.get(db, id=response_id)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Canned response not found"
        )
    return canned_response_service.update(db, db_obj=response, obj_in=response_in)


@router.delete("/canned-responses/{response_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_canned_response(
    response_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a canned response"""
    response = canned_response_service.get(db, id=response_id)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Canned response not found"
        )
    canned_response_service.delete(db, id=response_id)


@router.post("/canned-responses/{response_id}/use")
def use_canned_response(
    response_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Increment usage count and get canned response content"""
    response = canned_response_service.increment_usage(db, response_id=response_id)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Canned response not found"
        )
    return {"content": response.content}
