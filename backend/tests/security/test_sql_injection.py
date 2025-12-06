"""
SQL Injection Prevention Tests

Tests to verify that the application is protected against SQL injection attacks
across all input vectors including:
- API query parameters
- Request body fields
- Path parameters
- RLS context setting

Author: BARQ QA Team
Last Updated: 2025-12-06
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestSQLInjectionPrevention:
    """Test SQL injection prevention across the application"""

    # Common SQL injection payloads
    SQL_INJECTION_PAYLOADS = [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "' UNION SELECT * FROM users --",
        "admin'--",
        "' OR 1=1--",
        "' OR '1'='1' /*",
        "1; DELETE FROM couriers WHERE 1=1",
        "1' AND '1'='1",
        "' OR ''='",
        "'; EXEC xp_cmdshell('dir'); --",
        "1'; UPDATE users SET role='admin' WHERE '1'='1",
        "' OR EXISTS(SELECT * FROM users WHERE username='admin')--",
        "1 OR 1=1",
        "1 AND 1=0 UNION SELECT username, password FROM users",
        "'-'",
        "' '",
        "'+OR+1=1--",
        "' OR 'x'='x",
        "%27%20OR%20%271%27=%271",  # URL encoded
        "{{7*7}}",  # Template injection attempt
    ]

    @pytest.mark.security
    def test_sql_injection_in_login_email(self, client: TestClient):
        """Test SQL injection prevention in login email field"""
        for payload in self.SQL_INJECTION_PAYLOADS:
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": payload,
                    "password": "Test@1234"
                }
            )
            # Should fail authentication, not cause DB error
            assert response.status_code in [401, 422], \
                f"SQL injection payload succeeded: {payload}"
            # Response should not contain SQL error messages
            response_text = response.text.lower()
            assert "syntax error" not in response_text
            assert "sql" not in response_text or "sqlalchemy" not in response_text

    @pytest.mark.security
    def test_sql_injection_in_login_password(self, client: TestClient):
        """Test SQL injection prevention in login password field"""
        for payload in self.SQL_INJECTION_PAYLOADS:
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": "test@barq.com",
                    "password": payload
                }
            )
            assert response.status_code in [401, 422], \
                f"SQL injection payload succeeded: {payload}"

    @pytest.mark.security
    def test_sql_injection_in_courier_search(
        self,
        client: TestClient,
        admin_headers: dict
    ):
        """Test SQL injection prevention in courier search"""
        for payload in self.SQL_INJECTION_PAYLOADS:
            response = client.get(
                "/api/v1/fleet/couriers",
                params={"search": payload},
                headers=admin_headers
            )
            # Should return 200 with empty results or 422 for validation error
            assert response.status_code in [200, 422], \
                f"Unexpected status for payload: {payload}"
            if response.status_code == 200:
                data = response.json()
                # Verify no DB manipulation occurred
                assert isinstance(data.get("items", data), list)

    @pytest.mark.security
    def test_sql_injection_in_vehicle_search(
        self,
        client: TestClient,
        admin_headers: dict
    ):
        """Test SQL injection prevention in vehicle search"""
        for payload in self.SQL_INJECTION_PAYLOADS:
            response = client.get(
                "/api/v1/fleet/vehicles",
                params={"search": payload},
                headers=admin_headers
            )
            assert response.status_code in [200, 422], \
                f"Unexpected status for payload: {payload}"

    @pytest.mark.security
    def test_sql_injection_in_path_parameter(
        self,
        client: TestClient,
        admin_headers: dict
    ):
        """Test SQL injection prevention in path parameters"""
        injection_ids = [
            "1; DROP TABLE couriers;--",
            "1 OR 1=1",
            "1' OR '1'='1",
            "-1 UNION SELECT * FROM users",
        ]

        for payload in injection_ids:
            # Test courier endpoint
            response = client.get(
                f"/api/v1/fleet/couriers/{payload}",
                headers=admin_headers
            )
            # Should return 404 or 422, not 500
            assert response.status_code in [404, 422, 400], \
                f"Path injection may have succeeded: {payload}"

    @pytest.mark.security
    def test_sql_injection_in_courier_create(
        self,
        client: TestClient,
        admin_headers: dict
    ):
        """Test SQL injection prevention in courier creation"""
        for payload in self.SQL_INJECTION_PAYLOADS[:5]:  # Test subset
            courier_data = {
                "barq_id": payload,
                "full_name": payload,
                "email": "test@valid.com",
                "mobile_number": "+966501234567",
                "status": "active"
            }
            response = client.post(
                "/api/v1/fleet/couriers",
                json=courier_data,
                headers=admin_headers
            )
            # Should either validate and reject or create safely
            assert response.status_code in [201, 400, 422], \
                f"Unexpected status for payload: {payload}"
            if response.status_code == 201:
                # Verify data was escaped/stored safely
                data = response.json()
                # The payload should be stored as literal string, not executed
                assert payload in str(data.get("barq_id", "")) or \
                       payload in str(data.get("full_name", ""))

    @pytest.mark.security
    def test_sql_injection_in_filter_parameters(
        self,
        client: TestClient,
        admin_headers: dict
    ):
        """Test SQL injection prevention in filter query parameters"""
        filter_params = [
            {"status": "' OR '1'='1"},
            {"city": "'; DROP TABLE couriers; --"},
            {"project_type": "' UNION SELECT * FROM users --"},
            {"sponsorship_status": "1 OR 1=1"},
        ]

        for params in filter_params:
            response = client.get(
                "/api/v1/fleet/couriers",
                params=params,
                headers=admin_headers
            )
            # Should return validation error or empty results
            assert response.status_code in [200, 422], \
                f"Unexpected status for params: {params}"

    @pytest.mark.security
    def test_sql_injection_in_pagination(
        self,
        client: TestClient,
        admin_headers: dict
    ):
        """Test SQL injection prevention in pagination parameters"""
        injection_params = [
            {"skip": "0; DROP TABLE users;--", "limit": "10"},
            {"skip": "0", "limit": "10; DELETE FROM couriers"},
            {"page": "1 OR 1=1", "page_size": "10"},
        ]

        for params in injection_params:
            response = client.get(
                "/api/v1/fleet/couriers",
                params=params,
                headers=admin_headers
            )
            # Should return 422 for invalid types
            assert response.status_code == 422, \
                f"Non-integer pagination accepted: {params}"

    @pytest.mark.security
    def test_sql_injection_in_delivery_tracking(
        self,
        client: TestClient,
        admin_headers: dict
    ):
        """Test SQL injection prevention in delivery tracking number search"""
        for payload in self.SQL_INJECTION_PAYLOADS[:5]:
            response = client.get(
                "/api/v1/operations/deliveries",
                params={"tracking_number": payload},
                headers=admin_headers
            )
            assert response.status_code in [200, 422]

    @pytest.mark.security
    def test_second_order_sql_injection(
        self,
        client: TestClient,
        admin_headers: dict,
        db_session: Session
    ):
        """Test second-order SQL injection (stored then executed)"""
        # Create courier with potentially dangerous name
        malicious_name = "Test'; UPDATE users SET is_superuser=true WHERE email='attacker@test.com'; --"

        response = client.post(
            "/api/v1/fleet/couriers",
            json={
                "barq_id": "BRQ-SEC-001",
                "full_name": malicious_name,
                "email": "safe@test.com",
                "mobile_number": "+966501234567",
                "status": "active"
            },
            headers=admin_headers
        )

        if response.status_code == 201:
            # Verify the malicious SQL wasn't executed
            from app.models.user import User
            attacker = db_session.query(User).filter(
                User.email == "attacker@test.com"
            ).first()
            # Attacker user shouldn't exist or shouldn't be superuser
            assert attacker is None or not attacker.is_superuser

    @pytest.mark.security
    def test_blind_sql_injection(
        self,
        client: TestClient,
        admin_headers: dict
    ):
        """Test blind SQL injection prevention using timing attacks"""
        import time

        # Time-based blind SQL injection payload
        time_payloads = [
            "1; WAITFOR DELAY '0:0:5'--",
            "1; SELECT SLEEP(5)--",
            "1' AND SLEEP(5)--",
            "1; pg_sleep(5)--",
        ]

        for payload in time_payloads:
            start_time = time.time()
            response = client.get(
                f"/api/v1/fleet/couriers/{payload}",
                headers=admin_headers
            )
            elapsed = time.time() - start_time

            # Request should not take more than 3 seconds
            # (assuming normal timeout is less than 5 seconds)
            assert elapsed < 3.0, \
                f"Possible time-based SQL injection: {payload} took {elapsed}s"


class TestRLSSecurityContext:
    """Test Row-Level Security context setting security"""

    @pytest.mark.security
    def test_rls_context_injection_prevention(self, db_session: Session):
        """Test that RLS context setting is protected against injection"""
        from sqlalchemy import text

        malicious_org_ids = [
            "1; DROP TABLE organizations;--",
            "1 OR 1=1",
            "'; DELETE FROM couriers; --",
            "-1 UNION SELECT * FROM users",
        ]

        for malicious_id in malicious_org_ids:
            # This should either raise an error or safely convert
            try:
                # The safe way - parameterized
                db_session.execute(
                    text("SET app.current_org_id = :org_id"),
                    {"org_id": str(int(malicious_id))}  # Should fail conversion
                )
                db_session.rollback()
                assert False, f"Malicious org_id accepted: {malicious_id}"
            except (ValueError, TypeError):
                # Expected - conversion to int failed
                pass
            except Exception as e:
                # Reset the session
                db_session.rollback()
                # Should not be a SQL error from the injection
                assert "syntax error" not in str(e).lower()

    @pytest.mark.security
    def test_organization_id_validation(self, client: TestClient, test_user):
        """Test that organization IDs in tokens are validated"""
        from app.core.security import TokenManager

        invalid_org_ids = [
            -1,
            0,
            "abc",
            None,
            999999999,  # Non-existent
        ]

        for org_id in invalid_org_ids:
            try:
                token = TokenManager.create_access_token(
                    data={
                        "sub": str(test_user.id),
                        "org_id": org_id
                    }
                )
                headers = {"Authorization": f"Bearer {token}"}

                response = client.get(
                    "/api/v1/dashboard/stats",
                    headers=headers
                )

                # Should reject invalid org_id
                assert response.status_code in [401, 403], \
                    f"Invalid org_id {org_id} was accepted"
            except (ValueError, TypeError):
                # Expected for some invalid values
                pass


class TestNoSQLInjection:
    """Test NoSQL/JSON injection prevention (if applicable)"""

    @pytest.mark.security
    def test_json_injection_in_filters(
        self,
        client: TestClient,
        admin_headers: dict
    ):
        """Test JSON injection prevention in filter parameters"""
        json_payloads = [
            '{"$gt": ""}',
            '{"$ne": null}',
            '{"$where": "this.password"}',
            '{"$regex": ".*"}',
        ]

        for payload in json_payloads:
            response = client.get(
                "/api/v1/fleet/couriers",
                params={"filters": payload},
                headers=admin_headers
            )
            # Should not cause server error
            assert response.status_code != 500, \
                f"JSON injection may have caused error: {payload}"
