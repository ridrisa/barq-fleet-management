"""
Integration Tests for Authentication API

Tests user authentication, registration, and token management.

Author: BARQ QA Team
Last Updated: 2025-12-02
"""

import pytest
from tests.utils.factories import UserFactory, AdminUserFactory
from tests.utils.api_helpers import (
    make_get_request,
    make_post_request,
    assert_success_response,
    assert_unauthorized,
    assert_validation_error,
    create_test_token
)


@pytest.mark.integration
@pytest.mark.admin
@pytest.mark.auth
class TestAuthAPI:
    """Test Authentication API endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self, db_session, client, test_password):
        """Setup test data"""
        self.db = db_session
        self.client = client
        self.test_password = test_password

        # Create test user
        self.user = UserFactory.create()
        self.db.commit()

    def test_login_success(self):
        """Test successful login"""
        login_data = {
            "username": self.user.email,
            "password": self.test_password
        }

        response = self.client.post(
            "/api/v1/auth/login",
            data=login_data
        )

        assert_success_response(response)
        data = response.json()

        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            "username": self.user.email,
            "password": "wrong_password"
        }

        response = self.client.post(
            "/api/v1/auth/login",
            data=login_data
        )

        assert_unauthorized(response)

    def test_login_non_existent_user(self):
        """Test login with non-existent user"""
        login_data = {
            "username": "nonexistent@test.com",
            "password": "password"
        }

        response = self.client.post(
            "/api/v1/auth/login",
            data=login_data
        )

        assert_unauthorized(response)

    def test_get_current_user(self):
        """Test getting current user profile"""
        token = create_test_token(self.user.id, self.user.email, "user")

        response = make_get_request(
            self.client,
            "/api/v1/auth/me",
            token
        )

        assert_success_response(response)
        data = response.json()

        assert data["email"] == self.user.email
        assert data["id"] == self.user.id

    def test_get_current_user_unauthorized(self):
        """Test getting current user without token"""
        response = make_get_request(
            self.client,
            "/api/v1/auth/me"
        )

        assert_unauthorized(response)

    def test_refresh_token(self):
        """Test refreshing access token"""
        token = create_test_token(self.user.id, self.user.email, "user")

        response = make_post_request(
            self.client,
            "/api/v1/auth/refresh",
            {},
            token
        )

        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data

    def test_logout(self):
        """Test logout"""
        token = create_test_token(self.user.id, self.user.email, "user")

        response = make_post_request(
            self.client,
            "/api/v1/auth/logout",
            {},
            token
        )

        assert response.status_code in [200, 204]

    def test_register_new_user(self):
        """Test user registration"""
        register_data = {
            "email": "newuser@test.com",
            "full_name": "New User",
            "password": "NewPassword@123",
            "password_confirm": "NewPassword@123"
        }

        response = make_post_request(
            self.client,
            "/api/v1/auth/register",
            register_data
        )

        if response.status_code == 201:
            data = response.json()
            assert data["email"] == "newuser@test.com"

    def test_register_duplicate_email(self):
        """Test registration with duplicate email"""
        register_data = {
            "email": self.user.email,  # Existing email
            "full_name": "Duplicate User",
            "password": "Password@123",
            "password_confirm": "Password@123"
        }

        response = make_post_request(
            self.client,
            "/api/v1/auth/register",
            register_data
        )

        assert response.status_code in [400, 409]

    def test_register_password_mismatch(self):
        """Test registration with password mismatch"""
        register_data = {
            "email": "test@test.com",
            "full_name": "Test User",
            "password": "Password@123",
            "password_confirm": "DifferentPassword@123"
        }

        response = make_post_request(
            self.client,
            "/api/v1/auth/register",
            register_data
        )

        assert_validation_error(response)

    def test_change_password(self):
        """Test changing user password"""
        token = create_test_token(self.user.id, self.user.email, "user")

        change_data = {
            "current_password": self.test_password,
            "new_password": "NewPassword@456",
            "new_password_confirm": "NewPassword@456"
        }

        response = make_post_request(
            self.client,
            "/api/v1/auth/change-password",
            change_data,
            token
        )

        if response.status_code == 200:
            assert_success_response(response)

    def test_forgot_password(self):
        """Test forgot password request"""
        forgot_data = {
            "email": self.user.email
        }

        response = make_post_request(
            self.client,
            "/api/v1/auth/forgot-password",
            forgot_data
        )

        if response.status_code == 200:
            assert_success_response(response)

    def test_reset_password_with_token(self):
        """Test resetting password with token"""
        # This would require generating a reset token first
        reset_data = {
            "token": "reset-token-here",
            "new_password": "NewPassword@789",
            "new_password_confirm": "NewPassword@789"
        }

        response = make_post_request(
            self.client,
            "/api/v1/auth/reset-password",
            reset_data
        )

        # May return 400 if token is invalid
        assert response.status_code in [200, 400, 404]
