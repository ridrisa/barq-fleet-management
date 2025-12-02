"""Ticket Template Service"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.services.base import CRUDBase
from app.models.support import TicketTemplate, Ticket, TicketCategory, TicketPriority
from app.schemas.support import TicketTemplateCreate, TicketTemplateUpdate, TicketCreate
from datetime import datetime, timedelta, timezone


class TicketTemplateService(CRUDBase[TicketTemplate, TicketTemplateCreate, TicketTemplateUpdate]):
    """Service for ticket template management"""

    def create_template(
        self, db: Session, *, obj_in: TicketTemplateCreate, created_by: int
    ) -> TicketTemplate:
        """Create a new ticket template"""
        obj_in_data = obj_in.model_dump()
        obj_in_data['created_by'] = created_by

        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_name(self, db: Session, *, name: str) -> Optional[TicketTemplate]:
        """Get template by name"""
        return db.query(self.model).filter(self.model.name == name).first()

    def get_active_templates(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[TicketTemplate]:
        """Get all active templates"""
        return (
            db.query(self.model)
            .filter(self.model.is_active == True)
            .order_by(self.model.name)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_public_templates(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[TicketTemplate]:
        """Get all public and active templates"""
        return (
            db.query(self.model)
            .filter(
                self.model.is_active == True,
                self.model.is_public == True
            )
            .order_by(self.model.name)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_category(
        self, db: Session, *, category: TicketCategory, skip: int = 0, limit: int = 100
    ) -> List[TicketTemplate]:
        """Get templates by default category"""
        return (
            db.query(self.model)
            .filter(
                self.model.is_active == True,
                self.model.default_category == category
            )
            .order_by(self.model.name)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_ticket_from_template(
        self, db: Session, *, template_id: int, created_by: int,
        overrides: Optional[dict] = None
    ) -> Optional[Ticket]:
        """Create a ticket using a template"""
        template = self.get(db, id=template_id)
        if not template:
            return None

        # Build ticket data from template
        ticket_data = {
            'subject': template.default_subject or 'New Ticket',
            'description': template.default_description or 'No description provided',
            'category': template.default_category or TicketCategory.OTHER,
            'priority': template.default_priority or TicketPriority.MEDIUM,
            'department': template.default_department,
            'tags': template.default_tags,
            'custom_fields': template.default_custom_fields,
            'template_id': template_id,
            'created_by': created_by
        }

        # Apply overrides
        if overrides:
            for key, value in overrides.items():
                if value is not None and key in ticket_data:
                    ticket_data[key] = value

        # Generate ticket ID
        today = datetime.now()
        date_prefix = today.strftime("%Y%m%d")
        today_count = db.query(func.count(Ticket.id)).filter(
            func.date(Ticket.created_at) == today.date()
        ).scalar() or 0
        ticket_data['ticket_id'] = f"TKT-{date_prefix}-{(today_count + 1):03d}"

        # Create ticket
        ticket = Ticket(**ticket_data)
        db.add(ticket)

        # Set SLA if configured in template
        if template.sla_hours:
            ticket.sla_due_at = datetime.now(timezone.utc) + timedelta(hours=template.sla_hours)

        db.commit()
        db.refresh(ticket)
        return ticket

    def activate_template(self, db: Session, *, template_id: int) -> Optional[TicketTemplate]:
        """Activate a template"""
        template = self.get(db, id=template_id)
        if not template:
            return None

        template.is_active = True
        db.commit()
        db.refresh(template)
        return template

    def deactivate_template(self, db: Session, *, template_id: int) -> Optional[TicketTemplate]:
        """Deactivate a template"""
        template = self.get(db, id=template_id)
        if not template:
            return None

        template.is_active = False
        db.commit()
        db.refresh(template)
        return template


ticket_template_service = TicketTemplateService(TicketTemplate)
