"""
Unit Tests for Route Service

Tests cover:
- Route CRUD operations
- Route optimization
- Status management
- Statistics

Author: BARQ QA Team
Last Updated: 2025-12-10
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

from app.services.operations.route_service import RouteService
from app.models.operations.route import Route, RouteStatus


class TestRouteService:
    """Test Route Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create RouteService instance"""
        return RouteService(Route)

    # ==================== CRUD TESTS ====================

    def test_create_route(self, service, db_session, courier_factory, test_organization):
        """Test creating a route"""
        from app.schemas.operations.route import RouteCreate

        courier = courier_factory()
        route_data = RouteCreate(
            name="Morning Route A",
            courier_id=courier.id,
            start_location="Warehouse A",
            end_location="Distribution Center B",
            estimated_duration=120,
            organization_id=test_organization.id
        )

        route = service.create(db_session, obj_in=route_data)

        assert route is not None
        assert route.name == "Morning Route A"
        assert route.status == RouteStatus.PLANNED

    def test_get_route_by_id(self, service, db_session, courier_factory):
        """Test getting route by ID"""
        courier = courier_factory()
        route = Route(
            name="Test Route",
            courier_id=courier.id,
            start_location="A",
            end_location="B",
            status=RouteStatus.PLANNED
        )
        db_session.add(route)
        db_session.commit()

        result = service.get(db_session, route.id)

        assert result is not None
        assert result.id == route.id

    def test_get_multi_routes(self, service, db_session, courier_factory):
        """Test getting multiple routes"""
        courier = courier_factory()
        for i in range(3):
            route = Route(
                name=f"Route {i}",
                courier_id=courier.id,
                start_location="A",
                end_location="B",
                status=RouteStatus.PLANNED
            )
            db_session.add(route)
        db_session.commit()

        result = service.get_multi(db_session)

        assert len(result) >= 3

    # ==================== COURIER FILTER TESTS ====================

    def test_get_by_courier(self, service, db_session, courier_factory):
        """Test getting routes by courier"""
        courier1 = courier_factory()
        courier2 = courier_factory()

        route1 = Route(name="Route 1", courier_id=courier1.id, status=RouteStatus.PLANNED)
        route2 = Route(name="Route 2", courier_id=courier1.id, status=RouteStatus.PLANNED)
        route3 = Route(name="Route 3", courier_id=courier2.id, status=RouteStatus.PLANNED)
        db_session.add_all([route1, route2, route3])
        db_session.commit()

        result = service.get_by_courier(db_session, courier_id=courier1.id)

        assert len(result) >= 2
        assert all(r.courier_id == courier1.id for r in result)

    def test_get_by_courier_empty(self, service, db_session, courier_factory):
        """Test getting routes for courier with no routes"""
        courier = courier_factory()

        result = service.get_by_courier(db_session, courier_id=courier.id)

        assert len(result) == 0

    # ==================== STATUS FILTER TESTS ====================

    def test_get_by_status_planned(self, service, db_session, courier_factory):
        """Test getting planned routes"""
        courier = courier_factory()
        route = Route(name="Planned Route", courier_id=courier.id, status=RouteStatus.PLANNED)
        db_session.add(route)
        db_session.commit()

        result = service.get_by_status(db_session, status=RouteStatus.PLANNED)

        assert len(result) >= 1
        assert all(r.status == RouteStatus.PLANNED for r in result)

    def test_get_by_status_in_progress(self, service, db_session, courier_factory):
        """Test getting in-progress routes"""
        courier = courier_factory()
        route = Route(name="Active Route", courier_id=courier.id, status=RouteStatus.IN_PROGRESS)
        db_session.add(route)
        db_session.commit()

        result = service.get_by_status(db_session, status=RouteStatus.IN_PROGRESS)

        assert len(result) >= 1
        assert all(r.status == RouteStatus.IN_PROGRESS for r in result)

    def test_get_by_status_completed(self, service, db_session, courier_factory):
        """Test getting completed routes"""
        courier = courier_factory()
        route = Route(name="Completed Route", courier_id=courier.id, status=RouteStatus.COMPLETED)
        db_session.add(route)
        db_session.commit()

        result = service.get_by_status(db_session, status=RouteStatus.COMPLETED)

        assert len(result) >= 1
        assert all(r.status == RouteStatus.COMPLETED for r in result)

    # ==================== STATUS UPDATE TESTS ====================

    def test_start_route(self, service, db_session, courier_factory):
        """Test starting a route"""
        courier = courier_factory()
        route = Route(name="Route to Start", courier_id=courier.id, status=RouteStatus.PLANNED)
        db_session.add(route)
        db_session.commit()

        result = service.start_route(db_session, route_id=route.id)

        assert result is not None
        assert result.status == RouteStatus.IN_PROGRESS
        assert result.started_at is not None

    def test_complete_route(self, service, db_session, courier_factory):
        """Test completing a route"""
        courier = courier_factory()
        route = Route(
            name="Route to Complete",
            courier_id=courier.id,
            status=RouteStatus.IN_PROGRESS,
            started_at=datetime.now()
        )
        db_session.add(route)
        db_session.commit()

        result = service.complete_route(db_session, route_id=route.id)

        assert result is not None
        assert result.status == RouteStatus.COMPLETED
        assert result.completed_at is not None

    def test_cancel_route(self, service, db_session, courier_factory):
        """Test cancelling a route"""
        courier = courier_factory()
        route = Route(name="Route to Cancel", courier_id=courier.id, status=RouteStatus.PLANNED)
        db_session.add(route)
        db_session.commit()

        result = service.cancel_route(db_session, route_id=route.id, reason="Weather conditions")

        assert result is not None
        assert result.status == RouteStatus.CANCELLED

    # ==================== DATE RANGE QUERIES ====================

    def test_get_by_date_range(self, service, db_session, courier_factory):
        """Test getting routes by date range"""
        courier = courier_factory()
        route = Route(
            name="Today's Route",
            courier_id=courier.id,
            status=RouteStatus.PLANNED,
            scheduled_date=date.today()
        )
        db_session.add(route)
        db_session.commit()

        result = service.get_by_date_range(
            db_session,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=1)
        )

        assert len(result) >= 1

    def test_get_todays_routes(self, service, db_session, courier_factory):
        """Test getting today's routes"""
        courier = courier_factory()
        today_route = Route(
            name="Today Route",
            courier_id=courier.id,
            status=RouteStatus.PLANNED,
            scheduled_date=date.today()
        )
        tomorrow_route = Route(
            name="Tomorrow Route",
            courier_id=courier.id,
            status=RouteStatus.PLANNED,
            scheduled_date=date.today() + timedelta(days=1)
        )
        db_session.add_all([today_route, tomorrow_route])
        db_session.commit()

        result = service.get_todays_routes(db_session)

        route_names = [r.name for r in result]
        assert "Today Route" in route_names

    # ==================== ROUTE OPTIMIZATION TESTS ====================

    def test_add_stop_to_route(self, service, db_session, courier_factory):
        """Test adding a stop to route"""
        courier = courier_factory()
        route = Route(name="Route with Stops", courier_id=courier.id, status=RouteStatus.PLANNED)
        db_session.add(route)
        db_session.commit()

        result = service.add_stop(
            db_session,
            route_id=route.id,
            address="123 Test St",
            sequence=1
        )

        assert result is not None

    def test_reorder_stops(self, service, db_session, courier_factory):
        """Test reordering route stops"""
        courier = courier_factory()
        route = Route(name="Route to Reorder", courier_id=courier.id, status=RouteStatus.PLANNED)
        db_session.add(route)
        db_session.commit()

        # Add stops
        service.add_stop(db_session, route_id=route.id, address="Stop A", sequence=1)
        service.add_stop(db_session, route_id=route.id, address="Stop B", sequence=2)
        service.add_stop(db_session, route_id=route.id, address="Stop C", sequence=3)

        # Reorder
        new_order = [3, 1, 2]  # C, A, B
        result = service.reorder_stops(db_session, route_id=route.id, new_order=new_order)

        assert result is not None

    def test_optimize_route(self, service, db_session, courier_factory):
        """Test route optimization"""
        courier = courier_factory()
        route = Route(name="Route to Optimize", courier_id=courier.id, status=RouteStatus.PLANNED)
        db_session.add(route)
        db_session.commit()

        result = service.optimize_route(db_session, route_id=route.id)

        assert result is not None
        # Optimization should return optimized stop order

    # ==================== STATISTICS TESTS ====================

    def test_get_statistics(self, service, db_session, courier_factory):
        """Test getting route statistics"""
        courier = courier_factory()
        Route(name="R1", courier_id=courier.id, status=RouteStatus.PLANNED)
        Route(name="R2", courier_id=courier.id, status=RouteStatus.IN_PROGRESS)
        Route(name="R3", courier_id=courier.id, status=RouteStatus.COMPLETED)
        for r in [Route(name=f"R{i}", courier_id=courier.id, status=RouteStatus.PLANNED) for i in range(4, 7)]:
            db_session.add(r)
        db_session.commit()

        stats = service.get_statistics(db_session)

        assert "total_routes" in stats
        assert "planned" in stats
        assert "in_progress" in stats
        assert "completed" in stats

    def test_get_courier_route_performance(self, service, db_session, courier_factory):
        """Test getting courier route performance"""
        courier = courier_factory()
        # Create completed routes with timing data
        route = Route(
            name="Completed Route",
            courier_id=courier.id,
            status=RouteStatus.COMPLETED,
            estimated_duration=120,
            actual_duration=110
        )
        db_session.add(route)
        db_session.commit()

        performance = service.get_courier_performance(db_session, courier_id=courier.id)

        assert "total_routes" in performance
        assert "avg_completion_time" in performance
        assert "on_time_rate" in performance

    # ==================== PAGINATION TESTS ====================

    def test_get_multi_pagination(self, service, db_session, courier_factory):
        """Test pagination for routes"""
        courier = courier_factory()
        for i in range(5):
            route = Route(name=f"Route {i}", courier_id=courier.id, status=RouteStatus.PLANNED)
            db_session.add(route)
        db_session.commit()

        first_page = service.get_multi(db_session, skip=0, limit=2)
        second_page = service.get_multi(db_session, skip=2, limit=2)

        assert len(first_page) == 2
        assert len(second_page) == 2

    def test_get_by_courier_pagination(self, service, db_session, courier_factory):
        """Test pagination for courier routes"""
        courier = courier_factory()
        for i in range(5):
            route = Route(name=f"Route {i}", courier_id=courier.id, status=RouteStatus.PLANNED)
            db_session.add(route)
        db_session.commit()

        first_page = service.get_by_courier(db_session, courier_id=courier.id, skip=0, limit=2)
        second_page = service.get_by_courier(db_session, courier_id=courier.id, skip=2, limit=2)

        assert len(first_page) == 2
        assert len(second_page) == 2

    # ==================== ORGANIZATION FILTER TESTS ====================

    def test_get_by_organization(self, service, db_session, courier_factory, test_organization, second_organization):
        """Test getting routes filtered by organization"""
        courier1 = courier_factory(organization_id=test_organization.id)
        courier2 = courier_factory(organization_id=second_organization.id)

        route1 = Route(name="Org1 Route", courier_id=courier1.id, organization_id=test_organization.id)
        route2 = Route(name="Org2 Route", courier_id=courier2.id, organization_id=second_organization.id)
        db_session.add_all([route1, route2])
        db_session.commit()

        result = service.get_multi(db_session, organization_id=test_organization.id)

        assert all(r.organization_id == test_organization.id for r in result)
