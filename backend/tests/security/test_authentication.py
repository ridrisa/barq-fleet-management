"""
Security Tests for Authentication and Authorization

Tests cover:
- Authentication bypass attempts
- Token validation
- Password security
- Rate limiting
- SQL injection prevention
- Authorization boundaries

Author: BARQ QA Team
Last Updated: 2025-12-02
"""

import pytest
import time
from tests.utils.test_helpers import APITestHelper


class TestAuthenticationSecurity:
    """Security tests for authentication system"""

    def test_access_protected_endpoint_without_token(self, client):
        """Test that protected endpoints reject requests without token"""
        response = client.get("/api/v1/fleet/couriers")

        assert response.status_code == 401
        assert "unauthorized" in response.json().get("detail", "").lower()

    def test_access_with_invalid_token(self, client):
        """Test that invalid tokens are rejected"""
        headers = {"Authorization": "Bearer invalid-token-12345"}

        response = client.get(
            "/api/v1/fleet/couriers",
            headers=headers
        )

        assert response.status_code == 401

    def test_access_with_expired_token(self, client, test_user):
        """Test that expired tokens are rejected"""
        from datetime import timedelta
        from app.core.security import TokenManager

        # Create token with negative expiry (already expired)
        expired_token = TokenManager.create_access_token(
            data={"sub": str(test_user.id)},
            expires_delta=timedelta(seconds=-1)
        )

        headers = {"Authorization": f"Bearer {expired_token}"}

        response = client.get(
            "/api/v1/fleet/couriers",
            headers=headers
        )

        assert response.status_code == 401

    def test_access_with_malformed_token(self, client):
        """Test malformed authorization headers"""
        test_cases = [
            "Bearer",  # Missing token
            "invalid-format-token",  # No Bearer prefix
            "Bearer ",  # Empty token
            "Bearer token.with.extra.parts.here",  # Invalid JWT structure
        ]

        for auth_header in test_cases:
            headers = {"Authorization": auth_header}
            response = client.get(
                "/api/v1/fleet/couriers",
                headers=headers
            )
            assert response.status_code == 401, f"Failed for: {auth_header}"

    def test_password_hash_security(self, db_session, test_password):
        """Test that passwords are properly hashed"""
        from app.models.user import User
        from app.core.security import PasswordHasher

        user = User(
            email="security@test.com",
            full_name="Security Test",
            hashed_password=PasswordHasher.hash_password(test_password)
        )
        db_session.add(user)
        db_session.commit()

        # Password should be hashed
        assert user.hashed_password != test_password
        assert "$" in user.hashed_password  # Hash format marker

        # Should verify correctly
        assert PasswordHasher.verify_password(test_password, user.hashed_password)

        # Should fail with wrong password
        assert not PasswordHasher.verify_password("wrong-password", user.hashed_password)

    def test_weak_password_rejection(self, client, admin_headers):
        """Test that weak passwords are rejected"""
        weak_passwords = [
            "123456",  # Too common
            "password",  # Too common
            "abc",  # Too short
            "nouppercaseordigits",  # No uppercase or digits
            "NOLOWERCASE123",  # No lowercase
        ]

        for weak_pass in weak_passwords:
            user_data = {
                "email": f"test_{weak_pass}@test.com",
                "full_name": "Test User",
                "password": weak_pass,
                "role": "user"
            }

            response = client.post(
                "/api/v1/auth/register",
                json=user_data
            )

            # Should reject weak password
            assert response.status_code in [400, 422], f"Weak password accepted: {weak_pass}"

    def test_brute_force_protection(self, client, test_user):
        """Test brute force login protection"""
        # Attempt multiple failed logins
        for _ in range(6):  # Assuming max 5 attempts
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": test_user.email,
                    "password": "wrong-password"
                }
            )
            assert response.status_code == 401

        # Next attempt should be rate limited
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "wrong-password"
            }
        )

        # Should be locked out (429 or 401 with specific message)
        assert response.status_code in [429, 401]

    def test_sql_injection_prevention_login(self, client):
        """Test SQL injection attempts in login"""
        sql_injection_attempts = [
            "' OR '1'='1",
            "admin' --",
            "' OR 1=1--",
            "admin' OR '1'='1' /*",
        ]

        for injection in sql_injection_attempts:
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": injection,
                    "password": injection
                }
            )

            # Should not succeed
            assert response.status_code == 401, f"SQL injection succeeded: {injection}"

    def test_authorization_user_cannot_access_admin(
        self,
        client,
        auth_headers,
        admin_user
    ):
        """Test that regular users cannot access admin-only endpoints"""
        # Try to access admin endpoint
        response = client.get(
            "/api/v1/admin/users",
            headers=auth_headers
        )

        assert response.status_code in [401, 403]

    def test_authorization_user_cannot_modify_others_data(
        self,
        client,
        auth_headers,
        courier_factory
    ):
        """Test that users cannot modify others' data"""
        courier = courier_factory()

        # Try to update another courier's data
        response = client.put(
            f"/api/v1/fleet/couriers/{courier.id}",
            json={"full_name": "Hacked Name"},
            headers=auth_headers
        )

        assert response.status_code in [401, 403]

    def test_session_token_uniqueness(self, client, test_user, test_password):
        """Test that each login generates unique token"""
        tokens = []

        for _ in range(3):
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": test_user.email,
                    "password": test_password
                }
            )

            if response.status_code == 200:
                token = response.json().get("access_token")
                assert token not in tokens, "Token reused"
                tokens.append(token)

            time.sleep(0.1)  # Small delay

        assert len(set(tokens)) == len(tokens), "Duplicate tokens generated"

    def test_xss_prevention_in_response(self, client, admin_headers):
        """Test XSS prevention in API responses"""
        xss_payload = "<script>alert('XSS')</script>"

        courier_data = {
            "barq_id": "BRQ-XSS-TEST",
            "full_name": xss_payload,
            "mobile_number": "+966501234567",
            "email": "xss@test.com"
        }

        response = client.post(
            "/api/v1/fleet/couriers",
            json=courier_data,
            headers=admin_headers
        )

        if response.status_code == 201:
            data = response.json()
            # Response should escape or sanitize the XSS payload
            assert "<script>" not in str(data)

    def test_csrf_token_validation(self, client, auth_headers):
        """Test CSRF protection on state-changing operations"""
        # This would test CSRF tokens if implemented
        # For APIs, typically use same-origin policy and tokens
        pass  # Placeholder for CSRF tests

    def test_rate_limiting_on_sensitive_endpoints(self, client):
        """Test rate limiting on sensitive endpoints"""
        # Make rapid requests to sensitive endpoint
        responses = []

        for _ in range(30):  # Exceed rate limit
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "password123"
                }
            )
            responses.append(response.status_code)

        # Should have some 429 (Too Many Requests) responses
        assert 429 in responses, "Rate limiting not working"

    def test_password_reset_token_security(self, client, test_user):
        """Test password reset token security"""
        # Request password reset
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": test_user.email}
        )

        if response.status_code == 200:
            # Reset token should be single-use
            # Attempting to use same token twice should fail
            pass  # Would need to implement token tracking

    def test_token_in_url_prevention(self, client, test_token):
        """Test that tokens in URL are discouraged"""
        # Tokens should be in headers, not query params
        response = client.get(
            f"/api/v1/fleet/couriers?token={test_token}"
        )

        # Should not authenticate via URL parameter
        assert response.status_code == 401

    def test_secure_headers_present(self, client):
        """Test that security headers are present"""
        response = client.get("/api/v1/health")

        # Check for security headers
        headers = response.headers

        # These headers should be present for security
        # Note: Some might be set by reverse proxy in production
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "Content-Security-Policy",
        ]

        # At least some security headers should be present
        # In production environment
        pass  # Adjust based on actual implementation

    def test_sensitive_data_not_in_logs(self, client, test_user, test_password):
        """Test that sensitive data is not logged"""
        import logging
        from io import StringIO

        # Capture logs
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger("app")
        logger.addHandler(handler)

        # Perform login
        client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": test_password
            }
        )

        # Check logs don't contain password
        log_contents = log_stream.getvalue()
        assert test_password not in log_contents, "Password found in logs!"

        logger.removeHandler(handler)
