"""Ticket Reply Service"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.services.base import CRUDBase
from app.models.support import TicketReply
from app.schemas.support import TicketReplyCreate, TicketReplyUpdate


class TicketReplyService(CRUDBase[TicketReply, TicketReplyCreate, TicketReplyUpdate]):
    """Service for ticket reply operations"""

    def get_by_ticket(
        self,
        db: Session,
        *,
        ticket_id: int,
        skip: int = 0,
        limit: int = 100,
        include_internal: bool = True
    ) -> List[TicketReply]:
        """
        Get all replies for a specific ticket

        Args:
            db: Database session
            ticket_id: Ticket ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_internal: Whether to include internal notes

        Returns:
            List of ticket replies
        """
        query = db.query(self.model).filter(self.model.ticket_id == ticket_id)

        if not include_internal:
            query = query.filter(self.model.is_internal == 0)

        return query.order_by(self.model.created_at.asc()).offset(skip).limit(limit).all()

    def get_by_user(
        self,
        db: Session,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[TicketReply]:
        """
        Get all replies by a specific user

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of ticket replies
        """
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_ticket(self, db: Session, *, ticket_id: int) -> int:
        """Count replies for a ticket"""
        return db.query(self.model).filter(self.model.ticket_id == ticket_id).count()


# Create service instance
ticket_reply_service = TicketReplyService(TicketReply)
