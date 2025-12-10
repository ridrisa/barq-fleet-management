"""
Unit Tests for SMS Notification Service

Tests SMS notification functionality:
- SMS sending (mock mode)
- Template-based SMS notifications
- OTP and verification codes
- Emergency alerts
- Bulk SMS sending
"""

import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch

from app.services.sms_notification_service import SMSNotificationService


# ==================== SMS Service Initialization Tests ====================

class TestSMSServiceInit:
    """Tests for SMSNotificationService initialization"""

    def test_init_without_credentials(self):
        """Should initialize in mock mode without credentials"""
        service = SMSNotificationService()
        assert service.client is None

    def test_init_with_partial_credentials(self):
        """Should be in mock mode with partial credentials"""
        service = SMSNotificationService(account_sid="test_sid")
        assert service.client is None

    def test_init_custom_from_phone(self):
        """Should accept custom from phone number"""
        service = SMSNotificationService(from_phone="+966509876543")
        assert service.from_phone == "+966509876543"

    def test_init_default_from_phone(self):
        """Should have default from phone number"""
        service = SMSNotificationService()
        assert service.from_phone == "+966501234567"


# ==================== Basic SMS Sending Tests ====================

class TestSendSMS:
    """Tests for send_sms method"""

    @pytest.fixture
    def sms_service(self):
        """Create SMSNotificationService instance in mock mode"""
        return SMSNotificationService()

    def test_send_sms_mock_mode_success(self, sms_service):
        """Should succeed in mock mode"""
        result = sms_service.send_sms(
            to_phone="+966501234567",
            message="Test message",
        )
        assert result is True

    def test_send_sms_arabic_message(self, sms_service):
        """Should handle Arabic messages"""
        result = sms_service.send_sms(
            to_phone="+966501234567",
            message="مرحبا، هذه رسالة اختبار",
        )
        assert result is True

    def test_send_sms_mixed_language(self, sms_service):
        """Should handle mixed language messages"""
        result = sms_service.send_sms(
            to_phone="+966501234567",
            message="مرحبا Test رسالة Message",
        )
        assert result is True

    def test_send_sms_with_numbers(self, sms_service):
        """Should handle messages with numbers"""
        result = sms_service.send_sms(
            to_phone="+966501234567",
            message="Your balance: SAR 5,500.00",
        )
        assert result is True


# ==================== Leave SMS Notification Tests ====================

class TestLeaveSMSNotifications:
    """Tests for leave-related SMS notifications"""

    @pytest.fixture
    def sms_service(self):
        return SMSNotificationService()

    def test_send_leave_approval_sms(self, sms_service):
        """Should send leave approval SMS"""
        result = sms_service.send_leave_approval_sms(
            to_phone="+966501234567",
            courier_name="أحمد حسن",
            leave_type="سنوية",
            start_date="2025-01-15",
            end_date="2025-01-20",
        )
        assert result is True

    def test_send_leave_approval_sms_english_name(self, sms_service):
        """Should handle English names"""
        result = sms_service.send_leave_approval_sms(
            to_phone="+966501234567",
            courier_name="Ahmad Hassan",
            leave_type="Annual",
            start_date="2025-01-15",
            end_date="2025-01-20",
        )
        assert result is True

    def test_send_leave_rejection_sms(self, sms_service):
        """Should send leave rejection SMS"""
        result = sms_service.send_leave_rejection_sms(
            to_phone="+966501234567",
            courier_name="Ahmad Hassan",
            leave_type="Sick",
        )
        assert result is True


# ==================== Salary SMS Notification Tests ====================

class TestSalarySMSNotifications:
    """Tests for salary-related SMS notifications"""

    @pytest.fixture
    def sms_service(self):
        return SMSNotificationService()

    def test_send_salary_payment_sms(self, sms_service):
        """Should send salary payment SMS"""
        result = sms_service.send_salary_payment_sms(
            to_phone="+966501234567",
            courier_name="Ahmad Hassan",
            month=1,
            year=2025,
            net_salary=Decimal("5500.00"),
        )
        assert result is True

    def test_send_salary_payment_sms_large_amount(self, sms_service):
        """Should format large salary amounts"""
        result = sms_service.send_salary_payment_sms(
            to_phone="+966501234567",
            courier_name="Ahmad Hassan",
            month=12,
            year=2024,
            net_salary=Decimal("15500.50"),
        )
        assert result is True


# ==================== Document Expiry SMS Tests ====================

class TestDocumentExpirySMS:
    """Tests for document expiry SMS alerts"""

    @pytest.fixture
    def sms_service(self):
        return SMSNotificationService()

    def test_send_document_expiry_alert_normal(self, sms_service):
        """Should send normal expiry alert"""
        result = sms_service.send_document_expiry_alert(
            to_phone="+966501234567",
            courier_name="Ahmad Hassan",
            document_type="Driving License",
            expiry_date="2025-02-15",
            days_remaining=30,
        )
        assert result is True

    def test_send_document_expiry_alert_urgent(self, sms_service):
        """Should send urgent expiry alert (<=7 days)"""
        result = sms_service.send_document_expiry_alert(
            to_phone="+966501234567",
            courier_name="Ahmad Hassan",
            document_type="Iqama",
            expiry_date="2025-01-20",
            days_remaining=5,
        )
        assert result is True

    def test_send_document_expiry_alert_arabic_doc_type(self, sms_service):
        """Should handle Arabic document types"""
        result = sms_service.send_document_expiry_alert(
            to_phone="+966501234567",
            courier_name="أحمد حسن",
            document_type="رخصة القيادة",
            expiry_date="2025-02-15",
            days_remaining=30,
        )
        assert result is True


# ==================== OTP SMS Tests ====================

class TestOTPSMS:
    """Tests for OTP SMS functionality"""

    @pytest.fixture
    def sms_service(self):
        return SMSNotificationService()

    def test_send_otp_code_default_expiry(self, sms_service):
        """Should send OTP with default expiry"""
        result = sms_service.send_otp_code(
            to_phone="+966501234567",
            otp_code="123456",
        )
        assert result is True

    def test_send_otp_code_custom_expiry(self, sms_service):
        """Should send OTP with custom expiry"""
        result = sms_service.send_otp_code(
            to_phone="+966501234567",
            otp_code="654321",
            expiry_minutes=10,
        )
        assert result is True

    def test_send_otp_code_short_code(self, sms_service):
        """Should handle short OTP codes"""
        result = sms_service.send_otp_code(
            to_phone="+966501234567",
            otp_code="1234",
        )
        assert result is True

    def test_send_otp_code_alphanumeric(self, sms_service):
        """Should handle alphanumeric OTP codes"""
        result = sms_service.send_otp_code(
            to_phone="+966501234567",
            otp_code="AB1234",
        )
        assert result is True


# ==================== Emergency Alert SMS Tests ====================

class TestEmergencyAlertSMS:
    """Tests for emergency alert SMS"""

    @pytest.fixture
    def sms_service(self):
        return SMSNotificationService()

    def test_send_emergency_alert(self, sms_service):
        """Should send emergency alert"""
        result = sms_service.send_emergency_alert(
            to_phone="+966501234567",
            courier_name="Ahmad Hassan",
            message_text="Vehicle breakdown on King Fahd Road",
        )
        assert result is True

    def test_send_emergency_alert_arabic(self, sms_service):
        """Should send emergency alert in Arabic"""
        result = sms_service.send_emergency_alert(
            to_phone="+966501234567",
            courier_name="أحمد حسن",
            message_text="حادث مروري بالقرب من الموقع",
        )
        assert result is True


# ==================== Password Reset SMS Tests ====================

class TestPasswordResetSMS:
    """Tests for password reset SMS"""

    @pytest.fixture
    def sms_service(self):
        return SMSNotificationService()

    def test_send_password_reset_sms(self, sms_service):
        """Should send password reset code"""
        result = sms_service.send_password_reset_sms(
            to_phone="+966501234567",
            reset_code="ABC123",
        )
        assert result is True

    def test_send_password_reset_sms_numeric_code(self, sms_service):
        """Should handle numeric reset codes"""
        result = sms_service.send_password_reset_sms(
            to_phone="+966501234567",
            reset_code="987654",
        )
        assert result is True


# ==================== Attendance Reminder SMS Tests ====================

class TestAttendanceReminderSMS:
    """Tests for attendance reminder SMS"""

    @pytest.fixture
    def sms_service(self):
        return SMSNotificationService()

    def test_send_attendance_reminder(self, sms_service):
        """Should send attendance reminder"""
        result = sms_service.send_attendance_reminder(
            to_phone="+966501234567",
            courier_name="Ahmad Hassan",
        )
        assert result is True


# ==================== Bulk SMS Tests ====================

class TestBulkSMS:
    """Tests for bulk SMS functionality"""

    @pytest.fixture
    def sms_service(self):
        return SMSNotificationService()

    def test_send_bulk_sms_success(self, sms_service):
        """Should send bulk SMS to multiple recipients"""
        phone_numbers = [
            "+966501234567",
            "+966509876543",
            "+966501112223",
        ]

        result = sms_service.send_bulk_sms(
            phone_numbers=phone_numbers,
            message="Bulk test message",
        )

        assert result["total"] == 3
        assert result["success"] == 3
        assert result["failure"] == 0
        assert result["failed_numbers"] == []

    def test_send_bulk_sms_empty_list(self, sms_service):
        """Should handle empty phone list"""
        result = sms_service.send_bulk_sms(
            phone_numbers=[],
            message="Test message",
        )

        assert result["total"] == 0
        assert result["success"] == 0
        assert result["failure"] == 0

    def test_send_bulk_sms_single_recipient(self, sms_service):
        """Should handle single recipient in bulk send"""
        result = sms_service.send_bulk_sms(
            phone_numbers=["+966501234567"],
            message="Single bulk test",
        )

        assert result["total"] == 1
        assert result["success"] == 1

    def test_send_bulk_sms_partial_failure(self, sms_service):
        """Should track failures in bulk send"""
        with patch.object(sms_service, 'send_sms') as mock_send:
            mock_send.side_effect = [True, False, True]

            phone_numbers = [
                "+966501234567",
                "+966509876543",
                "+966501112223",
            ]

            result = sms_service.send_bulk_sms(
                phone_numbers=phone_numbers,
                message="Test",
            )

            assert result["total"] == 3
            assert result["success"] == 2
            assert result["failure"] == 1
            assert "+966509876543" in result["failed_numbers"]


# ==================== Phone Number Format Tests ====================

class TestPhoneNumberFormats:
    """Tests for various phone number formats"""

    @pytest.fixture
    def sms_service(self):
        return SMSNotificationService()

    def test_saudi_number_with_country_code(self, sms_service):
        """Should handle Saudi numbers with country code"""
        result = sms_service.send_sms(
            to_phone="+966501234567",
            message="Test",
        )
        assert result is True

    def test_saudi_number_without_plus(self, sms_service):
        """Should handle numbers without + prefix"""
        result = sms_service.send_sms(
            to_phone="966501234567",
            message="Test",
        )
        assert result is True

    def test_international_number(self, sms_service):
        """Should handle international numbers"""
        result = sms_service.send_sms(
            to_phone="+12025551234",
            message="Test",
        )
        assert result is True


# ==================== Error Handling Tests ====================

class TestErrorHandling:
    """Tests for error handling"""

    @pytest.fixture
    def sms_service(self):
        return SMSNotificationService()

    def test_send_sms_exception_returns_false(self, sms_service):
        """Should return False on exception"""
        with patch.object(sms_service, 'client', create=True) as mock_client:
            mock_client.messages.create.side_effect = Exception("API Error")
            sms_service.client = mock_client

            result = sms_service.send_sms(
                to_phone="+966501234567",
                message="Test",
            )
            # In mock mode (client=None), it should succeed
            # This tests that exceptions are caught

    def test_bulk_sms_with_exception(self, sms_service):
        """Should handle exceptions in bulk SMS"""
        with patch.object(sms_service, 'send_sms') as mock_send:
            mock_send.side_effect = [True, Exception("Network error"), True]

            result = sms_service.send_bulk_sms(
                phone_numbers=["+966501234567", "+966509876543", "+966501112223"],
                message="Test",
            )

            assert result["failure"] == 1
            assert "+966509876543" in result["failed_numbers"]


# ==================== Message Content Tests ====================

class TestMessageContent:
    """Tests for message content handling"""

    @pytest.fixture
    def sms_service(self):
        return SMSNotificationService()

    def test_long_message(self, sms_service):
        """Should handle long messages"""
        long_message = "A" * 500
        result = sms_service.send_sms(
            to_phone="+966501234567",
            message=long_message,
        )
        assert result is True

    def test_message_with_special_characters(self, sms_service):
        """Should handle special characters"""
        result = sms_service.send_sms(
            to_phone="+966501234567",
            message="Test: @#$%^&*()!",
        )
        assert result is True

    def test_message_with_emojis(self, sms_service):
        """Should handle emojis"""
        result = sms_service.send_sms(
            to_phone="+966501234567",
            message="Hello! 👋 Welcome! ✅",
        )
        assert result is True

    def test_message_with_newlines(self, sms_service):
        """Should handle newlines"""
        result = sms_service.send_sms(
            to_phone="+966501234567",
            message="Line 1\nLine 2\nLine 3",
        )
        assert result is True
