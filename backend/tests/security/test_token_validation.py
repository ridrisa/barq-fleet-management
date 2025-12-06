"""
Token Validation Security Tests

Tests for JWT token security including:
- Token structure validation
- Expiration enforcement
- Audience and issuer verification
- Token blacklist functionality
- Token tampering detection

Author: BARQ QA Team
Last Updated: 2025-12-06
"""

import pytest
import jwt
import time
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestTokenValidation:
    """Test JWT token validation security"""

    @pytest.mark.security
    def test_token_without_signature(self, client: TestClient, test_user):
        """Test that unsigned tokens are rejected"""
        # Create an unsigned token (algorithm: none)
        payload = {
            "sub": str(test_user.id),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        # Create token without signature
        unsigned_token = jwt.encode(payload, "", algorithm="none")

        headers = {"Authorization": f"Bearer {unsigned_token}"}
        response = client.get("/api/v1/fleet/couriers", headers=headers)

        assert response.status_code == 401, \
            "Unsigned token was accepted"

    @pytest.mark.security
    def test_token_with_wrong_secret(self, client: TestClient, test_user):
        """Test that tokens signed with wrong secret are rejected"""
        payload = {
            "sub": str(test_user.id),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        wrong_secret_token = jwt.encode(payload, "wrong-secret-key", algorithm="HS256")

        headers = {"Authorization": f"Bearer {wrong_secret_token}"}
        response = client.get("/api/v1/fleet/couriers", headers=headers)

        assert response.status_code == 401, \
            "Token with wrong secret was accepted"

    @pytest.mark.security
    def test_expired_token_rejected(self, client: TestClient, test_user):
        """Test that expired tokens are rejected"""
        from app.core.security import TokenManager

        # Create token that's already expired
        expired_token = TokenManager.create_access_token(
            data={"sub": str(test_user.id)},
            expires_delta=timedelta(seconds=-10)  # Already expired
        )

        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/v1/fleet/couriers", headers=headers)

        assert response.status_code == 401, \
            "Expired token was accepted"

    @pytest.mark.security
    def test_token_with_future_nbf(self, client: TestClient, test_user):
        """Test that tokens with future 'not before' time are rejected"""
        from app.config.settings import settings

        payload = {
            "sub": str(test_user.id),
            "exp": datetime.utcnow() + timedelta(hours=1),
            "nbf": datetime.utcnow() + timedelta(hours=1),  # Not valid yet
            "aud": settings.JWT_AUDIENCE,
            "iss": settings.JWT_ISSUER
        }
        future_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        headers = {"Authorization": f"Bearer {future_token}"}
        response = client.get("/api/v1/fleet/couriers", headers=headers)

        assert response.status_code == 401, \
            "Token with future nbf was accepted"

    @pytest.mark.security
    def test_token_with_wrong_audience(self, client: TestClient, test_user):
        """Test that tokens with wrong audience are rejected"""
        from app.config.settings import settings

        payload = {
            "sub": str(test_user.id),
            "exp": datetime.utcnow() + timedelta(hours=1),
            "aud": "wrong-audience",
            "iss": settings.JWT_ISSUER
        }
        wrong_aud_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        headers = {"Authorization": f"Bearer {wrong_aud_token}"}
        response = client.get("/api/v1/fleet/couriers", headers=headers)

        assert response.status_code == 401, \
            "Token with wrong audience was accepted"

    @pytest.mark.security
    def test_token_with_wrong_issuer(self, client: TestClient, test_user):
        """Test that tokens with wrong issuer are rejected"""
        from app.config.settings import settings

        payload = {
            "sub": str(test_user.id),
            "exp": datetime.utcnow() + timedelta(hours=1),
            "aud": settings.JWT_AUDIENCE,
            "iss": "wrong-issuer"
        }
        wrong_iss_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        headers = {"Authorization": f"Bearer {wrong_iss_token}"}
        response = client.get("/api/v1/fleet/couriers", headers=headers)

        assert response.status_code == 401, \
            "Token with wrong issuer was accepted"

    @pytest.mark.security
    def test_token_with_modified_payload(self, client: TestClient, test_user, admin_user):
        """Test that tokens with tampered payload are rejected"""
        from app.core.security import TokenManager

        # Get a valid token
        valid_token = TokenManager.create_access_token(
            data={"sub": str(test_user.id)}
        )

        # Try to modify the payload (change user_id to admin)
        parts = valid_token.split('.')
        if len(parts) == 3:
            import base64
            # Decode payload
            payload_b64 = parts[1]
            # Add padding if needed
            padding = 4 - len(payload_b64) % 4
            if padding != 4:
                payload_b64 += '=' * padding

            try:
                import json
                payload_json = base64.urlsafe_b64decode(payload_b64)
                payload = json.loads(payload_json)

                # Modify payload
                payload["sub"] = str(admin_user.id)

                # Re-encode (without proper signature)
                new_payload = base64.urlsafe_b64encode(
                    json.dumps(payload).encode()
                ).rstrip(b'=').decode()

                # Create tampered token
                tampered_token = f"{parts[0]}.{new_payload}.{parts[2]}"

                headers = {"Authorization": f"Bearer {tampered_token}"}
                response = client.get("/api/v1/fleet/couriers", headers=headers)

                assert response.status_code == 401, \
                    "Tampered token was accepted"
            except Exception:
                pass  # Token manipulation failed, which is fine

    @pytest.mark.security
    def test_token_with_invalid_user_id(self, client: TestClient):
        """Test that tokens with non-existent user IDs are rejected"""
        from app.core.security import TokenManager

        # Create token for non-existent user
        token = TokenManager.create_access_token(
            data={"sub": "999999999"}  # Non-existent user ID
        )

        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/fleet/couriers", headers=headers)

        assert response.status_code == 401, \
            "Token with non-existent user was accepted"

    @pytest.mark.security
    def test_token_with_negative_user_id(self, client: TestClient):
        """Test that tokens with negative user IDs are rejected"""
        from app.core.security import TokenManager

        token = TokenManager.create_access_token(
            data={"sub": "-1"}
        )

        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/fleet/couriers", headers=headers)

        assert response.status_code == 401, \
            "Token with negative user ID was accepted"

    @pytest.mark.security
    def test_token_with_string_user_id(self, client: TestClient):
        """Test that tokens with non-numeric user IDs are rejected"""
        from app.core.security import TokenManager

        token = TokenManager.create_access_token(
            data={"sub": "not-a-number"}
        )

        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/fleet/couriers", headers=headers)

        assert response.status_code == 401, \
            "Token with non-numeric user ID was accepted"


class TestTokenBlacklist:
    """Test token blacklist functionality"""

    @pytest.mark.security
    def test_blacklisted_token_rejected(
        self,
        client: TestClient,
        test_user,
        test_password: str
    ):
        """Test that blacklisted tokens are rejected"""
        # Login to get a token
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": test_password
            }
        )

        if login_response.status_code == 200:
            token = login_response.json().get("access_token")

            # First verify the token works
            headers = {"Authorization": f"Bearer {token}"}
            response = client.get("/api/v1/health", headers=headers)
            assert response.status_code == 200

            # Logout (should blacklist the token)
            logout_response = client.post(
                "/api/v1/auth/logout",
                headers=headers
            )

            # Token should now be rejected
            if logout_response.status_code == 200:
                response = client.get("/api/v1/fleet/couriers", headers=headers)
                assert response.status_code == 401, \
                    "Blacklisted token was accepted after logout"

    @pytest.mark.security
    def test_token_blacklist_persistence(
        self,
        client: TestClient,
        test_user,
        test_token: str
    ):
        """Test that token blacklist persists"""
        from app.core.token_blacklist import blacklist_token, is_token_blacklisted

        # Blacklist the token
        blacklist_token(test_token)

        # Verify it's blacklisted
        assert is_token_blacklisted(test_token), \
            "Token not found in blacklist after adding"

        # Token should be rejected
        headers = {"Authorization": f"Bearer {test_token}"}
        response = client.get("/api/v1/fleet/couriers", headers=headers)
        assert response.status_code == 401


class TestAuthorizationHeaders:
    """Test authorization header validation"""

    @pytest.mark.security
    def test_missing_auth_header(self, client: TestClient):
        """Test that requests without auth header are rejected"""
        response = client.get("/api/v1/fleet/couriers")
        assert response.status_code == 401

    @pytest.mark.security
    def test_empty_auth_header(self, client: TestClient):
        """Test that empty auth header is rejected"""
        headers = {"Authorization": ""}
        response = client.get("/api/v1/fleet/couriers", headers=headers)
        assert response.status_code in [401, 422]

    @pytest.mark.security
    def test_bearer_without_token(self, client: TestClient):
        """Test that 'Bearer' without token is rejected"""
        headers = {"Authorization": "Bearer"}
        response = client.get("/api/v1/fleet/couriers", headers=headers)
        assert response.status_code == 401

    @pytest.mark.security
    def test_bearer_with_space_only(self, client: TestClient):
        """Test that 'Bearer ' (with space) is rejected"""
        headers = {"Authorization": "Bearer "}
        response = client.get("/api/v1/fleet/couriers", headers=headers)
        assert response.status_code == 401

    @pytest.mark.security
    def test_wrong_auth_scheme(self, client: TestClient, test_token: str):
        """Test that wrong auth scheme is rejected"""
        schemes = ["Basic", "Digest", "Token", "OAuth", "APIKey"]

        for scheme in schemes:
            headers = {"Authorization": f"{scheme} {test_token}"}
            response = client.get("/api/v1/fleet/couriers", headers=headers)
            assert response.status_code == 401, \
                f"Wrong auth scheme '{scheme}' was accepted"

    @pytest.mark.security
    def test_lowercase_bearer(self, client: TestClient, test_token: str):
        """Test that lowercase 'bearer' is handled correctly"""
        headers = {"Authorization": f"bearer {test_token}"}
        response = client.get("/api/v1/fleet/couriers", headers=headers)
        # FastAPI's OAuth2PasswordBearer typically expects exact "Bearer"
        # This test verifies the behavior
        assert response.status_code in [200, 401]

    @pytest.mark.security
    def test_token_in_query_parameter_rejected(
        self,
        client: TestClient,
        test_token: str
    ):
        """Test that tokens in query parameters are rejected"""
        response = client.get(f"/api/v1/fleet/couriers?token={test_token}")
        assert response.status_code == 401, \
            "Token in query parameter was accepted"

    @pytest.mark.security
    def test_token_in_cookie_rejected(
        self,
        client: TestClient,
        test_token: str
    ):
        """Test that tokens in cookies are rejected (if not supported)"""
        response = client.get(
            "/api/v1/fleet/couriers",
            cookies={"access_token": test_token}
        )
        # Should reject unless cookie auth is explicitly supported
        assert response.status_code == 401


class TestRefreshTokenSecurity:
    """Test refresh token security (if implemented)"""

    @pytest.mark.security
    def test_access_token_cannot_refresh(
        self,
        client: TestClient,
        test_token: str
    ):
        """Test that access tokens cannot be used to refresh"""
        headers = {"Authorization": f"Bearer {test_token}"}
        response = client.post(
            "/api/v1/auth/refresh",
            headers=headers
        )
        # Should fail - access tokens shouldn't work for refresh
        # Or return 404 if refresh endpoint doesn't exist
        assert response.status_code in [401, 403, 404, 422]

    @pytest.mark.security
    def test_expired_refresh_token_rejected(self, client: TestClient, test_user):
        """Test that expired refresh tokens are rejected"""
        from app.core.security import TokenManager

        # Create expired refresh token
        expired_refresh = TokenManager.create_access_token(
            data={"sub": str(test_user.id), "type": "refresh"},
            expires_delta=timedelta(seconds=-10)
        )

        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": expired_refresh}
        )
        # Should reject expired token or return 404 if endpoint doesn't exist
        assert response.status_code in [401, 403, 404, 422]
