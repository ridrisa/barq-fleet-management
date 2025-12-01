"""Ticket Service"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from datetime import datetime

from app.services.base import CRUDBase
from app.models.support import Ticket, TicketCategory, TicketPriority, TicketStatus
from app.schemas.support import TicketCreate, TicketUpdate


class TicketService(CRUDBase[Ticket, TicketCreate, TicketUpdate]):
    """Service for ticket management operations"""

    def create(self, db: Session, *, obj_in: TicketCreate, created_by: int) -> Ticket:
        """
        Create a new ticket with auto-generated ticket_id

        Args:
            db: Database session
            obj_in: Ticket creation data
            created_by: User ID who is creating the ticket

        Returns:
            Created ticket object
        """
        # Generate ticket ID (format: TKT-YYYYMMDD-NNN)
        today = datetime.now()
        date_prefix = today.strftime("%Y%m%d")

        # Count today's tickets to get next sequence number
        today_count = db.query(func.count(self.model.id)).filter(
            func.date(self.model.created_at) == today.date()
        ).scalar() or 0

        ticket_id = f"TKT-{date_prefix}-{(today_count + 1):03d}"

        # Create ticket
        obj_in_data = obj_in.model_dump()
        obj_in_data['ticket_id'] = ticket_id
        obj_in_data['created_by'] = created_by

        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_courier(
        self, db: Session, *, courier_id: int, skip: int = 0, limit: int = 100
    ) -> List[Ticket]:
        """Get all tickets for a specific courier"""
        return (
            db.query(self.model)
            .filter(self.model.courier_id == courier_id)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_category(
        self, db: Session, *, category: TicketCategory, skip: int = 0, limit: int = 100
    ) -> List[Ticket]:
        """Get tickets by category"""
        return (
            db.query(self.model)
            .filter(self.model.category == category)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(
        self, db: Session, *, status: TicketStatus, skip: int = 0, limit: int = 100
    ) -> List[Ticket]:
        """Get tickets by status"""
        return (
            db.query(self.model)
            .filter(self.model.status == status)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_priority(
        self, db: Session, *, priority: TicketPriority, skip: int = 0, limit: int = 100
    ) -> List[Ticket]:
        """Get tickets by priority"""
        return (
            db.query(self.model)
            .filter(self.model.priority == priority)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_assigned_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Ticket]:
        """Get tickets assigned to a specific user"""
        return (
            db.query(self.model)
            .filter(self.model.assigned_to == user_id)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_creator(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Ticket]:
        """Get tickets created by a specific user"""
        return (
            db.query(self.model)
            .filter(self.model.created_by == user_id)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_open_tickets(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Ticket]:
        """Get all open tickets (open, in_progress, pending)"""
        return (
            db.query(self.model)
            .filter(
                self.model.status.in_([
                    TicketStatus.OPEN,
                    TicketStatus.IN_PROGRESS,
                    TicketStatus.PENDING
                ])
            )
            .order_by(self.model.priority.desc(), self.model.created_at)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_unassigned_tickets(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Ticket]:
        """Get unassigned tickets"""
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.assigned_to.is_(None),
                    self.model.status.in_([
                        TicketStatus.OPEN,
                        TicketStatus.IN_PROGRESS,
                        TicketStatus.PENDING
                    ])
                )
            )
            .order_by(self.model.priority.desc(), self.model.created_at)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def assign_ticket(
        self, db: Session, *, ticket_id: int, assigned_to: int
    ) -> Optional[Ticket]:
        """Assign a ticket to a user"""
        ticket = db.query(self.model).filter(self.model.id == ticket_id).first()
        if not ticket:
            return None

        ticket.assigned_to = assigned_to

        # If ticket is open, move it to in_progress
        if ticket.status == TicketStatus.OPEN:
            ticket.status = TicketStatus.IN_PROGRESS

        db.commit()
        db.refresh(ticket)
        return ticket

    def resolve_ticket(
        self, db: Session, *, ticket_id: int, resolution: str
    ) -> Optional[Ticket]:
        """Mark a ticket as resolved"""
        ticket = db.query(self.model).filter(self.model.id == ticket_id).first()
        if not ticket:
            return None

        ticket.status = TicketStatus.RESOLVED
        ticket.resolution = resolution
        ticket.resolved_at = datetime.now()

        db.commit()
        db.refresh(ticket)
        return ticket

    def close_ticket(
        self, db: Session, *, ticket_id: int
    ) -> Optional[Ticket]:
        """Close a resolved ticket"""
        ticket = db.query(self.model).filter(self.model.id == ticket_id).first()
        if not ticket:
            return None

        ticket.status = TicketStatus.CLOSED
        ticket.closed_at = datetime.now()

        db.commit()
        db.refresh(ticket)
        return ticket

    def reopen_ticket(
        self, db: Session, *, ticket_id: int
    ) -> Optional[Ticket]:
        """Reopen a closed or resolved ticket"""
        ticket = db.query(self.model).filter(self.model.id == ticket_id).first()
        if not ticket:
            return None

        ticket.status = TicketStatus.OPEN
        ticket.resolved_at = None
        ticket.closed_at = None
        ticket.resolution = None

        db.commit()
        db.refresh(ticket)
        return ticket

    def get_statistics(self, db: Session) -> Dict:
        """
        Get ticket statistics

        Returns:
            Dictionary with various ticket statistics
        """
        total = db.query(func.count(self.model.id)).scalar() or 0

        # Count by status
        open_count = db.query(func.count(self.model.id)).filter(
            self.model.status == TicketStatus.OPEN
        ).scalar() or 0

        in_progress_count = db.query(func.count(self.model.id)).filter(
            self.model.status == TicketStatus.IN_PROGRESS
        ).scalar() or 0

        pending_count = db.query(func.count(self.model.id)).filter(
            self.model.status == TicketStatus.PENDING
        ).scalar() or 0

        resolved_count = db.query(func.count(self.model.id)).filter(
            self.model.status == TicketStatus.RESOLVED
        ).scalar() or 0

        closed_count = db.query(func.count(self.model.id)).filter(
            self.model.status == TicketStatus.CLOSED
        ).scalar() or 0

        # Count by category
        by_category = {}
        for category in TicketCategory:
            count = db.query(func.count(self.model.id)).filter(
                self.model.category == category
            ).scalar() or 0
            by_category[category.value] = count

        # Count by priority
        by_priority = {}
        for priority in TicketPriority:
            count = db.query(func.count(self.model.id)).filter(
                self.model.priority == priority
            ).scalar() or 0
            by_priority[priority.value] = count

        # Calculate average resolution time
        resolved_tickets = db.query(self.model).filter(
            and_(
                self.model.status == TicketStatus.RESOLVED,
                self.model.resolved_at.isnot(None)
            )
        ).all()

        avg_resolution_time = 0.0
        if resolved_tickets:
            total_hours = 0
            for ticket in resolved_tickets:
                delta = ticket.resolved_at - ticket.created_at
                total_hours += delta.total_seconds() / 3600
            avg_resolution_time = total_hours / len(resolved_tickets)

        return {
            "total": total,
            "open": open_count,
            "in_progress": in_progress_count,
            "pending": pending_count,
            "resolved": resolved_count,
            "closed": closed_count,
            "by_category": by_category,
            "by_priority": by_priority,
            "avg_resolution_time_hours": round(avg_resolution_time, 2)
        }


ticket_service = TicketService(Ticket)
