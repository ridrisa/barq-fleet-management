"""
Unit Tests for Support Ticket Service

Tests cover:
- Ticket CRUD operations
- Status management
- Assignment
- Escalation
- Statistics

Author: BARQ QA Team
Last Updated: 2025-12-10
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch

from app.services.support.ticket_service import TicketService
from app.models.support.ticket import Ticket, TicketPriority, TicketStatus


class TestTicketService:
    """Test Ticket Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create TicketService instance"""
        return TicketService(Ticket)

    # ==================== CRUD TESTS ====================

    def test_create_ticket(self, service, db_session, test_user, test_organization):
        """Test creating a support ticket"""
        from app.schemas.support.ticket import TicketCreate

        ticket_data = TicketCreate(
            title="Login Issue",
            description="Cannot login to the system",
            priority=TicketPriority.HIGH,
            category="technical",
            requester_id=test_user.id,
            organization_id=test_organization.id
        )

        ticket = service.create(db_session, obj_in=ticket_data)

        assert ticket is not None
        assert ticket.title == "Login Issue"
        assert ticket.status == TicketStatus.OPEN
        assert ticket.priority == TicketPriority.HIGH

    def test_get_ticket_by_id(self, service, db_session, ticket_factory, test_user):
        """Test getting ticket by ID"""
        ticket = ticket_factory(test_user)

        result = service.get(db_session, ticket.id)

        assert result is not None
        assert result.id == ticket.id

    def test_get_multi_tickets(self, service, db_session, ticket_factory, test_user):
        """Test getting multiple tickets"""
        ticket1 = ticket_factory(test_user)
        ticket2 = ticket_factory(test_user)

        result = service.get_multi(db_session)

        assert len(result) >= 2

    # ==================== STATUS FILTER TESTS ====================

    def test_get_by_status_open(self, service, db_session, ticket_factory, test_user):
        """Test getting open tickets"""
        open_ticket = ticket_factory(test_user, status=TicketStatus.OPEN)
        closed_ticket = ticket_factory(test_user, status=TicketStatus.CLOSED)

        result = service.get_by_status(db_session, status=TicketStatus.OPEN)

        assert all(t.status == TicketStatus.OPEN for t in result)

    def test_get_by_status_in_progress(self, service, db_session, ticket_factory, test_user):
        """Test getting in-progress tickets"""
        in_progress = ticket_factory(test_user, status=TicketStatus.IN_PROGRESS)

        result = service.get_by_status(db_session, status=TicketStatus.IN_PROGRESS)

        assert all(t.status == TicketStatus.IN_PROGRESS for t in result)

    def test_get_by_status_closed(self, service, db_session, ticket_factory, test_user):
        """Test getting closed tickets"""
        closed = ticket_factory(test_user, status=TicketStatus.CLOSED)

        result = service.get_by_status(db_session, status=TicketStatus.CLOSED)

        assert all(t.status == TicketStatus.CLOSED for t in result)

    # ==================== PRIORITY FILTER TESTS ====================

    def test_get_by_priority_high(self, service, db_session, ticket_factory, test_user):
        """Test getting high priority tickets"""
        high = ticket_factory(test_user, priority=TicketPriority.HIGH)
        low = ticket_factory(test_user, priority=TicketPriority.LOW)

        result = service.get_by_priority(db_session, priority=TicketPriority.HIGH)

        assert all(t.priority == TicketPriority.HIGH for t in result)

    def test_get_by_priority_critical(self, service, db_session, ticket_factory, test_user):
        """Test getting critical priority tickets"""
        critical = ticket_factory(test_user, priority=TicketPriority.CRITICAL)

        result = service.get_by_priority(db_session, priority=TicketPriority.CRITICAL)

        assert all(t.priority == TicketPriority.CRITICAL for t in result)

    # ==================== REQUESTER FILTER TESTS ====================

    def test_get_by_requester(self, service, db_session, ticket_factory, test_user, admin_user):
        """Test getting tickets by requester"""
        user_ticket = ticket_factory(test_user)
        admin_ticket = ticket_factory(admin_user)

        result = service.get_by_requester(db_session, requester_id=test_user.id)

        assert all(t.requester_id == test_user.id for t in result)

    def test_get_by_requester_empty(self, service, db_session, manager_user):
        """Test getting tickets for user with no tickets"""
        result = service.get_by_requester(db_session, requester_id=manager_user.id)

        assert len(result) == 0

    # ==================== ASSIGNMENT TESTS ====================

    def test_assign_ticket(self, service, db_session, ticket_factory, test_user, admin_user):
        """Test assigning ticket to agent"""
        ticket = ticket_factory(test_user, status=TicketStatus.OPEN)

        result = service.assign_ticket(
            db_session,
            ticket_id=ticket.id,
            assignee_id=admin_user.id
        )

        assert result.assignee_id == admin_user.id
        assert result.status == TicketStatus.IN_PROGRESS

    def test_reassign_ticket(self, service, db_session, ticket_factory, test_user, admin_user, manager_user):
        """Test reassigning ticket to different agent"""
        ticket = ticket_factory(test_user, status=TicketStatus.IN_PROGRESS, assignee_id=admin_user.id)

        result = service.assign_ticket(
            db_session,
            ticket_id=ticket.id,
            assignee_id=manager_user.id
        )

        assert result.assignee_id == manager_user.id

    def test_unassign_ticket(self, service, db_session, ticket_factory, test_user, admin_user):
        """Test unassigning ticket"""
        ticket = ticket_factory(test_user, status=TicketStatus.IN_PROGRESS, assignee_id=admin_user.id)

        result = service.unassign_ticket(db_session, ticket_id=ticket.id)

        assert result.assignee_id is None

    # ==================== STATUS UPDATE TESTS ====================

    def test_update_status_to_in_progress(self, service, db_session, ticket_factory, test_user):
        """Test updating ticket status to in-progress"""
        ticket = ticket_factory(test_user, status=TicketStatus.OPEN)

        result = service.update_status(
            db_session,
            ticket_id=ticket.id,
            status=TicketStatus.IN_PROGRESS
        )

        assert result.status == TicketStatus.IN_PROGRESS

    def test_update_status_to_resolved(self, service, db_session, ticket_factory, test_user):
        """Test updating ticket status to resolved"""
        ticket = ticket_factory(test_user, status=TicketStatus.IN_PROGRESS)

        result = service.update_status(
            db_session,
            ticket_id=ticket.id,
            status=TicketStatus.RESOLVED,
            resolution="Issue fixed by clearing cache"
        )

        assert result.status == TicketStatus.RESOLVED

    def test_close_ticket(self, service, db_session, ticket_factory, test_user):
        """Test closing a ticket"""
        ticket = ticket_factory(test_user, status=TicketStatus.RESOLVED)

        result = service.close_ticket(db_session, ticket_id=ticket.id)

        assert result.status == TicketStatus.CLOSED
        assert result.closed_at is not None

    def test_reopen_ticket(self, service, db_session, ticket_factory, test_user):
        """Test reopening a closed ticket"""
        ticket = ticket_factory(test_user, status=TicketStatus.CLOSED)

        result = service.reopen_ticket(
            db_session,
            ticket_id=ticket.id,
            reason="Issue recurred"
        )

        assert result.status == TicketStatus.OPEN

    # ==================== ESCALATION TESTS ====================

    def test_escalate_ticket(self, service, db_session, ticket_factory, test_user):
        """Test escalating ticket priority"""
        ticket = ticket_factory(test_user, priority=TicketPriority.MEDIUM)

        result = service.escalate(
            db_session,
            ticket_id=ticket.id,
            reason="Customer is VIP"
        )

        assert result.priority == TicketPriority.HIGH

    def test_escalate_to_critical(self, service, db_session, ticket_factory, test_user):
        """Test escalating ticket to critical"""
        ticket = ticket_factory(test_user, priority=TicketPriority.HIGH)

        result = service.escalate(
            db_session,
            ticket_id=ticket.id,
            reason="Production system down"
        )

        assert result.priority == TicketPriority.CRITICAL

    # ==================== CATEGORY FILTER TESTS ====================

    def test_get_by_category(self, service, db_session, ticket_factory, test_user):
        """Test getting tickets by category"""
        technical = ticket_factory(test_user, category="technical")
        billing = ticket_factory(test_user, category="billing")

        result = service.get_by_category(db_session, category="technical")

        assert all(t.category == "technical" for t in result)

    # ==================== STATISTICS TESTS ====================

    def test_get_statistics(self, service, db_session, ticket_factory, test_user):
        """Test getting ticket statistics"""
        ticket_factory(test_user, status=TicketStatus.OPEN)
        ticket_factory(test_user, status=TicketStatus.IN_PROGRESS)
        ticket_factory(test_user, status=TicketStatus.CLOSED)

        stats = service.get_statistics(db_session)

        assert "total_tickets" in stats
        assert "open_tickets" in stats
        assert "in_progress_tickets" in stats
        assert "closed_tickets" in stats

    def test_get_statistics_by_priority(self, service, db_session, ticket_factory, test_user):
        """Test getting statistics by priority"""
        ticket_factory(test_user, priority=TicketPriority.HIGH)
        ticket_factory(test_user, priority=TicketPriority.LOW)
        ticket_factory(test_user, priority=TicketPriority.CRITICAL)

        stats = service.get_statistics(db_session)

        assert "priority_breakdown" in stats

    def test_get_average_resolution_time(self, service, db_session, ticket_factory, test_user):
        """Test getting average resolution time"""
        # Create resolved tickets with timing data
        ticket = ticket_factory(test_user, status=TicketStatus.RESOLVED)

        avg_time = service.get_average_resolution_time(db_session)

        # Should return average time in hours or None

    # ==================== SLA TESTS ====================

    def test_get_overdue_tickets(self, service, db_session, ticket_factory, test_user):
        """Test getting overdue tickets"""
        # Create ticket that's past SLA
        overdue = ticket_factory(
            test_user,
            status=TicketStatus.OPEN,
            priority=TicketPriority.HIGH
        )
        # Manually set created_at to past SLA time
        overdue.created_at = datetime.now() - timedelta(hours=5)
        db_session.commit()

        result = service.get_overdue_tickets(db_session, sla_hours=4)

        # Should include overdue ticket

    # ==================== PAGINATION TESTS ====================

    def test_get_multi_pagination(self, service, db_session, ticket_factory, test_user):
        """Test pagination for tickets"""
        for _ in range(5):
            ticket_factory(test_user)

        first_page = service.get_multi(db_session, skip=0, limit=2)
        second_page = service.get_multi(db_session, skip=2, limit=2)

        assert len(first_page) == 2
        assert len(second_page) == 2

    def test_get_by_requester_pagination(self, service, db_session, ticket_factory, test_user):
        """Test pagination for requester tickets"""
        for _ in range(5):
            ticket_factory(test_user)

        first_page = service.get_by_requester(db_session, requester_id=test_user.id, skip=0, limit=2)
        second_page = service.get_by_requester(db_session, requester_id=test_user.id, skip=2, limit=2)

        assert len(first_page) == 2
        assert len(second_page) == 2

    # ==================== ORGANIZATION FILTER TESTS ====================

    def test_get_by_organization(self, service, db_session, ticket_factory, test_user, test_organization, second_organization):
        """Test getting tickets filtered by organization"""
        ticket1 = ticket_factory(test_user, organization_id=test_organization.id)
        ticket2 = ticket_factory(test_user, organization_id=second_organization.id)

        result = service.get_multi(db_session, organization_id=test_organization.id)

        assert all(t.organization_id == test_organization.id for t in result)
