"""
Unit Tests for Additional Operations Services

Tests cover:
- COD Service
- SLA Service
- Dispatch Assignment Service
- Zone Service
- Incident Service
- Feedback Service

Author: BARQ QA Team
Last Updated: 2025-12-10
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

from app.services.operations.cod_service import CODService
from app.services.operations.sla_service import SLAService
from app.services.operations.dispatch_assignment_service import DispatchAssignmentService
from app.services.operations.zone_service import ZoneService
from app.services.operations.incident_service import IncidentService
from app.services.operations.feedback_service import FeedbackService
from app.models.operations.cod import COD, CODStatus
from app.models.operations.incident import Incident, IncidentType, IncidentStatus


# ==================== COD SERVICE TESTS ====================

class TestCODService:
    """Test COD (Cash on Delivery) Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create CODService instance"""
        return CODService(COD)

    def test_create_cod_collection(self, service, db_session, courier_factory, delivery_factory, test_organization):
        """Test creating a COD collection record"""
        from app.schemas.operations.cod import CODCreate

        courier = courier_factory()
        delivery = delivery_factory(courier)

        cod_data = CODCreate(
            delivery_id=delivery.id,
            courier_id=courier.id,
            amount=Decimal("250.00"),
            organization_id=test_organization.id
        )

        cod = service.create(db_session, obj_in=cod_data)

        assert cod is not None
        assert cod.amount == Decimal("250.00")
        assert cod.status == CODStatus.COLLECTED

    def test_get_cod_by_courier(self, service, db_session, courier_factory, cod_factory):
        """Test getting COD collections by courier"""
        courier1 = courier_factory()
        courier2 = courier_factory()
        cod1 = cod_factory(courier1)
        cod2 = cod_factory(courier2)

        result = service.get_by_courier(db_session, courier_id=courier1.id)

        assert all(c.courier_id == courier1.id for c in result)

    def test_get_cod_by_status(self, service, db_session, courier_factory, cod_factory):
        """Test getting COD collections by status"""
        courier = courier_factory()
        collected = cod_factory(courier, status=CODStatus.COLLECTED)
        remitted = cod_factory(courier, status=CODStatus.REMITTED)

        result = service.get_by_status(db_session, status=CODStatus.COLLECTED)

        assert all(c.status == CODStatus.COLLECTED for c in result)

    def test_mark_cod_remitted(self, service, db_session, courier_factory, cod_factory):
        """Test marking COD as remitted"""
        courier = courier_factory()
        cod = cod_factory(courier, status=CODStatus.COLLECTED)

        result = service.mark_remitted(
            db_session,
            cod_id=cod.id,
            remitted_at=datetime.now()
        )

        assert result.status == CODStatus.REMITTED
        assert result.remitted_at is not None

    def test_get_outstanding_cod(self, service, db_session, courier_factory, cod_factory):
        """Test getting outstanding COD amounts"""
        courier = courier_factory()
        cod_factory(courier, status=CODStatus.COLLECTED, amount=Decimal("100.00"))
        cod_factory(courier, status=CODStatus.COLLECTED, amount=Decimal("150.00"))
        cod_factory(courier, status=CODStatus.REMITTED, amount=Decimal("200.00"))

        outstanding = service.get_outstanding(db_session, courier_id=courier.id)

        assert outstanding >= Decimal("250.00")

    def test_get_cod_summary(self, service, db_session, courier_factory, cod_factory):
        """Test getting COD summary"""
        courier = courier_factory()
        cod_factory(courier, status=CODStatus.COLLECTED, amount=Decimal("100.00"))
        cod_factory(courier, status=CODStatus.REMITTED, amount=Decimal("200.00"))

        summary = service.get_summary(
            db_session,
            start_date=date.today() - timedelta(days=7),
            end_date=date.today()
        )

        assert "total_collected" in summary
        assert "total_remitted" in summary
        assert "outstanding" in summary

    def test_bulk_remit_cod(self, service, db_session, courier_factory, cod_factory):
        """Test bulk remitting COD collections"""
        courier = courier_factory()
        cods = [
            cod_factory(courier, status=CODStatus.COLLECTED)
            for _ in range(3)
        ]
        cod_ids = [c.id for c in cods]

        results = service.bulk_remit(db_session, cod_ids=cod_ids)

        assert len(results) == 3
        assert all(r.status == CODStatus.REMITTED for r in results)


# ==================== SLA SERVICE TESTS ====================

class TestSLAService:
    """Test SLA Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create SLAService instance"""
        return SLAService(db_session)

    def test_check_delivery_sla(self, service, db_session, delivery_factory, courier_factory):
        """Test checking delivery SLA compliance"""
        courier = courier_factory()
        delivery = delivery_factory(courier)

        result = service.check_sla(delivery_id=delivery.id)

        assert "is_within_sla" in result
        assert "time_remaining" in result

    def test_get_sla_violations(self, service, db_session, delivery_factory, courier_factory):
        """Test getting SLA violations"""
        courier = courier_factory()
        # Create delivery that violated SLA
        delivery = delivery_factory(courier, status="pending")
        # Set created_at to past SLA window
        delivery.created_at = datetime.now() - timedelta(hours=5)
        db_session.commit()

        violations = service.get_violations(
            start_date=date.today() - timedelta(days=7),
            end_date=date.today()
        )

        assert isinstance(violations, list)

    def test_get_sla_compliance_rate(self, service, db_session):
        """Test getting SLA compliance rate"""
        result = service.get_compliance_rate(
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        assert "compliance_rate" in result
        assert "total_deliveries" in result
        assert "within_sla" in result

    def test_get_sla_by_priority(self, service, db_session):
        """Test getting SLA metrics by priority"""
        result = service.get_by_priority()

        assert "high_priority_compliance" in result
        assert "standard_compliance" in result

    def test_escalate_sla_breach(self, service, db_session, delivery_factory, courier_factory):
        """Test escalating SLA breach"""
        courier = courier_factory()
        delivery = delivery_factory(courier)

        result = service.escalate_breach(
            delivery_id=delivery.id,
            reason="SLA exceeded by 2 hours"
        )

        assert result is not None


# ==================== DISPATCH ASSIGNMENT SERVICE TESTS ====================

class TestDispatchAssignmentService:
    """Test Dispatch Assignment Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create DispatchAssignmentService instance"""
        return DispatchAssignmentService(db_session)

    def test_assign_delivery_to_courier(self, service, db_session, delivery_factory, courier_factory):
        """Test assigning delivery to courier"""
        courier = courier_factory()
        delivery = delivery_factory(courier=None, status="pending")

        result = service.assign(
            delivery_id=delivery.id,
            courier_id=courier.id
        )

        assert result.courier_id == courier.id

    def test_auto_assign_delivery(self, service, db_session, delivery_factory, courier_factory):
        """Test auto-assigning delivery to best courier"""
        courier1 = courier_factory(city="Riyadh")
        courier2 = courier_factory(city="Riyadh")
        delivery = delivery_factory(courier=None, pickup_address="Riyadh")

        result = service.auto_assign(delivery_id=delivery.id)

        assert result.courier_id is not None

    def test_reassign_delivery(self, service, db_session, delivery_factory, courier_factory):
        """Test reassigning delivery to different courier"""
        courier1 = courier_factory()
        courier2 = courier_factory()
        delivery = delivery_factory(courier1)

        result = service.reassign(
            delivery_id=delivery.id,
            new_courier_id=courier2.id,
            reason="Original courier unavailable"
        )

        assert result.courier_id == courier2.id

    def test_get_available_couriers(self, service, db_session, courier_factory):
        """Test getting available couriers for dispatch"""
        courier1 = courier_factory(status="active")
        courier2 = courier_factory(status="on_leave")

        result = service.get_available_couriers()

        assert all(c.status == "active" for c in result)

    def test_get_assignment_history(self, service, db_session, delivery_factory, courier_factory):
        """Test getting assignment history for delivery"""
        courier = courier_factory()
        delivery = delivery_factory(courier)

        history = service.get_assignment_history(delivery_id=delivery.id)

        assert isinstance(history, list)


# ==================== ZONE SERVICE TESTS ====================

class TestZoneService:
    """Test Zone Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create ZoneService instance"""
        return ZoneService(db_session)

    def test_create_zone(self, service, db_session, test_organization):
        """Test creating a delivery zone"""
        from app.schemas.operations.zone import ZoneCreate

        zone_data = ZoneCreate(
            name="Riyadh North",
            city="Riyadh",
            coordinates=[
                {"lat": 24.7, "lng": 46.7},
                {"lat": 24.8, "lng": 46.7},
                {"lat": 24.8, "lng": 46.8},
                {"lat": 24.7, "lng": 46.8}
            ],
            organization_id=test_organization.id
        )

        zone = service.create(db_session, obj_in=zone_data)

        assert zone is not None
        assert zone.name == "Riyadh North"

    def test_get_zones_by_city(self, service, db_session, test_organization):
        """Test getting zones by city"""
        from app.models.operations.zone import Zone

        zone1 = Zone(name="Zone 1", city="Riyadh", organization_id=test_organization.id)
        zone2 = Zone(name="Zone 2", city="Jeddah", organization_id=test_organization.id)
        db_session.add_all([zone1, zone2])
        db_session.commit()

        result = service.get_by_city(db_session, city="Riyadh")

        assert all(z.city == "Riyadh" for z in result)

    def test_find_zone_by_coordinates(self, service, db_session, test_organization):
        """Test finding zone by coordinates"""
        result = service.find_zone_by_coordinates(
            db_session,
            lat=24.75,
            lng=46.75
        )

        # Should return matching zone or None

    def test_get_active_zones(self, service, db_session, test_organization):
        """Test getting active zones"""
        from app.models.operations.zone import Zone

        active = Zone(name="Active Zone", city="Riyadh", is_active=True, organization_id=test_organization.id)
        inactive = Zone(name="Inactive Zone", city="Riyadh", is_active=False, organization_id=test_organization.id)
        db_session.add_all([active, inactive])
        db_session.commit()

        result = service.get_active(db_session)

        assert all(z.is_active is True for z in result)


# ==================== INCIDENT SERVICE TESTS ====================

class TestIncidentService:
    """Test Incident Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create IncidentService instance"""
        return IncidentService(Incident)

    def test_create_incident(self, service, db_session, courier_factory, test_organization):
        """Test creating an incident report"""
        from app.schemas.operations.incident import IncidentCreate

        courier = courier_factory()
        incident_data = IncidentCreate(
            title="Minor Accident",
            description="Vehicle scratched",
            incident_type=IncidentType.ACCIDENT,
            courier_id=courier.id,
            organization_id=test_organization.id
        )

        incident = service.create(db_session, obj_in=incident_data)

        assert incident is not None
        assert incident.title == "Minor Accident"
        assert incident.status == IncidentStatus.REPORTED

    def test_get_incidents_by_courier(self, service, db_session, courier_factory, test_organization):
        """Test getting incidents by courier"""
        courier = courier_factory()
        incident = Incident(
            title="Test Incident",
            courier_id=courier.id,
            incident_type=IncidentType.ACCIDENT,
            status=IncidentStatus.REPORTED,
            organization_id=test_organization.id
        )
        db_session.add(incident)
        db_session.commit()

        result = service.get_by_courier(db_session, courier_id=courier.id)

        assert all(i.courier_id == courier.id for i in result)

    def test_get_incidents_by_type(self, service, db_session, courier_factory, test_organization):
        """Test getting incidents by type"""
        courier = courier_factory()
        accident = Incident(
            title="Accident",
            courier_id=courier.id,
            incident_type=IncidentType.ACCIDENT,
            organization_id=test_organization.id
        )
        theft = Incident(
            title="Theft",
            courier_id=courier.id,
            incident_type=IncidentType.THEFT,
            organization_id=test_organization.id
        )
        db_session.add_all([accident, theft])
        db_session.commit()

        result = service.get_by_type(db_session, incident_type=IncidentType.ACCIDENT)

        assert all(i.incident_type == IncidentType.ACCIDENT for i in result)

    def test_update_incident_status(self, service, db_session, courier_factory, test_organization):
        """Test updating incident status"""
        courier = courier_factory()
        incident = Incident(
            title="Test Incident",
            courier_id=courier.id,
            incident_type=IncidentType.ACCIDENT,
            status=IncidentStatus.REPORTED,
            organization_id=test_organization.id
        )
        db_session.add(incident)
        db_session.commit()

        result = service.update_status(
            db_session,
            incident_id=incident.id,
            status=IncidentStatus.INVESTIGATING
        )

        assert result.status == IncidentStatus.INVESTIGATING

    def test_resolve_incident(self, service, db_session, courier_factory, test_organization):
        """Test resolving an incident"""
        courier = courier_factory()
        incident = Incident(
            title="Test Incident",
            courier_id=courier.id,
            incident_type=IncidentType.ACCIDENT,
            status=IncidentStatus.INVESTIGATING,
            organization_id=test_organization.id
        )
        db_session.add(incident)
        db_session.commit()

        result = service.resolve(
            db_session,
            incident_id=incident.id,
            resolution="Issue resolved"
        )

        assert result.status == IncidentStatus.RESOLVED

    def test_get_incident_statistics(self, service, db_session, courier_factory, test_organization):
        """Test getting incident statistics"""
        courier = courier_factory()
        for i in range(3):
            incident = Incident(
                title=f"Incident {i}",
                courier_id=courier.id,
                incident_type=IncidentType.ACCIDENT,
                organization_id=test_organization.id
            )
            db_session.add(incident)
        db_session.commit()

        stats = service.get_statistics(db_session)

        assert "total_incidents" in stats
        assert "by_type" in stats
        assert "by_status" in stats


# ==================== FEEDBACK SERVICE TESTS ====================

class TestFeedbackService:
    """Test Feedback Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create FeedbackService instance"""
        return FeedbackService(db_session)

    def test_create_feedback(self, service, db_session, delivery_factory, courier_factory, test_organization):
        """Test creating delivery feedback"""
        from app.schemas.operations.feedback import FeedbackCreate

        courier = courier_factory()
        delivery = delivery_factory(courier)

        feedback_data = FeedbackCreate(
            delivery_id=delivery.id,
            rating=5,
            comment="Excellent service!",
            organization_id=test_organization.id
        )

        feedback = service.create(db_session, obj_in=feedback_data)

        assert feedback is not None
        assert feedback.rating == 5

    def test_get_feedback_by_courier(self, service, db_session, courier_factory):
        """Test getting feedback for courier"""
        courier = courier_factory()

        result = service.get_by_courier(db_session, courier_id=courier.id)

        assert isinstance(result, list)

    def test_get_average_rating(self, service, db_session, courier_factory):
        """Test getting average rating for courier"""
        courier = courier_factory()

        avg = service.get_average_rating(db_session, courier_id=courier.id)

        assert avg is None or 1 <= avg <= 5

    def test_get_feedback_summary(self, service, db_session):
        """Test getting feedback summary"""
        summary = service.get_summary(
            db_session,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        assert "average_rating" in summary
        assert "total_feedbacks" in summary
        assert "rating_distribution" in summary
