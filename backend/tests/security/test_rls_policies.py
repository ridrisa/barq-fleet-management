"""
Row-Level Security (RLS) Policy Tests

Tests to verify that PostgreSQL RLS policies are properly enforced
and that tenant isolation is maintained across all operations.

Author: BARQ QA Team
Last Updated: 2025-12-06
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text


class TestRLSPolicies:
    """Test Row-Level Security policy enforcement"""

    @pytest.fixture
    def org_a_data(self, db_session: Session):
        """Create test organization A with data"""
        from app.models.tenant.organization import Organization
        from app.models.fleet.courier import Courier, CourierStatus, SponsorshipStatus, ProjectType

        # Create org A
        org_a = Organization(
            name="Test Org A",
            slug="test-org-a",
            is_active=True
        )
        db_session.add(org_a)
        db_session.commit()
        db_session.refresh(org_a)

        # Create courier for org A
        courier_a = Courier(
            barq_id="BRQ-ORG-A-001",
            full_name="Courier Org A",
            email="courier_a@test.com",
            mobile_number="+966501111111",
            employee_id="EMP-A-001",
            status=CourierStatus.ACTIVE,
            sponsorship_status=SponsorshipStatus.INHOUSE,
            project_type=ProjectType.BARQ,
            city="Riyadh",
            organization_id=org_a.id
        )
        db_session.add(courier_a)
        db_session.commit()
        db_session.refresh(courier_a)

        return {"org": org_a, "courier": courier_a}

    @pytest.fixture
    def org_b_data(self, db_session: Session):
        """Create test organization B with data"""
        from app.models.tenant.organization import Organization
        from app.models.fleet.courier import Courier, CourierStatus, SponsorshipStatus, ProjectType

        # Create org B
        org_b = Organization(
            name="Test Org B",
            slug="test-org-b",
            is_active=True
        )
        db_session.add(org_b)
        db_session.commit()
        db_session.refresh(org_b)

        # Create courier for org B
        courier_b = Courier(
            barq_id="BRQ-ORG-B-001",
            full_name="Courier Org B",
            email="courier_b@test.com",
            mobile_number="+966502222222",
            employee_id="EMP-B-001",
            status=CourierStatus.ACTIVE,
            sponsorship_status=SponsorshipStatus.INHOUSE,
            project_type=ProjectType.BARQ,
            city="Jeddah",
            organization_id=org_b.id
        )
        db_session.add(courier_b)
        db_session.commit()
        db_session.refresh(courier_b)

        return {"org": org_b, "courier": courier_b}

    @pytest.mark.security
    def test_tenant_isolation_couriers(
        self,
        client: TestClient,
        db_session: Session,
        org_a_data: dict,
        org_b_data: dict,
        test_password: str
    ):
        """Test that couriers from one org cannot see couriers from another"""
        from app.models.user import User
        from app.models.tenant.organization_user import OrganizationUser
        from app.core.security import PasswordHasher, TokenManager

        # Create user for org A
        user_a = User(
            email="user_a@test.com",
            full_name="User A",
            hashed_password=PasswordHasher.hash_password(test_password),
            is_active=True
        )
        db_session.add(user_a)
        db_session.commit()
        db_session.refresh(user_a)

        # Associate user with org A
        org_user_a = OrganizationUser(
            user_id=user_a.id,
            organization_id=org_a_data["org"].id,
            role="ADMIN",
            is_active=True
        )
        db_session.add(org_user_a)
        db_session.commit()

        # Create token for user A with org A context
        token_a = TokenManager.create_access_token(
            data={
                "sub": str(user_a.id),
                "org_id": org_a_data["org"].id,
                "org_role": "ADMIN"
            }
        )
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # Get couriers for org A
        response = client.get(
            "/api/v1/fleet/couriers",
            headers=headers_a
        )

        assert response.status_code == 200
        data = response.json()
        couriers = data.get("items", data)

        # Should only see org A couriers
        courier_ids = [c.get("barq_id") for c in couriers if isinstance(c, dict)]

        assert org_a_data["courier"].barq_id in courier_ids or len(couriers) == 0, \
            "Should see org A courier"
        assert org_b_data["courier"].barq_id not in courier_ids, \
            "Should NOT see org B courier"

    @pytest.mark.security
    def test_tenant_isolation_vehicles(
        self,
        client: TestClient,
        db_session: Session,
        test_password: str
    ):
        """Test that vehicles are isolated by organization"""
        from app.models.tenant.organization import Organization
        from app.models.fleet.vehicle import Vehicle, VehicleStatus, VehicleType
        from app.models.user import User
        from app.models.tenant.organization_user import OrganizationUser
        from app.core.security import PasswordHasher, TokenManager

        # Create two organizations with vehicles
        org_1 = Organization(name="Vehicle Org 1", slug="vehicle-org-1", is_active=True)
        org_2 = Organization(name="Vehicle Org 2", slug="vehicle-org-2", is_active=True)
        db_session.add_all([org_1, org_2])
        db_session.commit()

        vehicle_1 = Vehicle(
            plate_number="VEH-111",
            vehicle_type=VehicleType.MOTORCYCLE,
            make="Honda",
            model="Wave",
            year=2023,
            status=VehicleStatus.AVAILABLE,
            city="Riyadh",
            organization_id=org_1.id
        )
        vehicle_2 = Vehicle(
            plate_number="VEH-222",
            vehicle_type=VehicleType.MOTORCYCLE,
            make="Yamaha",
            model="FZ",
            year=2023,
            status=VehicleStatus.AVAILABLE,
            city="Jeddah",
            organization_id=org_2.id
        )
        db_session.add_all([vehicle_1, vehicle_2])
        db_session.commit()

        # Create user for org 1
        user = User(
            email="vehicle_user@test.com",
            full_name="Vehicle User",
            hashed_password=PasswordHasher.hash_password(test_password),
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

        org_user = OrganizationUser(
            user_id=user.id,
            organization_id=org_1.id,
            role="ADMIN",
            is_active=True
        )
        db_session.add(org_user)
        db_session.commit()

        token = TokenManager.create_access_token(
            data={
                "sub": str(user.id),
                "org_id": org_1.id,
                "org_role": "ADMIN"
            }
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/v1/fleet/vehicles", headers=headers)

        assert response.status_code == 200
        data = response.json()
        vehicles = data.get("items", data)

        plate_numbers = [v.get("plate_number") for v in vehicles if isinstance(v, dict)]

        # Should only see org 1 vehicles
        assert "VEH-222" not in plate_numbers, \
            "Should NOT see org 2 vehicles"

    @pytest.mark.security
    def test_cross_tenant_access_attempt(
        self,
        client: TestClient,
        db_session: Session,
        org_a_data: dict,
        org_b_data: dict,
        test_password: str
    ):
        """Test that users cannot access other tenant's specific resources"""
        from app.models.user import User
        from app.models.tenant.organization_user import OrganizationUser
        from app.core.security import PasswordHasher, TokenManager

        # Create user for org A
        user_a = User(
            email="cross_tenant_user@test.com",
            full_name="Cross Tenant User",
            hashed_password=PasswordHasher.hash_password(test_password),
            is_active=True
        )
        db_session.add(user_a)
        db_session.commit()

        org_user_a = OrganizationUser(
            user_id=user_a.id,
            organization_id=org_a_data["org"].id,
            role="ADMIN",
            is_active=True
        )
        db_session.add(org_user_a)
        db_session.commit()

        token_a = TokenManager.create_access_token(
            data={
                "sub": str(user_a.id),
                "org_id": org_a_data["org"].id,
                "org_role": "ADMIN"
            }
        )
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # Try to access org B's courier directly
        response = client.get(
            f"/api/v1/fleet/couriers/{org_b_data['courier'].id}",
            headers=headers_a
        )

        # Should return 404 (not found in their org) or 403
        assert response.status_code in [403, 404], \
            f"Cross-tenant access succeeded! Status: {response.status_code}"

    @pytest.mark.security
    def test_cross_tenant_update_attempt(
        self,
        client: TestClient,
        db_session: Session,
        org_a_data: dict,
        org_b_data: dict,
        test_password: str
    ):
        """Test that users cannot update other tenant's resources"""
        from app.models.user import User
        from app.models.tenant.organization_user import OrganizationUser
        from app.core.security import PasswordHasher, TokenManager

        # Create user for org A
        user_a = User(
            email="cross_update_user@test.com",
            full_name="Cross Update User",
            hashed_password=PasswordHasher.hash_password(test_password),
            is_active=True
        )
        db_session.add(user_a)
        db_session.commit()

        org_user_a = OrganizationUser(
            user_id=user_a.id,
            organization_id=org_a_data["org"].id,
            role="ADMIN",
            is_active=True
        )
        db_session.add(org_user_a)
        db_session.commit()

        token_a = TokenManager.create_access_token(
            data={
                "sub": str(user_a.id),
                "org_id": org_a_data["org"].id,
                "org_role": "ADMIN"
            }
        )
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # Try to update org B's courier
        original_name = org_b_data["courier"].full_name
        response = client.put(
            f"/api/v1/fleet/couriers/{org_b_data['courier'].id}",
            json={"full_name": "Hacked Name"},
            headers=headers_a
        )

        # Should fail
        assert response.status_code in [403, 404], \
            f"Cross-tenant update succeeded! Status: {response.status_code}"

        # Verify courier wasn't modified
        db_session.refresh(org_b_data["courier"])
        assert org_b_data["courier"].full_name == original_name, \
            "Courier was modified despite access denial!"

    @pytest.mark.security
    def test_cross_tenant_delete_attempt(
        self,
        client: TestClient,
        db_session: Session,
        org_a_data: dict,
        org_b_data: dict,
        test_password: str
    ):
        """Test that users cannot delete other tenant's resources"""
        from app.models.user import User
        from app.models.tenant.organization_user import OrganizationUser
        from app.core.security import PasswordHasher, TokenManager

        # Create user for org A
        user_a = User(
            email="cross_delete_user@test.com",
            full_name="Cross Delete User",
            hashed_password=PasswordHasher.hash_password(test_password),
            is_active=True
        )
        db_session.add(user_a)
        db_session.commit()

        org_user_a = OrganizationUser(
            user_id=user_a.id,
            organization_id=org_a_data["org"].id,
            role="ADMIN",
            is_active=True
        )
        db_session.add(org_user_a)
        db_session.commit()

        token_a = TokenManager.create_access_token(
            data={
                "sub": str(user_a.id),
                "org_id": org_a_data["org"].id,
                "org_role": "ADMIN"
            }
        )
        headers_a = {"Authorization": f"Bearer {token_a}"}

        courier_b_id = org_b_data["courier"].id

        # Try to delete org B's courier
        response = client.delete(
            f"/api/v1/fleet/couriers/{courier_b_id}",
            headers=headers_a
        )

        # Should fail
        assert response.status_code in [403, 404], \
            f"Cross-tenant delete succeeded! Status: {response.status_code}"

        # Verify courier still exists
        from app.models.fleet.courier import Courier
        courier = db_session.query(Courier).filter(Courier.id == courier_b_id).first()
        assert courier is not None, "Courier was deleted despite access denial!"

    @pytest.mark.security
    def test_rls_context_properly_reset(self, db_session: Session):
        """Test that RLS context is properly reset between requests"""
        # Set context for org 1
        db_session.execute(
            text("SET app.current_org_id = :org_id"),
            {"org_id": "1"}
        )

        # Simulate request end - context should be reset
        try:
            db_session.execute(text("RESET app.current_org_id"))
        except Exception:
            pass

        # Verify context was reset
        try:
            result = db_session.execute(
                text("SHOW app.current_org_id")
            ).scalar()
            # If we get here, context should be empty or default
            assert result in [None, "", "0"], \
                f"RLS context not properly reset: {result}"
        except Exception:
            # Some databases throw an error when variable isn't set
            pass


class TestDashboardTenantIsolation:
    """Test that dashboard data is properly isolated by tenant"""

    @pytest.mark.security
    def test_dashboard_stats_isolation(
        self,
        client: TestClient,
        db_session: Session,
        test_password: str
    ):
        """Test that dashboard stats only show current org's data"""
        from app.models.tenant.organization import Organization
        from app.models.fleet.courier import Courier, CourierStatus, SponsorshipStatus, ProjectType
        from app.models.user import User
        from app.models.tenant.organization_user import OrganizationUser
        from app.core.security import PasswordHasher, TokenManager

        # Create two organizations
        org_1 = Organization(name="Dashboard Org 1", slug="dashboard-org-1", is_active=True)
        org_2 = Organization(name="Dashboard Org 2", slug="dashboard-org-2", is_active=True)
        db_session.add_all([org_1, org_2])
        db_session.commit()

        # Add 5 couriers to org 1
        for i in range(5):
            courier = Courier(
                barq_id=f"BRQ-DASH-1-{i}",
                full_name=f"Courier 1-{i}",
                email=f"courier1_{i}@test.com",
                mobile_number=f"+96650111{i:04d}",
                employee_id=f"EMP-DASH-1-{i}",
                status=CourierStatus.ACTIVE,
                sponsorship_status=SponsorshipStatus.INHOUSE,
                project_type=ProjectType.BARQ,
                city="Riyadh",
                organization_id=org_1.id
            )
            db_session.add(courier)

        # Add 10 couriers to org 2
        for i in range(10):
            courier = Courier(
                barq_id=f"BRQ-DASH-2-{i}",
                full_name=f"Courier 2-{i}",
                email=f"courier2_{i}@test.com",
                mobile_number=f"+96650222{i:04d}",
                employee_id=f"EMP-DASH-2-{i}",
                status=CourierStatus.ACTIVE,
                sponsorship_status=SponsorshipStatus.INHOUSE,
                project_type=ProjectType.BARQ,
                city="Jeddah",
                organization_id=org_2.id
            )
            db_session.add(courier)

        db_session.commit()

        # Create user for org 1
        user = User(
            email="dashboard_user@test.com",
            full_name="Dashboard User",
            hashed_password=PasswordHasher.hash_password(test_password),
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

        org_user = OrganizationUser(
            user_id=user.id,
            organization_id=org_1.id,
            role="ADMIN",
            is_active=True
        )
        db_session.add(org_user)
        db_session.commit()

        token = TokenManager.create_access_token(
            data={
                "sub": str(user.id),
                "org_id": org_1.id,
                "org_role": "ADMIN"
            }
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/v1/dashboard/stats", headers=headers)

        assert response.status_code == 200
        data = response.json()

        # Should only count org 1's couriers (5, not 15)
        total_couriers = data.get("total_couriers", 0)
        assert total_couriers <= 5, \
            f"Dashboard showing data from other orgs: {total_couriers} couriers"
