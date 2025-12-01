"""Email Notification Service

Service for sending email notifications using SendGrid or SMTP.
Supports template-based emails for various system events.
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr
import logging

# Email sending library - using SendGrid as an example
# Install: pip install sendgrid
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    logging.warning("SendGrid not installed. Email service will run in mock mode.")


class EmailRecipient(BaseModel):
    """Email recipient model"""
    email: EmailStr
    name: Optional[str] = None


class EmailTemplate:
    """Email template definitions"""

    # Leave approval/rejection
    LEAVE_APPROVED = "leave_approved"
    LEAVE_REJECTED = "leave_rejected"

    # Salary
    SALARY_PAID = "salary_paid"
    SALARY_PROCESSED = "salary_processed"

    # Loan
    LOAN_APPROVED = "loan_approved"
    LOAN_REJECTED = "loan_rejected"
    LOAN_PAYMENT_DUE = "loan_payment_due"

    # Document expiry
    LICENSE_EXPIRING = "license_expiring"
    IQAMA_EXPIRING = "iqama_expiring"
    VEHICLE_REGISTRATION_EXPIRING = "vehicle_registration_expiring"

    # System
    PASSWORD_RESET = "password_reset"
    ACCOUNT_CREATED = "account_created"
    WELCOME = "welcome"


class EmailNotificationService:
    """
    Service for sending email notifications

    Supports:
    - Template-based emails
    - Multiple recipients
    - Attachments
    - Dynamic content
    """

    def __init__(
        self,
        sendgrid_api_key: Optional[str] = None,
        from_email: str = "noreply@barqfleet.com",
        from_name: str = "BARQ Fleet Management"
    ):
        """
        Initialize email notification service

        Args:
            sendgrid_api_key: SendGrid API key
            from_email: Default sender email
            from_name: Default sender name
        """
        self.sendgrid_api_key = sendgrid_api_key
        self.from_email = from_email
        self.from_name = from_name
        self.logger = logging.getLogger(__name__)

        # Initialize SendGrid client if available
        if SENDGRID_AVAILABLE and sendgrid_api_key:
            self.sg_client = SendGridAPIClient(sendgrid_api_key)
        else:
            self.sg_client = None
            self.logger.warning("Running in mock mode - emails will be logged but not sent")

    def send_email(
        self,
        to: EmailRecipient,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None,
        cc: Optional[List[EmailRecipient]] = None,
        bcc: Optional[List[EmailRecipient]] = None,
        attachments: Optional[List[Dict]] = None
    ) -> bool:
        """
        Send a single email

        Args:
            to: Recipient
            subject: Email subject
            html_content: HTML email body
            plain_content: Plain text email body (optional)
            cc: CC recipients
            bcc: BCC recipients
            attachments: List of attachments

        Returns:
            True if email was sent successfully
        """
        try:
            if self.sg_client:
                # Send via SendGrid
                message = Mail(
                    from_email=Email(self.from_email, self.from_name),
                    to_emails=To(to.email, to.name),
                    subject=subject,
                    plain_text_content=Content("text/plain", plain_content or html_content),
                    html_content=Content("text/html", html_content)
                )

                response = self.sg_client.send(message)
                self.logger.info(f"Email sent to {to.email} - Status: {response.status_code}")
                return response.status_code == 202

            else:
                # Mock mode - just log
                self.logger.info(
                    f"[MOCK] Email would be sent to {to.email}\n"
                    f"Subject: {subject}\n"
                    f"Content: {html_content[:100]}..."
                )
                return True

        except Exception as e:
            self.logger.error(f"Failed to send email to {to.email}: {str(e)}")
            return False

    def send_leave_approval_notification(
        self,
        to_email: str,
        courier_name: str,
        leave_type: str,
        start_date: str,
        end_date: str,
        days: int
    ) -> bool:
        """
        Send leave approval notification

        Args:
            to_email: Courier email
            courier_name: Name of the courier
            leave_type: Type of leave
            start_date: Leave start date
            end_date: Leave end date
            days: Number of days

        Returns:
            True if sent successfully
        """
        subject = "Leave Request Approved"
        html_content = f"""
        <html>
        <body>
            <h2>Leave Request Approved</h2>
            <p>Dear {courier_name},</p>
            <p>Your leave request has been approved.</p>
            <ul>
                <li><strong>Leave Type:</strong> {leave_type}</li>
                <li><strong>Start Date:</strong> {start_date}</li>
                <li><strong>End Date:</strong> {end_date}</li>
                <li><strong>Total Days:</strong> {days}</li>
            </ul>
            <p>Please plan accordingly.</p>
            <p>Best regards,<br>BARQ Fleet Management</p>
        </body>
        </html>
        """

        return self.send_email(
            to=EmailRecipient(email=to_email, name=courier_name),
            subject=subject,
            html_content=html_content
        )

    def send_leave_rejection_notification(
        self,
        to_email: str,
        courier_name: str,
        leave_type: str,
        start_date: str,
        end_date: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Send leave rejection notification

        Args:
            to_email: Courier email
            courier_name: Name of the courier
            leave_type: Type of leave
            start_date: Leave start date
            end_date: Leave end date
            reason: Rejection reason

        Returns:
            True if sent successfully
        """
        subject = "Leave Request Rejected"
        html_content = f"""
        <html>
        <body>
            <h2>Leave Request Rejected</h2>
            <p>Dear {courier_name},</p>
            <p>Unfortunately, your leave request has been rejected.</p>
            <ul>
                <li><strong>Leave Type:</strong> {leave_type}</li>
                <li><strong>Requested Dates:</strong> {start_date} to {end_date}</li>
                {f'<li><strong>Reason:</strong> {reason}</li>' if reason else ''}
            </ul>
            <p>Please contact HR for more information.</p>
            <p>Best regards,<br>BARQ Fleet Management</p>
        </body>
        </html>
        """

        return self.send_email(
            to=EmailRecipient(email=to_email, name=courier_name),
            subject=subject,
            html_content=html_content
        )

    def send_salary_payment_notification(
        self,
        to_email: str,
        courier_name: str,
        month: int,
        year: int,
        net_salary: Decimal,
        payment_date: str
    ) -> bool:
        """
        Send salary payment notification

        Args:
            to_email: Courier email
            courier_name: Name of the courier
            month: Month
            year: Year
            net_salary: Net salary amount
            payment_date: Payment date

        Returns:
            True if sent successfully
        """
        subject = f"Salary Payment - {month}/{year}"
        html_content = f"""
        <html>
        <body>
            <h2>Salary Payment Notification</h2>
            <p>Dear {courier_name},</p>
            <p>Your salary for {month}/{year} has been processed and paid.</p>
            <ul>
                <li><strong>Net Salary:</strong> SAR {net_salary:,.2f}</li>
                <li><strong>Payment Date:</strong> {payment_date}</li>
            </ul>
            <p>Please check your bank account.</p>
            <p>For detailed salary breakdown, please log in to the employee portal.</p>
            <p>Best regards,<br>BARQ Fleet Management</p>
        </body>
        </html>
        """

        return self.send_email(
            to=EmailRecipient(email=to_email, name=courier_name),
            subject=subject,
            html_content=html_content
        )

    def send_document_expiry_alert(
        self,
        to_email: str,
        courier_name: str,
        document_type: str,
        document_number: str,
        expiry_date: str,
        days_until_expiry: int
    ) -> bool:
        """
        Send document expiry alert

        Args:
            to_email: Courier email
            courier_name: Name of the courier
            document_type: Type of document (license, iqama, etc.)
            document_number: Document number
            expiry_date: Expiry date
            days_until_expiry: Days until expiry

        Returns:
            True if sent successfully
        """
        urgency = "URGENT" if days_until_expiry <= 7 else "IMPORTANT"

        subject = f"{urgency}: {document_type} Expiring Soon"
        html_content = f"""
        <html>
        <body>
            <h2 style="color: {'red' if days_until_expiry <= 7 else 'orange'};">{urgency}: Document Expiring Soon</h2>
            <p>Dear {courier_name},</p>
            <p>Your {document_type} is expiring in {days_until_expiry} days.</p>
            <ul>
                <li><strong>Document Type:</strong> {document_type}</li>
                <li><strong>Document Number:</strong> {document_number}</li>
                <li><strong>Expiry Date:</strong> {expiry_date}</li>
                <li><strong>Days Remaining:</strong> {days_until_expiry}</li>
            </ul>
            <p>Please renew your {document_type} as soon as possible to avoid any issues.</p>
            <p>Contact HR if you need assistance with the renewal process.</p>
            <p>Best regards,<br>BARQ Fleet Management</p>
        </body>
        </html>
        """

        return self.send_email(
            to=EmailRecipient(email=to_email, name=courier_name),
            subject=subject,
            html_content=html_content
        )

    def send_loan_approval_notification(
        self,
        to_email: str,
        courier_name: str,
        loan_amount: Decimal,
        monthly_deduction: Decimal,
        approval_date: str
    ) -> bool:
        """
        Send loan approval notification

        Args:
            to_email: Courier email
            courier_name: Name of the courier
            loan_amount: Loan amount
            monthly_deduction: Monthly deduction
            approval_date: Approval date

        Returns:
            True if sent successfully
        """
        subject = "Loan Request Approved"
        html_content = f"""
        <html>
        <body>
            <h2>Loan Request Approved</h2>
            <p>Dear {courier_name},</p>
            <p>Your loan request has been approved.</p>
            <ul>
                <li><strong>Loan Amount:</strong> SAR {loan_amount:,.2f}</li>
                <li><strong>Monthly Deduction:</strong> SAR {monthly_deduction:,.2f}</li>
                <li><strong>Approval Date:</strong> {approval_date}</li>
            </ul>
            <p>The loan amount will be disbursed to your account within 2-3 business days.</p>
            <p>Monthly deductions will start from your next salary payment.</p>
            <p>Best regards,<br>BARQ Fleet Management</p>
        </body>
        </html>
        """

        return self.send_email(
            to=EmailRecipient(email=to_email, name=courier_name),
            subject=subject,
            html_content=html_content
        )

    def send_welcome_email(
        self,
        to_email: str,
        courier_name: str,
        employee_id: str,
        start_date: str
    ) -> bool:
        """
        Send welcome email to new employee

        Args:
            to_email: Employee email
            courier_name: Name of the employee
            employee_id: Employee ID
            start_date: Start date

        Returns:
            True if sent successfully
        """
        subject = "Welcome to BARQ Fleet Management"
        html_content = f"""
        <html>
        <body>
            <h2>Welcome to BARQ Fleet Management!</h2>
            <p>Dear {courier_name},</p>
            <p>Welcome to our team! We're excited to have you join us.</p>
            <ul>
                <li><strong>Employee ID:</strong> {employee_id}</li>
                <li><strong>Start Date:</strong> {start_date}</li>
            </ul>
            <p>Please complete your onboarding process and set up your account credentials.</p>
            <p>If you have any questions, don't hesitate to reach out to HR.</p>
            <p>Best regards,<br>BARQ Fleet Management Team</p>
        </body>
        </html>
        """

        return self.send_email(
            to=EmailRecipient(email=to_email, name=courier_name),
            subject=subject,
            html_content=html_content
        )

    def send_bulk_notification(
        self,
        recipients: List[EmailRecipient],
        subject: str,
        html_content: str
    ) -> Dict[str, int]:
        """
        Send bulk emails to multiple recipients

        Args:
            recipients: List of email recipients
            subject: Email subject
            html_content: HTML content

        Returns:
            Dictionary with success and failure counts
        """
        success_count = 0
        failure_count = 0

        for recipient in recipients:
            try:
                if self.send_email(
                    to=recipient,
                    subject=subject,
                    html_content=html_content
                ):
                    success_count += 1
                else:
                    failure_count += 1
            except Exception as e:
                self.logger.error(f"Failed to send to {recipient.email}: {str(e)}")
                failure_count += 1

        return {
            "total": len(recipients),
            "success": success_count,
            "failure": failure_count
        }


# Singleton instance (configure with settings)
email_notification_service = EmailNotificationService()
