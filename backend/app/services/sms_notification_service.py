"""SMS Notification Service using Twilio

Provides SMS notifications for:
- Leave approvals/rejections
- Salary payments
- Document expiry alerts
- Emergency notifications
- OTP/verification codes
"""
from typing import Optional
from decimal import Decimal
import logging

# Twilio SDK
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logging.warning("Twilio not installed. SMS service will run in mock mode.")


class SMSNotificationService:
    """
    Service for sending SMS notifications via Twilio

    Supports:
    - Transactional SMS (leave, salary, documents)
    - OTP and verification codes
    - Emergency alerts
    - Bulk SMS
    """

    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_phone: str = "+966501234567"  # Default Saudi number
    ):
        """
        Initialize SMS notification service

        Args:
            account_sid: Twilio account SID
            auth_token: Twilio auth token
            from_phone: Sender phone number
        """
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_phone = from_phone
        self.logger = logging.getLogger(__name__)

        # Initialize Twilio client if available
        if TWILIO_AVAILABLE and account_sid and auth_token:
            self.client = TwilioClient(account_sid, auth_token)
        else:
            self.client = None
            self.logger.warning("Running in mock mode - SMS will be logged but not sent")

    def send_sms(
        self,
        to_phone: str,
        message: str
    ) -> bool:
        """
        Send a single SMS

        Args:
            to_phone: Recipient phone number (E.164 format)
            message: SMS message text

        Returns:
            True if SMS was sent successfully
        """
        try:
            if self.client:
                # Send via Twilio
                message_obj = self.client.messages.create(
                    body=message,
                    from_=self.from_phone,
                    to=to_phone
                )
                self.logger.info(f"SMS sent to {to_phone} - SID: {message_obj.sid}")
                return message_obj.status in ["queued", "sent", "delivered"]

            else:
                # Mock mode - just log
                self.logger.info(
                    f"[MOCK SMS] To: {to_phone}\n"
                    f"From: {self.from_phone}\n"
                    f"Message: {message}"
                )
                return True

        except Exception as e:
            self.logger.error(f"Failed to send SMS to {to_phone}: {str(e)}")
            return False

    def send_leave_approval_sms(
        self,
        to_phone: str,
        courier_name: str,
        leave_type: str,
        start_date: str,
        end_date: str
    ) -> bool:
        """Send leave approval SMS"""
        message = (
            f"مرحبا {courier_name},\n"
            f"تم قبول طلب الاجازة ({leave_type})\n"
            f"من: {start_date}\n"
            f"الى: {end_date}\n"
            f"BARQ Fleet Management"
        )

        return self.send_sms(to_phone, message)

    def send_leave_rejection_sms(
        self,
        to_phone: str,
        courier_name: str,
        leave_type: str
    ) -> bool:
        """Send leave rejection SMS"""
        message = (
            f"مرحبا {courier_name},\n"
            f"للأسف، تم رفض طلب الاجازة ({leave_type})\n"
            f"يرجى الاتصال بقسم الموارد البشرية\n"
            f"BARQ"
        )

        return self.send_sms(to_phone, message)

    def send_salary_payment_sms(
        self,
        to_phone: str,
        courier_name: str,
        month: int,
        year: int,
        net_salary: Decimal
    ) -> bool:
        """Send salary payment SMS"""
        message = (
            f"مرحبا {courier_name},\n"
            f"تم دفع الراتب {month}/{year}\n"
            f"المبلغ: {net_salary:,.2f} ريال\n"
            f"BARQ"
        )

        return self.send_sms(to_phone, message)

    def send_document_expiry_alert(
        self,
        to_phone: str,
        courier_name: str,
        document_type: str,
        expiry_date: str,
        days_remaining: int
    ) -> bool:
        """Send document expiry alert"""
        urgency = "عاجل" if days_remaining <= 7 else "تنبيه"

        message = (
            f"{urgency}: {courier_name}\n"
            f"{document_type} ستنتهي صلاحيته في {days_remaining} يوم\n"
            f"تاريخ الانتهاء: {expiry_date}\n"
            f"يرجى التجديد فورا - BARQ"
        )

        return self.send_sms(to_phone, message)

    def send_otp_code(
        self,
        to_phone: str,
        otp_code: str,
        expiry_minutes: int = 5
    ) -> bool:
        """Send OTP verification code"""
        message = (
            f"رمز التحقق الخاص بك: {otp_code}\n"
            f"صالح لمدة {expiry_minutes} دقائق\n"
            f"لا تشارك هذا الرمز - BARQ"
        )

        return self.send_sms(to_phone, message)

    def send_emergency_alert(
        self,
        to_phone: str,
        courier_name: str,
        message_text: str
    ) -> bool:
        """Send emergency alert"""
        message = (
            f"تنبيه طارئ - {courier_name}:\n"
            f"{message_text}\n"
            f"BARQ Fleet Management"
        )

        return self.send_sms(to_phone, message)

    def send_password_reset_sms(
        self,
        to_phone: str,
        reset_code: str
    ) -> bool:
        """Send password reset code"""
        message = (
            f"رمز إعادة تعيين كلمة المرور: {reset_code}\n"
            f"صالح لمدة 15 دقيقة\n"
            f"BARQ"
        )

        return self.send_sms(to_phone, message)

    def send_attendance_reminder(
        self,
        to_phone: str,
        courier_name: str
    ) -> bool:
        """Send attendance reminder"""
        message = (
            f"تذكير: {courier_name}\n"
            f"لم يتم تسجيل حضورك اليوم\n"
            f"يرجى تسجيل الحضور - BARQ"
        )

        return self.send_sms(to_phone, message)

    def send_bulk_sms(
        self,
        phone_numbers: list,
        message: str
    ) -> dict:
        """
        Send bulk SMS to multiple recipients

        Args:
            phone_numbers: List of phone numbers
            message: Message text

        Returns:
            Dictionary with success and failure counts
        """
        success_count = 0
        failure_count = 0
        failed_numbers = []

        for phone in phone_numbers:
            try:
                if self.send_sms(phone, message):
                    success_count += 1
                else:
                    failure_count += 1
                    failed_numbers.append(phone)
            except Exception as e:
                self.logger.error(f"Failed to send SMS to {phone}: {str(e)}")
                failure_count += 1
                failed_numbers.append(phone)

        return {
            "total": len(phone_numbers),
            "success": success_count,
            "failure": failure_count,
            "failed_numbers": failed_numbers
        }


# Singleton instance
sms_notification_service = SMSNotificationService()
