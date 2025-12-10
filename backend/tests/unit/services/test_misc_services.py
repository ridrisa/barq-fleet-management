"""
Unit Tests for Miscellaneous Services

Tests cover:
- Password Reset Service
- Audit Log Service
- Role Service
- Data Integrity Service
- Email Notification Service
- SMS Notification Service

Author: BARQ QA Team
Last Updated: 2025-12-10
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from app.services.password_reset_service import PasswordResetService
from app.services.audit_log_service import AuditLogService
from app.services.role_service import RoleService
from app.services.data_integrity_service import DataIntegrityService
from app.services.email_notification_service import EmailNotificationService
from app.services.sms_notification_service import SMSNotificationService


# ==================== PASSWORD RESET SERVICE TESTS ====================

class TestPasswordResetService:
    """Test Password Reset Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create PasswordResetService instance"""
        return PasswordResetService(db_session)

    def test_initiate_password_reset(self, service, db_session, test_user):
        """Test initiating password reset"""
        result = service.initiate_reset(email=test_user.email)

        assert result is not None
        assert "token" in result or "reset_initiated" in result

    def test_initiate_reset_nonexistent_email(self, service, db_session):
        """Test initiating reset for nonexistent email"""
        result = service.initiate_reset(email="nonexistent@test.com")

        # Should not reveal if email exists
        assert result is not None

    def test_validate_reset_token(self, service, db_session, test_user):
        """Test validating reset token"""
        # First initiate reset to get token
        initiation = service.initiate_reset(email=test_user.email)

        if "token" in initiation:
            is_valid = service.validate_token(token=initiation["token"])
            assert is_valid is True

    def test_validate_expired_token(self, service, db_session):
        """Test validating expired token"""
        is_valid = service.validate_token(token="expired_token_123")

        assert is_valid is False

    def test_complete_password_reset(self, service, db_session, test_user):
        """Test completing password reset"""
        # First initiate reset
        initiation = service.initiate_reset(email=test_user.email)

        if "token" in initiation:
            result = service.complete_reset(
                token=initiation["token"],
                new_password="NewSecurePassword123!"
            )

            assert result is True

    def test_complete_reset_with_invalid_token(self, service, db_session):
        """Test completing reset with invalid token"""
        result = service.complete_reset(
            token="invalid_token",
            new_password="NewPassword123!"
        )

        assert result is False


# ==================== AUDIT LOG SERVICE TESTS ====================

class TestAuditLogService:
    """Test Audit Log Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create AuditLogService instance"""
        return AuditLogService(db_session)

    def test_log_action(self, service, db_session, test_user):
        """Test logging an action"""
        result = service.log_action(
            user_id=test_user.id,
            action="CREATE",
            entity_type="courier",
            entity_id=1,
            details={"field": "status", "old_value": None, "new_value": "active"}
        )

        assert result is not None

    def test_log_login(self, service, db_session, test_user):
        """Test logging a login event"""
        result = service.log_login(
            user_id=test_user.id,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            success=True
        )

        assert result is not None

    def test_log_failed_login(self, service, db_session):
        """Test logging a failed login attempt"""
        result = service.log_login(
            email="test@example.com",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            success=False
        )

        assert result is not None

    def test_get_logs_by_user(self, service, db_session, test_user):
        """Test getting audit logs by user"""
        # First log some actions
        service.log_action(
            user_id=test_user.id,
            action="UPDATE",
            entity_type="delivery",
            entity_id=1
        )

        result = service.get_by_user(user_id=test_user.id)

        assert isinstance(result, list)

    def test_get_logs_by_entity(self, service, db_session, test_user):
        """Test getting audit logs by entity"""
        service.log_action(
            user_id=test_user.id,
            action="CREATE",
            entity_type="courier",
            entity_id=123
        )

        result = service.get_by_entity(
            entity_type="courier",
            entity_id=123
        )

        assert isinstance(result, list)

    def test_get_logs_by_date_range(self, service, db_session):
        """Test getting audit logs by date range"""
        result = service.get_by_date_range(
            start_date=date.today() - timedelta(days=7),
            end_date=date.today()
        )

        assert isinstance(result, list)

    def test_get_logs_by_action_type(self, service, db_session, test_user):
        """Test getting audit logs by action type"""
        service.log_action(
            user_id=test_user.id,
            action="DELETE",
            entity_type="vehicle",
            entity_id=1
        )

        result = service.get_by_action(action="DELETE")

        assert all(log.action == "DELETE" for log in result)


# ==================== ROLE SERVICE TESTS ====================

class TestRoleService:
    """Test Role Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create RoleService instance"""
        from app.models.role import Role
        return RoleService(Role)

    def test_create_role(self, service, db_session, test_organization):
        """Test creating a role"""
        from app.schemas.role import RoleCreate

        role_data = RoleCreate(
            name="Fleet Manager",
            description="Manages fleet operations",
            permissions=["view_couriers", "manage_vehicles", "view_reports"],
            organization_id=test_organization.id
        )

        role = service.create(db_session, obj_in=role_data)

        assert role is not None
        assert role.name == "Fleet Manager"

    def test_get_role_by_name(self, service, db_session, test_organization):
        """Test getting role by name"""
        from app.models.role import Role

        role = Role(name="Test Role", organization_id=test_organization.id)
        db_session.add(role)
        db_session.commit()

        result = service.get_by_name(db_session, name="Test Role")

        assert result is not None
        assert result.name == "Test Role"

    def test_get_all_roles(self, service, db_session, test_organization):
        """Test getting all roles"""
        from app.models.role import Role

        role1 = Role(name="Role 1", organization_id=test_organization.id)
        role2 = Role(name="Role 2", organization_id=test_organization.id)
        db_session.add_all([role1, role2])
        db_session.commit()

        result = service.get_multi(db_session)

        assert len(result) >= 2

    def test_update_role_permissions(self, service, db_session, test_organization):
        """Test updating role permissions"""
        from app.models.role import Role

        role = Role(
            name="Updatable Role",
            permissions=["read"],
            organization_id=test_organization.id
        )
        db_session.add(role)
        db_session.commit()

        result = service.update_permissions(
            db_session,
            role_id=role.id,
            permissions=["read", "write", "delete"]
        )

        assert "write" in result.permissions
        assert "delete" in result.permissions

    def test_assign_role_to_user(self, service, db_session, test_user, test_organization):
        """Test assigning role to user"""
        from app.models.role import Role

        role = Role(name="Assignable Role", organization_id=test_organization.id)
        db_session.add(role)
        db_session.commit()

        result = service.assign_to_user(
            db_session,
            role_id=role.id,
            user_id=test_user.id
        )

        assert result is not None


# ==================== DATA INTEGRITY SERVICE TESTS ====================

class TestDataIntegrityService:
    """Test Data Integrity Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create DataIntegrityService instance"""
        return DataIntegrityService(db_session)

    def test_check_orphan_records(self, service, db_session):
        """Test checking for orphan records"""
        result = service.check_orphans()

        assert "orphan_records" in result
        assert "tables_checked" in result

    def test_check_referential_integrity(self, service, db_session):
        """Test checking referential integrity"""
        result = service.check_referential_integrity()

        assert "violations" in result
        assert "is_valid" in result

    def test_check_duplicate_records(self, service, db_session):
        """Test checking for duplicate records"""
        result = service.check_duplicates()

        assert "duplicate_count" in result
        assert "tables_checked" in result

    def test_run_full_integrity_check(self, service, db_session):
        """Test running full integrity check"""
        result = service.run_full_check()

        assert "orphans" in result
        assert "duplicates" in result
        assert "referential_integrity" in result
        assert "overall_status" in result


# ==================== EMAIL NOTIFICATION SERVICE TESTS ====================

class TestEmailNotificationService:
    """Test Email Notification Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create EmailNotificationService instance"""
        return EmailNotificationService()

    @patch("app.services.email_notification_service.send_email")
    def test_send_welcome_email(self, mock_send, service, test_user):
        """Test sending welcome email"""
        mock_send.return_value = True

        result = service.send_welcome_email(
            to_email=test_user.email,
            user_name=test_user.full_name
        )

        assert result is True
        mock_send.assert_called_once()

    @patch("app.services.email_notification_service.send_email")
    def test_send_password_reset_email(self, mock_send, service, test_user):
        """Test sending password reset email"""
        mock_send.return_value = True

        result = service.send_password_reset_email(
            to_email=test_user.email,
            reset_link="https://example.com/reset?token=abc123"
        )

        assert result is True

    @patch("app.services.email_notification_service.send_email")
    def test_send_leave_approval_notification(self, mock_send, service, test_user):
        """Test sending leave approval notification"""
        mock_send.return_value = True

        result = service.send_leave_notification(
            to_email=test_user.email,
            leave_type="Annual",
            status="approved",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5)
        )

        assert result is True

    @patch("app.services.email_notification_service.send_email")
    def test_send_salary_slip_email(self, mock_send, service, test_user):
        """Test sending salary slip email"""
        mock_send.return_value = True

        result = service.send_salary_slip_email(
            to_email=test_user.email,
            month="January",
            year=2025,
            attachment=b"PDF_CONTENT"
        )

        assert result is True

    @patch("app.services.email_notification_service.send_email")
    def test_send_bulk_emails(self, mock_send, service):
        """Test sending bulk emails"""
        mock_send.return_value = True

        recipients = ["user1@test.com", "user2@test.com", "user3@test.com"]
        result = service.send_bulk(
            to_emails=recipients,
            subject="Announcement",
            body="Important update"
        )

        assert result["sent"] == 3


# ==================== SMS NOTIFICATION SERVICE TESTS ====================

class TestSMSNotificationService:
    """Test SMS Notification Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create SMSNotificationService instance"""
        return SMSNotificationService()

    @patch("app.services.sms_notification_service.send_sms")
    def test_send_delivery_notification(self, mock_send, service):
        """Test sending delivery notification SMS"""
        mock_send.return_value = True

        result = service.send_delivery_notification(
            phone_number="+966501234567",
            tracking_number="TRK-001",
            status="Out for delivery"
        )

        assert result is True

    @patch("app.services.sms_notification_service.send_sms")
    def test_send_otp(self, mock_send, service):
        """Test sending OTP SMS"""
        mock_send.return_value = True

        result = service.send_otp(
            phone_number="+966501234567",
            otp_code="123456"
        )

        assert result is True

    @patch("app.services.sms_notification_service.send_sms")
    def test_send_alert(self, mock_send, service):
        """Test sending alert SMS"""
        mock_send.return_value = True

        result = service.send_alert(
            phone_number="+966501234567",
            message="Your document is expiring soon"
        )

        assert result is True

    @patch("app.services.sms_notification_service.send_sms")
    def test_send_sms_failure_handling(self, mock_send, service):
        """Test SMS failure handling"""
        mock_send.side_effect = Exception("SMS service unavailable")

        result = service.send_otp(
            phone_number="+966501234567",
            otp_code="123456"
        )

        # Should handle failure gracefully
        assert result is False or result is None

    @patch("app.services.sms_notification_service.send_sms")
    def test_send_bulk_sms(self, mock_send, service):
        """Test sending bulk SMS"""
        mock_send.return_value = True

        recipients = ["+966501234567", "+966507654321", "+966509876543"]
        result = service.send_bulk(
            phone_numbers=recipients,
            message="Monthly update"
        )

        assert result["sent"] == 3
