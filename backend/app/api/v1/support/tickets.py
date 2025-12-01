"""Support Tickets API Routes"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.support import TicketCategory, TicketPriority, TicketStatus
from app.schemas.support import (
    TicketCreate, TicketUpdate, TicketResponse, TicketList,
    TicketAssign, TicketResolve, TicketStatistics, TicketWithRelations,
    TicketReplyCreate, TicketReplyResponse
)
from app.services.support import ticket_service, ticket_reply_service


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

    # Set ticket_id from URL
    reply_in.ticket_id = ticket_id
    return ticket_reply_service.create(db, obj_in=reply_in)
