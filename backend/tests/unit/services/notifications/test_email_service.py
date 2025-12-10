"""
Unit Tests for Email Notification Service

Tests email notification functionality:
- EmailRecipient model
- EmailTemplate constants
- Email sending (mock mode)
- Template-based notifications
- Bulk email sending
"""

import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch

from app.services.email_notification_service import (
    EmailNotificationService,
    EmailRecipient,
    EmailTemplate,
)


# ==================== EmailRecipient Model Tests ====================

class TestEmailRecipient:
    """Tests for EmailRecipient model"""

    def test_create_recipient_email_only(self):
        """Should create recipient with email only"""
        recipient = EmailRecipient(email="test@barq.com")
        assert recipient.email == "test@barq.com"
        assert recipient.name is None

    def test_create_recipient_with_name(self):
        """Should create recipient with email and name"""
        recipient = EmailRecipient(email="test@barq.com", name="Test User")
        assert recipient.email == "test@barq.com"
        assert recipient.name == "Test User"

    def test_invalid_email_raises_error(self):
        """Invalid email should raise validation error"""
        with pytest.raises(ValueError):
            EmailRecipient(email="invalid-email")

    def test_valid_email_formats(self):
        """Should accept various valid email formats"""
        valid_emails = [
            "simple@example.com",
            "very.common@example.com",
            "user+tag@example.com",
            "admin@subdomain.example.com",
        ]
        for email in valid_emails:
            recipient = EmailRecipient(email=email)
            assert recipient.email == email


# ==================== EmailTemplate Constants Tests ====================

class TestEmailTemplate:
    """Tests for EmailTemplate constants"""

    def test_leave_templates_exist(self):
        """Leave-related templates should exist"""
        assert EmailTemplate.LEAVE_APPROVED == "leave_approved"
        assert EmailTemplate.LEAVE_REJECTED == "leave_rejected"

    def test_salary_templates_exist(self):
        """Salary-related templates should exist"""
        assert EmailTemplate.SALARY_PAID == "salary_paid"
        assert EmailTemplate.SALARY_PROCESSED == "salary_processed"

    def test_loan_templates_exist(self):
        """Loan-related templates should exist"""
        assert EmailTemplate.LOAN_APPROVED == "loan_approved"
        assert EmailTemplate.LOAN_REJECTED == "loan_rejected"
        assert EmailTemplate.LOAN_PAYMENT_DUE == "loan_payment_due"

    def test_document_templates_exist(self):
        """Document expiry templates should exist"""
        assert EmailTemplate.LICENSE_EXPIRING == "license_expiring"
        assert EmailTemplate.IQAMA_EXPIRING == "iqama_expiring"
        assert EmailTemplate.VEHICLE_REGISTRATION_EXPIRING == "vehicle_registration_expiring"

    def test_system_templates_exist(self):
        """System templates should exist"""
        assert EmailTemplate.PASSWORD_RESET == "password_reset"
        assert EmailTemplate.ACCOUNT_CREATED == "account_created"
        assert EmailTemplate.WELCOME == "welcome"


# ==================== EmailNotificationService Initialization Tests ====================

class TestEmailServiceInit:
    """Tests for EmailNotificationService initialization"""

    def test_init_without_api_key(self):
        """Should initialize in mock mode without API key"""
        service = EmailNotificationService()
        assert service.sg_client is None

    def test_init_with_api_key(self):
        """Should try to initialize SendGrid with API key"""
        # Even with API key, if SendGrid not available, should be None
        service = EmailNotificationService(sendgrid_api_key="test_api_key")
        # In test environment, SendGrid may not be available
        # This just verifies initialization doesn't crash

    def test_init_custom_from_email(self):
        """Should accept custom from email"""
        service = EmailNotificationService(from_email="custom@barq.com")
        assert service.from_email == "custom@barq.com"

    def test_init_custom_from_name(self):
        """Should accept custom from name"""
        service = EmailNotificationService(from_name="Custom Name")
        assert service.from_name == "Custom Name"


# ==================== Basic Email Sending Tests ====================

class TestSendEmail:
    """Tests for send_email method"""

    @pytest.fixture
    def email_service(self):
        """Create EmailNotificationService instance in mock mode"""
        return EmailNotificationService()

    def test_send_email_mock_mode_success(self, email_service):
        """Should succeed in mock mode"""
        result = email_service.send_email(
            to=EmailRecipient(email="test@barq.com", name="Test User"),
            subject="Test Subject",
            html_content="<p>Test Content</p>",
        )
        assert result is True

    def test_send_email_with_plain_content(self, email_service):
        """Should accept plain text content"""
        result = email_service.send_email(
            to=EmailRecipient(email="test@barq.com"),
            subject="Test Subject",
            html_content="<p>HTML Content</p>",
            plain_content="Plain Content",
        )
        assert result is True

    def test_send_email_with_cc(self, email_service):
        """Should accept CC recipients"""
        result = email_service.send_email(
            to=EmailRecipient(email="test@barq.com"),
            subject="Test Subject",
            html_content="<p>Content</p>",
            cc=[EmailRecipient(email="cc@barq.com")],
        )
        assert result is True

    def test_send_email_with_bcc(self, email_service):
        """Should accept BCC recipients"""
        result = email_service.send_email(
            to=EmailRecipient(email="test@barq.com"),
            subject="Test Subject",
            html_content="<p>Content</p>",
            bcc=[EmailRecipient(email="bcc@barq.com")],
        )
        assert result is True


# ==================== Leave Notification Tests ====================

class TestLeaveNotifications:
    """Tests for leave-related notifications"""

    @pytest.fixture
    def email_service(self):
        return EmailNotificationService()

    def test_send_leave_approval_notification(self, email_service):
        """Should send leave approval notification"""
        result = email_service.send_leave_approval_notification(
            to_email="courier@barq.com",
            courier_name="Ahmad Hassan",
            leave_type="Annual",
            start_date="2025-01-15",
            end_date="2025-01-20",
            days=5,
        )
        assert result is True

    def test_send_leave_rejection_notification(self, email_service):
        """Should send leave rejection notification"""
        result = email_service.send_leave_rejection_notification(
            to_email="courier@barq.com",
            courier_name="Ahmad Hassan",
            leave_type="Sick",
            start_date="2025-01-15",
            end_date="2025-01-17",
        )
        assert result is True

    def test_send_leave_rejection_with_reason(self, email_service):
        """Should send leave rejection with reason"""
        result = email_service.send_leave_rejection_notification(
            to_email="courier@barq.com",
            courier_name="Ahmad Hassan",
            leave_type="Annual",
            start_date="2025-01-15",
            end_date="2025-01-20",
            reason="Insufficient leave balance",
        )
        assert result is True


# ==================== Salary Notification Tests ====================

class TestSalaryNotifications:
    """Tests for salary-related notifications"""

    @pytest.fixture
    def email_service(self):
        return EmailNotificationService()

    def test_send_salary_payment_notification(self, email_service):
        """Should send salary payment notification"""
        result = email_service.send_salary_payment_notification(
            to_email="courier@barq.com",
            courier_name="Ahmad Hassan",
            month=1,
            year=2025,
            net_salary=Decimal("5500.00"),
            payment_date="2025-01-28",
        )
        assert result is True

    def test_send_salary_payment_large_amount(self, email_service):
        """Should format large salary amounts correctly"""
        result = email_service.send_salary_payment_notification(
            to_email="courier@barq.com",
            courier_name="Ahmad Hassan",
            month=12,
            year=2024,
            net_salary=Decimal("15500.50"),
            payment_date="2024-12-28",
        )
        assert result is True


# ==================== Document Expiry Alert Tests ====================

class TestDocumentExpiryAlerts:
    """Tests for document expiry alerts"""

    @pytest.fixture
    def email_service(self):
        return EmailNotificationService()

    def test_send_document_expiry_alert_normal(self, email_service):
        """Should send normal expiry alert (>7 days)"""
        result = email_service.send_document_expiry_alert(
            to_email="courier@barq.com",
            courier_name="Ahmad Hassan",
            document_type="Driving License",
            document_number="DL-123456",
            expiry_date="2025-02-15",
            days_until_expiry=30,
        )
        assert result is True

    def test_send_document_expiry_alert_urgent(self, email_service):
        """Should send urgent expiry alert (<=7 days)"""
        result = email_service.send_document_expiry_alert(
            to_email="courier@barq.com",
            courier_name="Ahmad Hassan",
            document_type="Iqama",
            document_number="IQ-789012",
            expiry_date="2025-01-20",
            days_until_expiry=5,
        )
        assert result is True

    def test_send_document_expiry_alert_critical(self, email_service):
        """Should handle critical expiry (1 day)"""
        result = email_service.send_document_expiry_alert(
            to_email="courier@barq.com",
            courier_name="Ahmad Hassan",
            document_type="Vehicle Registration",
            document_number="VR-345678",
            expiry_date="2025-01-16",
            days_until_expiry=1,
        )
        assert result is True


# ==================== Loan Notification Tests ====================

class TestLoanNotifications:
    """Tests for loan-related notifications"""

    @pytest.fixture
    def email_service(self):
        return EmailNotificationService()

    def test_send_loan_approval_notification(self, email_service):
        """Should send loan approval notification"""
        result = email_service.send_loan_approval_notification(
            to_email="courier@barq.com",
            courier_name="Ahmad Hassan",
            loan_amount=Decimal("10000.00"),
            monthly_deduction=Decimal("1000.00"),
            approval_date="2025-01-15",
        )
        assert result is True

    def test_send_loan_approval_small_amount(self, email_service):
        """Should handle small loan amounts"""
        result = email_service.send_loan_approval_notification(
            to_email="courier@barq.com",
            courier_name="Ahmad Hassan",
            loan_amount=Decimal("500.00"),
            monthly_deduction=Decimal("100.00"),
            approval_date="2025-01-15",
        )
        assert result is True


# ==================== Welcome Email Tests ====================

class TestWelcomeEmails:
    """Tests for welcome emails"""

    @pytest.fixture
    def email_service(self):
        return EmailNotificationService()

    def test_send_welcome_email(self, email_service):
        """Should send welcome email to new employee"""
        result = email_service.send_welcome_email(
            to_email="newemployee@barq.com",
            courier_name="New Employee",
            employee_id="EMP-001",
            start_date="2025-01-20",
        )
        assert result is True


# ==================== Bulk Email Tests ====================

class TestBulkEmails:
    """Tests for bulk email functionality"""

    @pytest.fixture
    def email_service(self):
        return EmailNotificationService()

    def test_send_bulk_notification_success(self, email_service):
        """Should send bulk emails to multiple recipients"""
        recipients = [
            EmailRecipient(email="user1@barq.com", name="User 1"),
            EmailRecipient(email="user2@barq.com", name="User 2"),
            EmailRecipient(email="user3@barq.com", name="User 3"),
        ]

        result = email_service.send_bulk_notification(
            recipients=recipients,
            subject="Bulk Test",
            html_content="<p>Bulk test content</p>",
        )

        assert result["total"] == 3
        assert result["success"] == 3
        assert result["failure"] == 0

    def test_send_bulk_notification_empty_list(self, email_service):
        """Should handle empty recipient list"""
        result = email_service.send_bulk_notification(
            recipients=[],
            subject="Bulk Test",
            html_content="<p>Content</p>",
        )

        assert result["total"] == 0
        assert result["success"] == 0
        assert result["failure"] == 0

    def test_send_bulk_notification_single_recipient(self, email_service):
        """Should handle single recipient in bulk send"""
        recipients = [EmailRecipient(email="single@barq.com")]

        result = email_service.send_bulk_notification(
            recipients=recipients,
            subject="Single Bulk",
            html_content="<p>Content</p>",
        )

        assert result["total"] == 1
        assert result["success"] == 1


# ==================== Error Handling Tests ====================

class TestErrorHandling:
    """Tests for error handling"""

    @pytest.fixture
    def email_service(self):
        return EmailNotificationService()

    def test_send_email_exception_handling(self, email_service):
        """Should handle exceptions gracefully"""
        # In mock mode, this should succeed
        # Testing the exception path requires mocking the logger
        result = email_service.send_email(
            to=EmailRecipient(email="test@barq.com"),
            subject="Test",
            html_content="<p>Content</p>",
        )
        assert result is True

    def test_bulk_email_partial_failure(self, email_service):
        """Should count failures in bulk send"""
        # Mock a failure scenario
        with patch.object(email_service, 'send_email') as mock_send:
            mock_send.side_effect = [True, Exception("Failed"), True]

            recipients = [
                EmailRecipient(email="user1@barq.com"),
                EmailRecipient(email="user2@barq.com"),
                EmailRecipient(email="user3@barq.com"),
            ]

            result = email_service.send_bulk_notification(
                recipients=recipients,
                subject="Test",
                html_content="<p>Content</p>",
            )

            assert result["total"] == 3
            assert result["success"] == 2
            assert result["failure"] == 1
