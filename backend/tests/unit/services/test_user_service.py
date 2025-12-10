"""
Unit Tests for User Service

Tests cover:
- User CRUD operations
- Authentication (email/password)
- Google OAuth operations
- User status management
- Role management

Author: BARQ QA Team
Last Updated: 2025-12-10
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.services.user_service import UserService, user_service
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class TestUserService:
    """Test User Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create UserService instance"""
        return UserService(User)

    # ==================== CREATE TESTS ====================

    def test_create_user_success(self, service, db_session):
        """Test successful user creation"""
        user_data = UserCreate(
            email="newuser@test.com",
            password="SecurePass123!",
            full_name="New User",
            role="user"
        )

        user = service.create(db_session, obj_in=user_data)

        assert user is not None
        assert user.email == "newuser@test.com"
        assert user.full_name == "New User"
        assert user.role == "user"
        assert user.is_active is True
        assert user.hashed_password is not None
        assert user.hashed_password != "SecurePass123!"

    def test_create_user_with_superuser_flag(self, service, db_session):
        """Test creating a superuser"""
        user_data = UserCreate(
            email="superuser@test.com",
            password="SecurePass123!",
            full_name="Super User",
            role="admin",
            is_superuser=True
        )

        user = service.create(db_session, obj_in=user_data)

        assert user.is_superuser is True
        assert user.role == "admin"

    def test_create_user_inactive(self, service, db_session):
        """Test creating an inactive user"""
        user_data = UserCreate(
            email="inactive@test.com",
            password="SecurePass123!",
            full_name="Inactive User",
            is_active=False
        )

        user = service.create(db_session, obj_in=user_data)

        assert user.is_active is False

    # ==================== READ TESTS ====================

    def test_get_by_email_exists(self, service, db_session, test_user):
        """Test getting user by email when exists"""
        result = service.get_by_email(db_session, email=test_user.email)

        assert result is not None
        assert result.id == test_user.id
        assert result.email == test_user.email

    def test_get_by_email_not_exists(self, service, db_session):
        """Test getting user by email when not exists"""
        result = service.get_by_email(db_session, email="nonexistent@test.com")

        assert result is None

    def test_get_by_role(self, service, db_session, test_user, admin_user, manager_user):
        """Test getting users by role"""
        users = service.get_by_role(db_session, role="user")

        assert len(users) >= 1
        assert all(u.role == "user" for u in users)

    def test_get_active_users(self, service, db_session, test_user, admin_user):
        """Test getting all active users"""
        users = service.get_active_users(db_session)

        assert len(users) >= 2
        assert all(u.is_active is True for u in users)

    def test_get_by_google_id_exists(self, service, db_session):
        """Test getting user by Google ID when exists"""
        # Create user with Google ID
        google_user = User(
            email="google@test.com",
            full_name="Google User",
            google_id="google_12345",
            is_active=True
        )
        db_session.add(google_user)
        db_session.commit()

        result = service.get_by_google_id(db_session, google_id="google_12345")

        assert result is not None
        assert result.google_id == "google_12345"

    def test_get_by_google_id_not_exists(self, service, db_session):
        """Test getting user by Google ID when not exists"""
        result = service.get_by_google_id(db_session, google_id="nonexistent_google_id")

        assert result is None

    # ==================== UPDATE TESTS ====================

    def test_update_user_full_name(self, service, db_session, test_user):
        """Test updating user full name"""
        update_data = UserUpdate(full_name="Updated Name")

        updated = service.update(db_session, db_obj=test_user, obj_in=update_data)

        assert updated.full_name == "Updated Name"

    def test_update_user_password(self, service, db_session, test_user, test_password):
        """Test updating user password"""
        old_hash = test_user.hashed_password
        update_data = {"password": "NewSecurePass456!"}

        updated = service.update(db_session, db_obj=test_user, obj_in=update_data)

        assert updated.hashed_password != old_hash
        assert verify_password("NewSecurePass456!", updated.hashed_password)

    def test_update_user_role(self, service, db_session, test_user):
        """Test updating user role"""
        update_data = UserUpdate(role="manager")

        updated = service.update(db_session, db_obj=test_user, obj_in=update_data)

        assert updated.role == "manager"

    # ==================== AUTHENTICATION TESTS ====================

    def test_authenticate_valid_credentials(self, service, db_session, test_user, test_password):
        """Test authentication with valid credentials"""
        result = service.authenticate(
            db_session,
            email=test_user.email,
            password=test_password
        )

        assert result is not None
        assert result.id == test_user.id

    def test_authenticate_invalid_password(self, service, db_session, test_user):
        """Test authentication with invalid password"""
        result = service.authenticate(
            db_session,
            email=test_user.email,
            password="WrongPassword!"
        )

        assert result is None

    def test_authenticate_nonexistent_user(self, service, db_session):
        """Test authentication with nonexistent user"""
        result = service.authenticate(
            db_session,
            email="nonexistent@test.com",
            password="SomePassword123!"
        )

        assert result is None

    def test_authenticate_user_without_password(self, service, db_session):
        """Test authentication for user without password (Google OAuth user)"""
        # Create user without password
        oauth_user = User(
            email="oauth@test.com",
            full_name="OAuth User",
            google_id="google_oauth_123",
            is_active=True,
            hashed_password=None
        )
        db_session.add(oauth_user)
        db_session.commit()

        result = service.authenticate(
            db_session,
            email="oauth@test.com",
            password="AnyPassword"
        )

        assert result is None

    # ==================== STATUS TESTS ====================

    def test_is_active_returns_true(self, service, test_user):
        """Test is_active returns True for active user"""
        assert service.is_active(test_user) is True

    def test_is_active_returns_false(self, service, db_session):
        """Test is_active returns False for inactive user"""
        inactive_user = User(
            email="inactive@test.com",
            full_name="Inactive User",
            hashed_password="hash",
            is_active=False
        )
        db_session.add(inactive_user)
        db_session.commit()

        assert service.is_active(inactive_user) is False

    def test_is_superuser_returns_true(self, service, admin_user):
        """Test is_superuser returns True for superuser"""
        assert service.is_superuser(admin_user) is True

    def test_is_superuser_returns_false(self, service, test_user):
        """Test is_superuser returns False for regular user"""
        assert service.is_superuser(test_user) is False

    # ==================== GOOGLE OAUTH TESTS ====================

    def test_create_google_user(self, service, db_session):
        """Test creating user from Google OAuth"""
        user = service.create_google_user(
            db_session,
            email="googleuser@gmail.com",
            google_id="google_oauth_456",
            full_name="Google OAuth User",
            picture="https://example.com/picture.jpg"
        )

        assert user is not None
        assert user.email == "googleuser@gmail.com"
        assert user.google_id == "google_oauth_456"
        assert user.full_name == "Google OAuth User"
        assert user.picture == "https://example.com/picture.jpg"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.role == "user"

    def test_update_google_info(self, service, db_session, test_user):
        """Test updating Google OAuth info for existing user"""
        updated = service.update_google_info(
            db_session,
            user=test_user,
            google_id="linked_google_id",
            picture="https://example.com/new_picture.jpg"
        )

        assert updated.google_id == "linked_google_id"
        assert updated.picture == "https://example.com/new_picture.jpg"

    def test_update_google_info_without_picture(self, service, db_session, test_user):
        """Test updating Google OAuth info without picture"""
        original_picture = test_user.picture

        updated = service.update_google_info(
            db_session,
            user=test_user,
            google_id="another_google_id"
        )

        assert updated.google_id == "another_google_id"
        assert updated.picture == original_picture

    # ==================== DEACTIVATION TESTS ====================

    def test_deactivate_user(self, service, db_session, test_user):
        """Test deactivating a user"""
        result = service.deactivate(db_session, user_id=test_user.id)

        assert result is not None
        assert result.is_active is False

    def test_deactivate_nonexistent_user(self, service, db_session):
        """Test deactivating nonexistent user"""
        result = service.deactivate(db_session, user_id=99999)

        assert result is None

    def test_activate_user(self, service, db_session):
        """Test activating a user"""
        # Create inactive user
        inactive_user = User(
            email="toreactivate@test.com",
            full_name="To Reactivate",
            hashed_password="hash",
            is_active=False
        )
        db_session.add(inactive_user)
        db_session.commit()

        result = service.activate(db_session, user_id=inactive_user.id)

        assert result is not None
        assert result.is_active is True

    def test_activate_nonexistent_user(self, service, db_session):
        """Test activating nonexistent user"""
        result = service.activate(db_session, user_id=99999)

        assert result is None

    # ==================== PASSWORD CHANGE TESTS ====================

    def test_change_password(self, service, db_session, test_user):
        """Test changing user password"""
        old_hash = test_user.hashed_password

        result = service.change_password(
            db_session,
            user=test_user,
            new_password="NewSecurePassword789!"
        )

        assert result.hashed_password != old_hash
        assert verify_password("NewSecurePassword789!", result.hashed_password)

    # ==================== PAGINATION TESTS ====================

    def test_get_by_role_with_pagination(self, service, db_session):
        """Test getting users by role with pagination"""
        # Create multiple users
        for i in range(5):
            user = User(
                email=f"paginateduser{i}@test.com",
                full_name=f"Paginated User {i}",
                hashed_password="hash",
                role="user",
                is_active=True
            )
            db_session.add(user)
        db_session.commit()

        # Get first page
        first_page = service.get_by_role(db_session, role="user", skip=0, limit=2)
        # Get second page
        second_page = service.get_by_role(db_session, role="user", skip=2, limit=2)

        assert len(first_page) == 2
        assert len(second_page) == 2
        assert first_page[0].id != second_page[0].id

    def test_get_active_users_with_pagination(self, service, db_session):
        """Test getting active users with pagination"""
        users = service.get_active_users(db_session, skip=0, limit=1)

        assert len(users) <= 1
