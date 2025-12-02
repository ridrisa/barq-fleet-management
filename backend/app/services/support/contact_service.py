"""Contact Support Service"""
from typing import Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
import uuid

from app.models.support import Ticket, TicketCategory, TicketPriority, TicketStatus


class ContactSupportService:
    """Service for handling contact form submissions"""

    def submit_contact_form(
        self, db: Session, *,
        name: str,
        email: str,
        subject: str,
        message: str,
        phone: Optional[str] = None,
        department: Optional[str] = None,
        urgency: str = "normal"
    ) -> Dict:
        """
        Handle contact form submission and optionally create a ticket

        Args:
            db: Database session
            name: Contact name
            email: Contact email
            subject: Message subject
            message: Message content
            phone: Optional phone number
            department: Optional department to route to
            urgency: Urgency level (normal, high, critical)

        Returns:
            Dictionary with submission result
        """
        # Generate reference number
        reference_number = f"REF-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        # Determine priority based on urgency
        priority_map = {
            "normal": TicketPriority.MEDIUM,
            "high": TicketPriority.HIGH,
            "critical": TicketPriority.URGENT
        }
        priority = priority_map.get(urgency, TicketPriority.MEDIUM)

        # Auto-create ticket
        today = datetime.now()
        date_prefix = today.strftime("%Y%m%d")
        today_count = db.query(func.count(Ticket.id)).filter(
            func.date(Ticket.created_at) == today.date()
        ).scalar() or 0

        ticket_id = f"TKT-{date_prefix}-{(today_count + 1):03d}"

        # Map department to category if possible
        category = TicketCategory.OTHER
        if department:
            department_category_map = {
                "technical": TicketCategory.TECHNICAL,
                "billing": TicketCategory.BILLING,
                "delivery": TicketCategory.DELIVERY,
                "complaint": TicketCategory.COMPLAINT,
                "hr": TicketCategory.HR,
                "finance": TicketCategory.FINANCE,
                "operations": TicketCategory.OPERATIONS,
                "it": TicketCategory.IT
            }
            category = department_category_map.get(department.lower(), TicketCategory.OTHER)

        # Create ticket
        ticket = Ticket(
            ticket_id=ticket_id,
            subject=subject,
            description=f"Contact Form Submission\n\nFrom: {name}\nEmail: {email}\nPhone: {phone or 'N/A'}\n\n{message}",
            category=category,
            priority=priority,
            status=TicketStatus.OPEN,
            contact_email=email,
            contact_phone=phone,
            department=department,
            tags="contact-form"
        )

        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        # Determine estimated response time based on urgency
        response_times = {
            "normal": "24-48 hours",
            "high": "12-24 hours",
            "critical": "2-4 hours"
        }
        estimated_response_time = response_times.get(urgency, "24-48 hours")

        return {
            "success": True,
            "message": "Your message has been received. We will get back to you shortly.",
            "ticket_id": ticket.ticket_id,
            "reference_number": reference_number,
            "estimated_response_time": estimated_response_time
        }

    def get_departments(self) -> list:
        """Get list of available departments for contact routing"""
        return [
            {
                "name": "Technical Support",
                "email": "technical@barq.sa",
                "phone": "+966-XXX-XXX-XXXX",
                "hours": "Sunday - Thursday, 8 AM - 6 PM",
                "description": "For technical issues and system problems",
                "average_response_time": "4-8 hours"
            },
            {
                "name": "Billing & Finance",
                "email": "billing@barq.sa",
                "phone": "+966-XXX-XXX-XXXX",
                "hours": "Sunday - Thursday, 9 AM - 5 PM",
                "description": "For billing inquiries and payment issues",
                "average_response_time": "12-24 hours"
            },
            {
                "name": "Delivery Operations",
                "email": "operations@barq.sa",
                "phone": "+966-XXX-XXX-XXXX",
                "hours": "24/7",
                "description": "For delivery-related inquiries",
                "average_response_time": "2-4 hours"
            },
            {
                "name": "Human Resources",
                "email": "hr@barq.sa",
                "phone": "+966-XXX-XXX-XXXX",
                "hours": "Sunday - Thursday, 9 AM - 5 PM",
                "description": "For HR and employment inquiries",
                "average_response_time": "24-48 hours"
            },
            {
                "name": "General Inquiries",
                "email": "info@barq.sa",
                "phone": "+966-XXX-XXX-XXXX",
                "hours": "Sunday - Thursday, 9 AM - 5 PM",
                "description": "For general questions and information",
                "average_response_time": "24-48 hours"
            }
        ]


contact_support_service = ContactSupportService()
