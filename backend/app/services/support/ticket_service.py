"""Ticket Service"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, extract, func, or_
from sqlalchemy.orm import Session

from app.models.support import EscalationLevel, Ticket, TicketCategory, TicketPriority, TicketStatus
from app.schemas.support import TicketCreate, TicketUpdate
from app.services.base import CRUDBase


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
        today_count = (
            db.query(func.count(self.model.id))
            .filter(func.date(self.model.created_at) == today.date())
            .scalar()
            or 0
        )

        ticket_id = f"TKT-{date_prefix}-{(today_count + 1):03d}"

        # Create ticket
        obj_in_data = obj_in.model_dump()
        obj_in_data["ticket_id"] = ticket_id
        obj_in_data["created_by"] = created_by

        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_with_sla(
        self, db: Session, *, obj_in: TicketCreate, created_by: int, sla_hours: int
    ) -> Ticket:
        """Create ticket with SLA deadline"""
        ticket = self.create(db, obj_in=obj_in, created_by=created_by)
        ticket.sla_due_at = datetime.now(timezone.utc) + timedelta(hours=sla_hours)
        db.commit()
        db.refresh(ticket)
        return ticket

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

    def get_open_tickets(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Ticket]:
        """Get all open tickets (open, in_progress, pending)"""
        return (
            db.query(self.model)
            .filter(
                self.model.status.in_(
                    [TicketStatus.OPEN, TicketStatus.IN_PROGRESS, TicketStatus.PENDING]
                )
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
                    self.model.status.in_(
                        [TicketStatus.OPEN, TicketStatus.IN_PROGRESS, TicketStatus.PENDING]
                    ),
                )
            )
            .order_by(self.model.priority.desc(), self.model.created_at)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def assign_ticket(self, db: Session, *, ticket_id: int, assigned_to: int) -> Optional[Ticket]:
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

    def resolve_ticket(self, db: Session, *, ticket_id: int, resolution: str) -> Optional[Ticket]:
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

    def close_ticket(self, db: Session, *, ticket_id: int) -> Optional[Ticket]:
        """Close a resolved ticket"""
        ticket = db.query(self.model).filter(self.model.id == ticket_id).first()
        if not ticket:
            return None

        ticket.status = TicketStatus.CLOSED
        ticket.closed_at = datetime.now()

        db.commit()
        db.refresh(ticket)
        return ticket

    def reopen_ticket(self, db: Session, *, ticket_id: int) -> Optional[Ticket]:
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
        open_count = (
            db.query(func.count(self.model.id))
            .filter(self.model.status == TicketStatus.OPEN)
            .scalar()
            or 0
        )

        in_progress_count = (
            db.query(func.count(self.model.id))
            .filter(self.model.status == TicketStatus.IN_PROGRESS)
            .scalar()
            or 0
        )

        pending_count = (
            db.query(func.count(self.model.id))
            .filter(self.model.status == TicketStatus.PENDING)
            .scalar()
            or 0
        )

        resolved_count = (
            db.query(func.count(self.model.id))
            .filter(self.model.status == TicketStatus.RESOLVED)
            .scalar()
            or 0
        )

        closed_count = (
            db.query(func.count(self.model.id))
            .filter(self.model.status == TicketStatus.CLOSED)
            .scalar()
            or 0
        )

        # Count by category
        by_category = {}
        for category in TicketCategory:
            count = (
                db.query(func.count(self.model.id)).filter(self.model.category == category).scalar()
                or 0
            )
            by_category[category.value] = count

        # Count by priority
        by_priority = {}
        for priority in TicketPriority:
            count = (
                db.query(func.count(self.model.id)).filter(self.model.priority == priority).scalar()
                or 0
            )
            by_priority[priority.value] = count

        # Calculate average resolution time
        resolved_tickets = (
            db.query(self.model)
            .filter(
                and_(self.model.status == TicketStatus.RESOLVED, self.model.resolved_at.isnot(None))
            )
            .all()
        )

        avg_resolution_time = 0.0
        if resolved_tickets:
            total_hours = 0
            for ticket in resolved_tickets:
                delta = ticket.resolved_at - ticket.created_at
                total_hours += delta.total_seconds() / 3600
            avg_resolution_time = total_hours / len(resolved_tickets)

        # Count by escalation
        by_escalation = {}
        for level in EscalationLevel:
            count = (
                db.query(func.count(self.model.id))
                .filter(self.model.escalation_level == level)
                .scalar()
                or 0
            )
            by_escalation[level.value] = count

        escalated_count = (
            db.query(func.count(self.model.id))
            .filter(self.model.escalation_level != EscalationLevel.NONE)
            .scalar()
            or 0
        )

        merged_count = (
            db.query(func.count(self.model.id)).filter(self.model.is_merged == True).scalar() or 0
        )

        # Calculate average first response time
        tickets_with_response = (
            db.query(self.model).filter(self.model.first_response_at.isnot(None)).all()
        )

        avg_first_response_minutes = 0.0
        if tickets_with_response:
            total_minutes = 0
            for ticket in tickets_with_response:
                delta = ticket.first_response_at - ticket.created_at
                total_minutes += delta.total_seconds() / 60
            avg_first_response_minutes = total_minutes / len(tickets_with_response)

        # Calculate SLA compliance rate
        tickets_with_sla = db.query(self.model).filter(self.model.sla_due_at.isnot(None)).all()

        sla_compliance_rate = 0.0
        if tickets_with_sla:
            compliant_count = sum(1 for t in tickets_with_sla if not t.sla_breached)
            sla_compliance_rate = (compliant_count / len(tickets_with_sla)) * 100

        return {
            "total": total,
            "open": open_count,
            "in_progress": in_progress_count,
            "waiting": pending_count,
            "resolved": resolved_count,
            "closed": closed_count,
            "by_category": by_category,
            "by_priority": by_priority,
            "by_escalation": by_escalation,
            "avg_resolution_time_hours": round(avg_resolution_time, 2),
            "avg_first_response_minutes": round(avg_first_response_minutes, 2),
            "sla_compliance_rate": round(sla_compliance_rate, 2),
            "escalated_count": escalated_count,
            "merged_count": merged_count,
        }

    # SLA Management
    def set_sla(self, db: Session, *, ticket_id: int, sla_hours: int) -> Optional[Ticket]:
        """Set SLA deadline for a ticket"""
        ticket = db.query(self.model).filter(self.model.id == ticket_id).first()
        if not ticket:
            return None

        ticket.sla_due_at = datetime.now(timezone.utc) + timedelta(hours=sla_hours)
        db.commit()
        db.refresh(ticket)
        return ticket

    def record_first_response(self, db: Session, *, ticket_id: int) -> Optional[Ticket]:
        """Record first response time for a ticket"""
        ticket = db.query(self.model).filter(self.model.id == ticket_id).first()
        if not ticket or ticket.first_response_at:
            return ticket

        ticket.first_response_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(ticket)
        return ticket

    def check_sla_breach(self, db: Session, *, ticket_id: int) -> Optional[Ticket]:
        """Check and update SLA breach status"""
        ticket = db.query(self.model).filter(self.model.id == ticket_id).first()
        if not ticket or not ticket.sla_due_at:
            return ticket

        if ticket.sla_due_at < datetime.now(timezone.utc) and not ticket.sla_breached:
            ticket.sla_breached = True
            db.commit()
            db.refresh(ticket)

        return ticket

    def get_sla_breached_tickets(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Ticket]:
        """Get tickets that have breached SLA"""
        return (
            db.query(self.model)
            .filter(self.model.sla_breached == True)
            .order_by(self.model.sla_due_at)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_sla_at_risk_tickets(
        self, db: Session, *, hours_threshold: int = 2, skip: int = 0, limit: int = 100
    ) -> List[Ticket]:
        """Get tickets at risk of breaching SLA"""
        threshold_time = datetime.now(timezone.utc) + timedelta(hours=hours_threshold)
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.sla_due_at.isnot(None),
                    self.model.sla_breached == False,
                    self.model.sla_due_at <= threshold_time,
                    self.model.status.in_(
                        [TicketStatus.OPEN, TicketStatus.IN_PROGRESS, TicketStatus.PENDING]
                    ),
                )
            )
            .order_by(self.model.sla_due_at)
            .offset(skip)
            .limit(limit)
            .all()
        )

    # Escalation Management
    def escalate_ticket(
        self,
        db: Session,
        *,
        ticket_id: int,
        escalation_level: EscalationLevel,
        reason: str,
        escalated_by: int,
        assign_to: Optional[int] = None,
    ) -> Optional[Ticket]:
        """Escalate a ticket to a higher level"""
        ticket = db.query(self.model).filter(self.model.id == ticket_id).first()
        if not ticket:
            return None

        ticket.escalation_level = escalation_level
        ticket.escalation_reason = reason
        ticket.escalated_by = escalated_by
        ticket.escalated_at = datetime.now(timezone.utc)

        if assign_to:
            ticket.assigned_to = assign_to

        db.commit()
        db.refresh(ticket)
        return ticket

    def get_escalated_tickets(
        self,
        db: Session,
        *,
        level: Optional[EscalationLevel] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Ticket]:
        """Get escalated tickets, optionally filtered by level"""
        query = db.query(self.model).filter(self.model.escalation_level != EscalationLevel.NONE)

        if level:
            query = query.filter(self.model.escalation_level == level)

        return query.order_by(self.model.escalated_at.desc()).offset(skip).limit(limit).all()

    def de_escalate_ticket(self, db: Session, *, ticket_id: int) -> Optional[Ticket]:
        """Remove escalation from a ticket"""
        ticket = db.query(self.model).filter(self.model.id == ticket_id).first()
        if not ticket:
            return None

        ticket.escalation_level = EscalationLevel.NONE
        ticket.escalation_reason = None
        ticket.escalated_by = None
        ticket.escalated_at = None

        db.commit()
        db.refresh(ticket)
        return ticket

    # Ticket Merge Operations
    def merge_tickets(
        self, db: Session, *, source_ticket_ids: List[int], target_ticket_id: int
    ) -> Optional[Ticket]:
        """Merge multiple tickets into a target ticket"""
        target_ticket = db.query(self.model).filter(self.model.id == target_ticket_id).first()
        if not target_ticket:
            return None

        # Mark source tickets as merged
        for source_id in source_ticket_ids:
            if source_id == target_ticket_id:
                continue

            source_ticket = db.query(self.model).filter(self.model.id == source_id).first()
            if source_ticket:
                source_ticket.is_merged = True
                source_ticket.merged_into_id = target_ticket_id
                source_ticket.status = TicketStatus.CLOSED
                source_ticket.closed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(target_ticket)
        return target_ticket

    def get_merged_tickets(self, db: Session, *, target_ticket_id: int) -> List[Ticket]:
        """Get all tickets merged into a target ticket"""
        return db.query(self.model).filter(self.model.merged_into_id == target_ticket_id).all()

    # Bulk Operations
    def bulk_assign(self, db: Session, *, ticket_ids: List[int], assigned_to: int) -> int:
        """Assign multiple tickets to a user"""
        result = (
            db.query(self.model)
            .filter(self.model.id.in_(ticket_ids))
            .update(
                {"assigned_to": assigned_to, "status": TicketStatus.IN_PROGRESS},
                synchronize_session=False,
            )
        )
        db.commit()
        return result

    def bulk_change_status(
        self, db: Session, *, ticket_ids: List[int], status: TicketStatus
    ) -> int:
        """Change status of multiple tickets"""
        update_data = {"status": status}
        if status == TicketStatus.CLOSED:
            update_data["closed_at"] = datetime.now(timezone.utc)
        elif status == TicketStatus.RESOLVED:
            update_data["resolved_at"] = datetime.now(timezone.utc)

        result = (
            db.query(self.model)
            .filter(self.model.id.in_(ticket_ids))
            .update(update_data, synchronize_session=False)
        )
        db.commit()
        return result

    def bulk_change_priority(
        self, db: Session, *, ticket_ids: List[int], priority: TicketPriority
    ) -> int:
        """Change priority of multiple tickets"""
        result = (
            db.query(self.model)
            .filter(self.model.id.in_(ticket_ids))
            .update({"priority": priority}, synchronize_session=False)
        )
        db.commit()
        return result

    def bulk_close(self, db: Session, *, ticket_ids: List[int]) -> int:
        """Close multiple tickets"""
        result = (
            db.query(self.model)
            .filter(self.model.id.in_(ticket_ids))
            .update(
                {"status": TicketStatus.CLOSED, "closed_at": datetime.now(timezone.utc)},
                synchronize_session=False,
            )
        )
        db.commit()
        return result

    def bulk_delete(self, db: Session, *, ticket_ids: List[int]) -> int:
        """Delete multiple tickets"""
        result = (
            db.query(self.model)
            .filter(self.model.id.in_(ticket_ids))
            .delete(synchronize_session=False)
        )
        db.commit()
        return result

    # Search
    def search_tickets(
        self, db: Session, *, query: str, skip: int = 0, limit: int = 100
    ) -> List[Ticket]:
        """Search tickets by subject or description"""
        return (
            db.query(self.model)
            .filter(
                or_(
                    self.model.subject.ilike(f"%{query}%"),
                    self.model.description.ilike(f"%{query}%"),
                    self.model.ticket_id.ilike(f"%{query}%"),
                    self.model.tags.ilike(f"%{query}%"),
                )
            )
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    # Department-based queries
    def get_by_department(
        self, db: Session, *, department: str, skip: int = 0, limit: int = 100
    ) -> List[Ticket]:
        """Get tickets by department"""
        return (
            db.query(self.model)
            .filter(self.model.department == department)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    # Alias methods for compatibility
    def get_by_assignee(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Ticket]:
        """Alias for get_by_assigned_user"""
        return self.get_by_assigned_user(db, user_id=user_id, skip=skip, limit=limit)

    def create_with_user(self, db: Session, *, obj_in: TicketCreate, user_id: int) -> Ticket:
        """Alias for create with created_by parameter"""
        return self.create(db, obj_in=obj_in, created_by=user_id)


ticket_service = TicketService(Ticket)
