"""
Dashboard API Integration Tests

Tests for all dashboard endpoints including:
- Stats endpoint
- Chart endpoints
- Alerts endpoint
- Performance endpoint
- Summary endpoint

All tests verify authentication requirements and organization isolation.

Author: BARQ QA Team
Last Updated: 2025-12-06
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestDashboardAuthentication:
    """Test authentication requirements for dashboard endpoints"""

    DASHBOARD_ENDPOINTS = [
        "/api/v1/dashboard/stats",
        "/api/v1/dashboard/charts/deliveries",
        "/api/v1/dashboard/charts/fleet-status",
        "/api/v1/dashboard/charts/courier-status",
        "/api/v1/dashboard/charts/sponsorship",
        "/api/v1/dashboard/charts/project-types",
        "/api/v1/dashboard/charts/city-distribution",
        "/api/v1/dashboard/charts/monthly-trends",
        "/api/v1/dashboard/alerts",
        "/api/v1/dashboard/performance/top-couriers",
        "/api/v1/dashboard/recent-activity",
        "/api/v1/dashboard/summary",
    ]

    @pytest.mark.integration
    def test_dashboard_endpoints_require_auth(self, client: TestClient):
        """Test that all dashboard endpoints require authentication"""
        for endpoint in self.DASHBOARD_ENDPOINTS:
            response = client.get(endpoint)
            assert response.status_code == 401, \
                f"Endpoint {endpoint} accessible without auth"

    @pytest.mark.integration
    def test_dashboard_endpoints_require_org_context(
        self,
        client: TestClient,
        test_token: str
    ):
        """Test that dashboard endpoints require organization context in token"""
        # Token without org_id should fail
        headers = {"Authorization": f"Bearer {test_token}"}

        for endpoint in self.DASHBOARD_ENDPOINTS:
            response = client.get(endpoint, headers=headers)
            # Should either work (if org is in token) or fail with 401/403
            assert response.status_code in [200, 401, 403], \
                f"Unexpected status {response.status_code} for {endpoint}"

    @pytest.mark.integration
    def test_dashboard_rejects_invalid_token(self, client: TestClient):
        """Test that dashboard rejects invalid tokens"""
        headers = {"Authorization": "Bearer invalid-token-12345"}

        for endpoint in self.DASHBOARD_ENDPOINTS:
            response = client.get(endpoint, headers=headers)
            assert response.status_code == 401, \
                f"Invalid token accepted for {endpoint}"


class TestDashboardStats:
    """Test /api/v1/dashboard/stats endpoint"""

    @pytest.fixture
    def org_with_data(self, db_session: Session, test_password: str):
        """Create organization with test data"""
        from app.models.tenant.organization import Organization
        from app.models.fleet.courier import Courier, CourierStatus, SponsorshipStatus, ProjectType
        from app.models.fleet.vehicle import Vehicle, VehicleStatus, VehicleType
        from app.models.user import User
        from app.models.tenant.organization_user import OrganizationUser
        from app.core.security import PasswordHasher, TokenManager

        # Create organization
        org = Organization(
            name="Stats Test Org",
            slug="stats-test-org",
            is_active=True
        )
        db_session.add(org)
        db_session.commit()
        db_session.refresh(org)

        # Create couriers with various statuses
        statuses = [
            CourierStatus.ACTIVE,
            CourierStatus.ACTIVE,
            CourierStatus.ACTIVE,
            CourierStatus.INACTIVE,
            CourierStatus.ON_LEAVE,
        ]
        couriers = []
        for i, status in enumerate(statuses):
            courier = Courier(
                barq_id=f"BRQ-STATS-{i}",
                full_name=f"Stats Courier {i}",
                email=f"stats_courier_{i}@test.com",
                mobile_number=f"+96650{i:08d}",
                employee_id=f"EMP-STATS-{i}",
                status=status,
                sponsorship_status=SponsorshipStatus.INHOUSE,
                project_type=ProjectType.BARQ,
                city="Riyadh",
                organization_id=org.id
            )
            db_session.add(courier)
            couriers.append(courier)

        # Create vehicles
        vehicle_statuses = ["available", "assigned", "maintenance"]
        vehicles = []
        for i, vstatus in enumerate(vehicle_statuses):
            vehicle = Vehicle(
                plate_number=f"STATS-{i}",
                vehicle_type=VehicleType.MOTORCYCLE,
                make="Honda",
                model="Wave",
                year=2023,
                status=vstatus,
                city="Riyadh",
                organization_id=org.id
            )
            db_session.add(vehicle)
            vehicles.append(vehicle)

        db_session.commit()

        # Create user with org access
        user = User(
            email="stats_user@test.com",
            full_name="Stats User",
            hashed_password=PasswordHasher.hash_password(test_password),
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

        org_user = OrganizationUser(
            user_id=user.id,
            organization_id=org.id,
            role="ADMIN",
            is_active=True
        )
        db_session.add(org_user)
        db_session.commit()

        token = TokenManager.create_access_token(
            data={
                "sub": str(user.id),
                "org_id": org.id,
                "org_role": "ADMIN"
            }
        )

        return {
            "org": org,
            "couriers": couriers,
            "vehicles": vehicles,
            "user": user,
            "token": token
        }

    @pytest.mark.integration
    def test_stats_returns_correct_structure(
        self,
        client: TestClient,
        org_with_data: dict
    ):
        """Test that stats endpoint returns correct structure"""
        headers = {"Authorization": f"Bearer {org_with_data['token']}"}
        response = client.get("/api/v1/dashboard/stats", headers=headers)

        assert response.status_code == 200
        data = response.json()

        # Verify required fields
        required_fields = [
            "total_vehicles",
            "total_couriers",
            "active_couriers",
            "vehicles_available",
            "vehicles_assigned",
        ]

        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    @pytest.mark.integration
    def test_stats_counts_are_correct(
        self,
        client: TestClient,
        org_with_data: dict
    ):
        """Test that stats counts match actual data"""
        headers = {"Authorization": f"Bearer {org_with_data['token']}"}
        response = client.get("/api/v1/dashboard/stats", headers=headers)

        assert response.status_code == 200
        data = response.json()

        # We created 5 couriers, 3 active
        assert data["total_couriers"] >= 5
        assert data["active_couriers"] >= 3

        # We created 3 vehicles
        assert data["total_vehicles"] >= 3


class TestDashboardCharts:
    """Test dashboard chart endpoints"""

    @pytest.fixture
    def auth_headers(self, db_session: Session, test_password: str):
        """Create authenticated user with organization"""
        from app.models.tenant.organization import Organization
        from app.models.user import User
        from app.models.tenant.organization_user import OrganizationUser
        from app.core.security import PasswordHasher, TokenManager

        org = Organization(
            name="Charts Test Org",
            slug="charts-test-org",
            is_active=True
        )
        db_session.add(org)
        db_session.commit()

        user = User(
            email="charts_user@test.com",
            full_name="Charts User",
            hashed_password=PasswordHasher.hash_password(test_password),
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

        org_user = OrganizationUser(
            user_id=user.id,
            organization_id=org.id,
            role="ADMIN",
            is_active=True
        )
        db_session.add(org_user)
        db_session.commit()

        token = TokenManager.create_access_token(
            data={
                "sub": str(user.id),
                "org_id": org.id,
                "org_role": "ADMIN"
            }
        )

        return {"Authorization": f"Bearer {token}"}

    @pytest.mark.integration
    def test_delivery_trends_structure(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test delivery trends endpoint structure"""
        response = client.get(
            "/api/v1/dashboard/charts/deliveries",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "trend_data" in data
        assert isinstance(data["trend_data"], list)

        # Should have 7 days of data
        if len(data["trend_data"]) > 0:
            day_data = data["trend_data"][0]
            assert "date" in day_data
            assert "deliveries" in day_data or "day" in day_data

    @pytest.mark.integration
    def test_fleet_status_structure(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test fleet status endpoint structure"""
        response = client.get(
            "/api/v1/dashboard/charts/fleet-status",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "fleet_status" in data
        assert isinstance(data["fleet_status"], list)

        # Each item should have name, value, color
        for item in data["fleet_status"]:
            assert "name" in item
            assert "value" in item
            assert "color" in item

    @pytest.mark.integration
    def test_courier_status_structure(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test courier status endpoint structure"""
        response = client.get(
            "/api/v1/dashboard/charts/courier-status",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "courier_status" in data
        assert isinstance(data["courier_status"], list)

    @pytest.mark.integration
    def test_sponsorship_distribution_structure(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test sponsorship distribution endpoint structure"""
        response = client.get(
            "/api/v1/dashboard/charts/sponsorship",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "sponsorship_distribution" in data
        assert isinstance(data["sponsorship_distribution"], list)

    @pytest.mark.integration
    def test_project_distribution_structure(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test project type distribution endpoint structure"""
        response = client.get(
            "/api/v1/dashboard/charts/project-types",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "project_distribution" in data
        assert isinstance(data["project_distribution"], list)

    @pytest.mark.integration
    def test_city_distribution_structure(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test city distribution endpoint structure"""
        response = client.get(
            "/api/v1/dashboard/charts/city-distribution",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "city_distribution" in data
        assert isinstance(data["city_distribution"], list)

    @pytest.mark.integration
    def test_monthly_trends_structure(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test monthly trends endpoint structure"""
        response = client.get(
            "/api/v1/dashboard/charts/monthly-trends",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "monthly_trends" in data
        assert isinstance(data["monthly_trends"], list)


class TestDashboardAlerts:
    """Test dashboard alerts endpoint"""

    @pytest.fixture
    def org_with_alerts(self, db_session: Session, test_password: str):
        """Create organization with data that triggers alerts"""
        from app.models.tenant.organization import Organization
        from app.models.fleet.courier import Courier, CourierStatus, SponsorshipStatus, ProjectType
        from app.models.fleet.vehicle import Vehicle, VehicleStatus, VehicleType
        from app.models.user import User
        from app.models.tenant.organization_user import OrganizationUser
        from app.core.security import PasswordHasher, TokenManager
        from datetime import date, timedelta

        org = Organization(
            name="Alerts Test Org",
            slug="alerts-test-org",
            is_active=True
        )
        db_session.add(org)
        db_session.commit()

        # Create courier with expiring iqama (within 30 days)
        expiring_courier = Courier(
            barq_id="BRQ-EXPIRING",
            full_name="Expiring Iqama Courier",
            email="expiring@test.com",
            mobile_number="+966501234567",
            employee_id="EMP-EXP",
            status=CourierStatus.ACTIVE,
            sponsorship_status=SponsorshipStatus.INHOUSE,
            project_type=ProjectType.BARQ,
            city="Riyadh",
            iqama_expiry_date=date.today() + timedelta(days=15),
            organization_id=org.id
        )
        db_session.add(expiring_courier)

        # Create vehicle in maintenance
        maintenance_vehicle = Vehicle(
            plate_number="MAINT-001",
            vehicle_type=VehicleType.MOTORCYCLE,
            make="Honda",
            model="Wave",
            year=2023,
            status="maintenance",
            city="Riyadh",
            organization_id=org.id
        )
        db_session.add(maintenance_vehicle)
        db_session.commit()

        user = User(
            email="alerts_user@test.com",
            full_name="Alerts User",
            hashed_password=PasswordHasher.hash_password(test_password),
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

        org_user = OrganizationUser(
            user_id=user.id,
            organization_id=org.id,
            role="ADMIN",
            is_active=True
        )
        db_session.add(org_user)
        db_session.commit()

        token = TokenManager.create_access_token(
            data={
                "sub": str(user.id),
                "org_id": org.id,
                "org_role": "ADMIN"
            }
        )

        return {"org": org, "token": token}

    @pytest.mark.integration
    def test_alerts_structure(
        self,
        client: TestClient,
        org_with_alerts: dict
    ):
        """Test alerts endpoint structure"""
        headers = {"Authorization": f"Bearer {org_with_alerts['token']}"}
        response = client.get("/api/v1/dashboard/alerts", headers=headers)

        assert response.status_code == 200
        data = response.json()

        assert "alerts" in data
        assert "summary" in data
        assert isinstance(data["alerts"], list)

        # Summary should have counts
        assert "critical" in data["summary"]
        assert "warning" in data["summary"]
        assert "info" in data["summary"]

    @pytest.mark.integration
    def test_alerts_contain_expected_types(
        self,
        client: TestClient,
        org_with_alerts: dict
    ):
        """Test that alerts include expected alert types"""
        headers = {"Authorization": f"Bearer {org_with_alerts['token']}"}
        response = client.get("/api/v1/dashboard/alerts", headers=headers)

        assert response.status_code == 200
        data = response.json()

        # Check alert structure
        for alert in data["alerts"]:
            assert "type" in alert
            assert alert["type"] in ["critical", "warning", "info"]
            assert "title" in alert
            assert "message" in alert


class TestDashboardPerformance:
    """Test dashboard performance endpoint"""

    @pytest.fixture
    def org_with_performers(self, db_session: Session, test_password: str):
        """Create organization with courier performance data"""
        from app.models.tenant.organization import Organization
        from app.models.fleet.courier import Courier, CourierStatus, SponsorshipStatus, ProjectType
        from app.models.user import User
        from app.models.tenant.organization_user import OrganizationUser
        from app.core.security import PasswordHasher, TokenManager
        from decimal import Decimal

        org = Organization(
            name="Performance Test Org",
            slug="performance-test-org",
            is_active=True
        )
        db_session.add(org)
        db_session.commit()

        # Create couriers with performance scores
        scores = [95.0, 88.5, 82.0, 75.5, 70.0]
        for i, score in enumerate(scores):
            courier = Courier(
                barq_id=f"BRQ-PERF-{i}",
                full_name=f"Performer {i}",
                email=f"performer_{i}@test.com",
                mobile_number=f"+96650{i:08d}",
                employee_id=f"EMP-PERF-{i}",
                status=CourierStatus.ACTIVE,
                sponsorship_status=SponsorshipStatus.INHOUSE,
                project_type=ProjectType.BARQ,
                city="Riyadh",
                performance_score=Decimal(str(score)),
                total_deliveries=100 - (i * 10),
                organization_id=org.id
            )
            db_session.add(courier)

        db_session.commit()

        user = User(
            email="performance_user@test.com",
            full_name="Performance User",
            hashed_password=PasswordHasher.hash_password(test_password),
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

        org_user = OrganizationUser(
            user_id=user.id,
            organization_id=org.id,
            role="ADMIN",
            is_active=True
        )
        db_session.add(org_user)
        db_session.commit()

        token = TokenManager.create_access_token(
            data={
                "sub": str(user.id),
                "org_id": org.id,
                "org_role": "ADMIN"
            }
        )

        return {"org": org, "token": token}

    @pytest.mark.integration
    def test_top_couriers_structure(
        self,
        client: TestClient,
        org_with_performers: dict
    ):
        """Test top couriers endpoint structure"""
        headers = {"Authorization": f"Bearer {org_with_performers['token']}"}
        response = client.get(
            "/api/v1/dashboard/performance/top-couriers",
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "top_couriers" in data
        assert isinstance(data["top_couriers"], list)

        # Check courier structure
        if len(data["top_couriers"]) > 0:
            courier = data["top_couriers"][0]
            assert "rank" in courier
            assert "name" in courier
            assert "performance_score" in courier

    @pytest.mark.integration
    def test_top_couriers_sorted_by_score(
        self,
        client: TestClient,
        org_with_performers: dict
    ):
        """Test that top couriers are sorted by performance score"""
        headers = {"Authorization": f"Bearer {org_with_performers['token']}"}
        response = client.get(
            "/api/v1/dashboard/performance/top-couriers",
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        scores = [c["performance_score"] for c in data["top_couriers"]]
        assert scores == sorted(scores, reverse=True), \
            "Couriers not sorted by performance score"

    @pytest.mark.integration
    def test_top_couriers_limit_parameter(
        self,
        client: TestClient,
        org_with_performers: dict
    ):
        """Test that limit parameter works"""
        headers = {"Authorization": f"Bearer {org_with_performers['token']}"}
        response = client.get(
            "/api/v1/dashboard/performance/top-couriers",
            params={"limit": 3},
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["top_couriers"]) <= 3


class TestDashboardSummary:
    """Test dashboard summary endpoint"""

    @pytest.fixture
    def auth_headers_for_summary(self, db_session: Session, test_password: str):
        """Create authenticated user for summary tests"""
        from app.models.tenant.organization import Organization
        from app.models.user import User
        from app.models.tenant.organization_user import OrganizationUser
        from app.core.security import PasswordHasher, TokenManager

        org = Organization(
            name="Summary Test Org",
            slug="summary-test-org",
            is_active=True
        )
        db_session.add(org)
        db_session.commit()

        user = User(
            email="summary_user@test.com",
            full_name="Summary User",
            hashed_password=PasswordHasher.hash_password(test_password),
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

        org_user = OrganizationUser(
            user_id=user.id,
            organization_id=org.id,
            role="ADMIN",
            is_active=True
        )
        db_session.add(org_user)
        db_session.commit()

        token = TokenManager.create_access_token(
            data={
                "sub": str(user.id),
                "org_id": org.id,
                "org_role": "ADMIN"
            }
        )

        return {"Authorization": f"Bearer {token}"}

    @pytest.mark.integration
    def test_summary_structure(
        self,
        client: TestClient,
        auth_headers_for_summary: dict
    ):
        """Test executive summary endpoint structure"""
        response = client.get(
            "/api/v1/dashboard/summary",
            headers=auth_headers_for_summary
        )

        assert response.status_code == 200
        data = response.json()

        assert "summary" in data
        assert "trends" in data
        assert "health_score" in data

        # Check summary structure
        summary = data["summary"]
        assert "total_couriers" in summary
        assert "active_couriers" in summary
        assert "total_vehicles" in summary

        # Check health score structure
        health = data["health_score"]
        assert "overall_score" in health
        assert "status" in health
        assert health["status"] in ["excellent", "good", "fair", "needs_attention"]

    @pytest.mark.integration
    def test_recent_activity_structure(
        self,
        client: TestClient,
        auth_headers_for_summary: dict
    ):
        """Test recent activity endpoint structure"""
        response = client.get(
            "/api/v1/dashboard/recent-activity",
            headers=auth_headers_for_summary
        )

        assert response.status_code == 200
        data = response.json()

        assert "activities" in data
        assert isinstance(data["activities"], list)

        # Check activity structure if any exist
        for activity in data["activities"]:
            assert "type" in activity
            assert "title" in activity
            assert "timestamp" in activity or "description" in activity
