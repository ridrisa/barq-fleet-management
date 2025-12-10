"""
Unit Tests for Organization/Tenant Services

Tests cover:
- Organization Service
- Organization User Service
- Multi-tenancy operations

Author: BARQ QA Team
Last Updated: 2025-12-10
"""

import pytest
from datetime import date, datetime
from unittest.mock import Mock, patch

from app.services.tenant.organization_service import OrganizationService
from app.services.tenant.organization_user_service import OrganizationUserService
from app.models.tenant.organization import Organization
from app.models.tenant.organization_user import OrganizationUser


# ==================== ORGANIZATION SERVICE TESTS ====================

class TestOrganizationService:
    """Test Organization Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create OrganizationService instance"""
        return OrganizationService(Organization)

    # ==================== CRUD TESTS ====================

    def test_create_organization(self, service, db_session):
        """Test creating an organization"""
        from app.schemas.tenant.organization import OrganizationCreate

        org_data = OrganizationCreate(
            name="ACME Fleet Services",
            slug="acme-fleet",
            is_active=True
        )

        org = service.create(db_session, obj_in=org_data)

        assert org is not None
        assert org.name == "ACME Fleet Services"
        assert org.slug == "acme-fleet"
        assert org.is_active is True

    def test_get_organization_by_id(self, service, db_session, test_organization):
        """Test getting organization by ID"""
        result = service.get(db_session, test_organization.id)

        assert result is not None
        assert result.id == test_organization.id

    def test_get_organization_by_slug(self, service, db_session, test_organization):
        """Test getting organization by slug"""
        result = service.get_by_slug(db_session, slug=test_organization.slug)

        assert result is not None
        assert result.slug == test_organization.slug

    def test_get_organization_by_slug_not_exists(self, service, db_session):
        """Test getting organization by slug when not exists"""
        result = service.get_by_slug(db_session, slug="nonexistent-org")

        assert result is None

    def test_get_all_organizations(self, service, db_session, test_organization, second_organization):
        """Test getting all organizations"""
        result = service.get_multi(db_session)

        assert len(result) >= 2

    # ==================== STATUS FILTER TESTS ====================

    def test_get_active_organizations(self, service, db_session):
        """Test getting active organizations"""
        active = Organization(name="Active Org", slug="active-org", is_active=True)
        inactive = Organization(name="Inactive Org", slug="inactive-org", is_active=False)
        db_session.add_all([active, inactive])
        db_session.commit()

        result = service.get_active(db_session)

        assert all(org.is_active is True for org in result)

    def test_get_inactive_organizations(self, service, db_session):
        """Test getting inactive organizations"""
        active = Organization(name="Active Org 2", slug="active-org-2", is_active=True)
        inactive = Organization(name="Inactive Org 2", slug="inactive-org-2", is_active=False)
        db_session.add_all([active, inactive])
        db_session.commit()

        result = service.get_inactive(db_session)

        assert all(org.is_active is False for org in result)

    # ==================== ACTIVATION TESTS ====================

    def test_activate_organization(self, service, db_session):
        """Test activating an organization"""
        org = Organization(name="To Activate", slug="to-activate", is_active=False)
        db_session.add(org)
        db_session.commit()

        result = service.activate(db_session, organization_id=org.id)

        assert result.is_active is True

    def test_deactivate_organization(self, service, db_session):
        """Test deactivating an organization"""
        org = Organization(name="To Deactivate", slug="to-deactivate", is_active=True)
        db_session.add(org)
        db_session.commit()

        result = service.deactivate(db_session, organization_id=org.id)

        assert result.is_active is False

    # ==================== UPDATE TESTS ====================

    def test_update_organization_name(self, service, db_session, test_organization):
        """Test updating organization name"""
        from app.schemas.tenant.organization import OrganizationUpdate

        update_data = OrganizationUpdate(name="Updated Name")

        result = service.update(db_session, db_obj=test_organization, obj_in=update_data)

        assert result.name == "Updated Name"

    def test_update_organization_settings(self, service, db_session, test_organization):
        """Test updating organization settings"""
        settings = {
            "timezone": "Asia/Riyadh",
            "currency": "SAR",
            "language": "ar"
        }

        result = service.update_settings(
            db_session,
            organization_id=test_organization.id,
            settings=settings
        )

        assert result is not None

    # ==================== STATISTICS TESTS ====================

    def test_get_organization_statistics(self, service, db_session, test_organization):
        """Test getting organization statistics"""
        stats = service.get_statistics(db_session, organization_id=test_organization.id)

        assert "total_users" in stats
        assert "total_couriers" in stats
        assert "total_vehicles" in stats

    def test_get_all_statistics(self, service, db_session):
        """Test getting overall statistics"""
        stats = service.get_all_statistics(db_session)

        assert "total_organizations" in stats
        assert "active_organizations" in stats

    # ==================== SEARCH TESTS ====================

    def test_search_organizations(self, service, db_session):
        """Test searching organizations"""
        org = Organization(name="Searchable Corp", slug="searchable-corp", is_active=True)
        db_session.add(org)
        db_session.commit()

        result = service.search(db_session, search_term="Searchable")

        assert len(result) >= 1
        assert any(o.name == "Searchable Corp" for o in result)


# ==================== ORGANIZATION USER SERVICE TESTS ====================

class TestOrganizationUserService:
    """Test Organization User Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create OrganizationUserService instance"""
        return OrganizationUserService(OrganizationUser)

    # ==================== ADD USER TESTS ====================

    def test_add_user_to_organization(self, service, db_session, test_user, test_organization):
        """Test adding user to organization"""
        result = service.add_user(
            db_session,
            user_id=test_user.id,
            organization_id=test_organization.id,
            role="MEMBER"
        )

        assert result is not None
        assert result.user_id == test_user.id
        assert result.organization_id == test_organization.id
        assert result.role == "MEMBER"

    def test_add_user_as_admin(self, service, db_session, admin_user, test_organization):
        """Test adding user as admin"""
        result = service.add_user(
            db_session,
            user_id=admin_user.id,
            organization_id=test_organization.id,
            role="ADMIN"
        )

        assert result.role == "ADMIN"

    def test_add_user_as_owner(self, service, db_session, test_user, second_organization):
        """Test adding user as owner"""
        result = service.add_user(
            db_session,
            user_id=test_user.id,
            organization_id=second_organization.id,
            role="OWNER"
        )

        assert result.role == "OWNER"

    def test_add_user_duplicate_fails(self, service, db_session, test_user, test_organization):
        """Test adding duplicate user fails"""
        # First add
        service.add_user(
            db_session,
            user_id=test_user.id,
            organization_id=test_organization.id,
            role="MEMBER"
        )

        # Second add should fail or return existing
        with pytest.raises(Exception):
            service.add_user(
                db_session,
                user_id=test_user.id,
                organization_id=test_organization.id,
                role="MEMBER"
            )

    # ==================== REMOVE USER TESTS ====================

    def test_remove_user_from_organization(self, service, db_session, test_user, test_organization):
        """Test removing user from organization"""
        # First add
        service.add_user(
            db_session,
            user_id=test_user.id,
            organization_id=test_organization.id,
            role="MEMBER"
        )

        # Then remove
        result = service.remove_user(
            db_session,
            user_id=test_user.id,
            organization_id=test_organization.id
        )

        assert result is True

    def test_remove_user_not_member(self, service, db_session, manager_user, test_organization):
        """Test removing user who is not a member"""
        result = service.remove_user(
            db_session,
            user_id=manager_user.id,
            organization_id=test_organization.id
        )

        assert result is False

    # ==================== ROLE UPDATE TESTS ====================

    def test_update_user_role(self, service, db_session, test_user, test_organization):
        """Test updating user role in organization"""
        # First add as member
        service.add_user(
            db_session,
            user_id=test_user.id,
            organization_id=test_organization.id,
            role="MEMBER"
        )

        # Promote to admin
        result = service.update_role(
            db_session,
            user_id=test_user.id,
            organization_id=test_organization.id,
            new_role="ADMIN"
        )

        assert result.role == "ADMIN"

    def test_demote_user_role(self, service, db_session, test_user, test_organization):
        """Test demoting user role"""
        # Add as admin
        service.add_user(
            db_session,
            user_id=test_user.id,
            organization_id=test_organization.id,
            role="ADMIN"
        )

        # Demote to member
        result = service.update_role(
            db_session,
            user_id=test_user.id,
            organization_id=test_organization.id,
            new_role="MEMBER"
        )

        assert result.role == "MEMBER"

    # ==================== QUERY TESTS ====================

    def test_get_users_by_organization(self, service, db_session, test_user, admin_user, test_organization):
        """Test getting users by organization"""
        service.add_user(db_session, user_id=test_user.id, organization_id=test_organization.id, role="MEMBER")
        service.add_user(db_session, user_id=admin_user.id, organization_id=test_organization.id, role="ADMIN")

        result = service.get_by_organization(db_session, organization_id=test_organization.id)

        assert len(result) >= 2

    def test_get_organizations_by_user(self, service, db_session, test_user, test_organization, second_organization):
        """Test getting organizations by user"""
        service.add_user(db_session, user_id=test_user.id, organization_id=test_organization.id, role="MEMBER")
        service.add_user(db_session, user_id=test_user.id, organization_id=second_organization.id, role="MEMBER")

        result = service.get_by_user(db_session, user_id=test_user.id)

        assert len(result) >= 2

    def test_get_users_by_role(self, service, db_session, test_user, admin_user, test_organization):
        """Test getting users by role in organization"""
        service.add_user(db_session, user_id=test_user.id, organization_id=test_organization.id, role="MEMBER")
        service.add_user(db_session, user_id=admin_user.id, organization_id=test_organization.id, role="ADMIN")

        admins = service.get_by_role(
            db_session,
            organization_id=test_organization.id,
            role="ADMIN"
        )

        assert all(u.role == "ADMIN" for u in admins)

    def test_get_organization_owners(self, service, db_session, test_user, test_organization):
        """Test getting organization owners"""
        service.add_user(db_session, user_id=test_user.id, organization_id=test_organization.id, role="OWNER")

        owners = service.get_owners(db_session, organization_id=test_organization.id)

        assert all(u.role == "OWNER" for u in owners)

    # ==================== CHECK MEMBERSHIP TESTS ====================

    def test_is_member(self, service, db_session, test_user, test_organization):
        """Test checking if user is member"""
        service.add_user(db_session, user_id=test_user.id, organization_id=test_organization.id, role="MEMBER")

        is_member = service.is_member(
            db_session,
            user_id=test_user.id,
            organization_id=test_organization.id
        )

        assert is_member is True

    def test_is_not_member(self, service, db_session, manager_user, test_organization):
        """Test checking if user is not member"""
        is_member = service.is_member(
            db_session,
            user_id=manager_user.id,
            organization_id=test_organization.id
        )

        assert is_member is False

    def test_has_role(self, service, db_session, test_user, test_organization):
        """Test checking if user has specific role"""
        service.add_user(db_session, user_id=test_user.id, organization_id=test_organization.id, role="ADMIN")

        has_admin = service.has_role(
            db_session,
            user_id=test_user.id,
            organization_id=test_organization.id,
            role="ADMIN"
        )

        assert has_admin is True

    def test_get_user_role(self, service, db_session, test_user, test_organization):
        """Test getting user's role in organization"""
        service.add_user(db_session, user_id=test_user.id, organization_id=test_organization.id, role="MEMBER")

        role = service.get_user_role(
            db_session,
            user_id=test_user.id,
            organization_id=test_organization.id
        )

        assert role == "MEMBER"

    # ==================== PAGINATION TESTS ====================

    def test_get_users_pagination(self, service, db_session, test_organization):
        """Test pagination for organization users"""
        # Create and add multiple users
        from app.models.user import User
        from app.core.security import PasswordHasher

        for i in range(5):
            user = User(
                email=f"paginateduser{i}@test.com",
                full_name=f"User {i}",
                hashed_password=PasswordHasher.hash_password("Test@1234"),
                is_active=True
            )
            db_session.add(user)
            db_session.flush()
            service.add_user(db_session, user_id=user.id, organization_id=test_organization.id, role="MEMBER")

        db_session.commit()

        first_page = service.get_by_organization(db_session, organization_id=test_organization.id, skip=0, limit=2)
        second_page = service.get_by_organization(db_session, organization_id=test_organization.id, skip=2, limit=2)

        assert len(first_page) == 2
        assert len(second_page) == 2
