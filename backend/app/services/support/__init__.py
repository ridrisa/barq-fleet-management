"""Support Services

Consolidated services for support module:
- ticket_service.py: Tickets, replies, canned responses, templates, contact forms
- knowledge_service.py: FAQs and knowledge base articles
- feedback_service.py: Customer feedback
- chat_service.py: Live chat sessions and messages
- analytics_service.py: Support analytics and reporting
"""

# Ticket-related services (consolidated)
from app.services.support.ticket_service import (
    canned_response_service,
    contact_support_service,
    ticket_reply_service,
    ticket_service,
    ticket_template_service,
)

# Knowledge-related services (consolidated)
from app.services.support.knowledge_service import (
    faq_service,
    kb_article_service,
)

# Standalone services
from app.services.support.analytics_service import support_analytics_service
from app.services.support.chat_service import chat_message_service, chat_session_service
from app.services.support.feedback_service import feedback_service

__all__ = [
    # Ticket services
    "ticket_service",
    "ticket_reply_service",
    "ticket_template_service",
    "canned_response_service",
    "contact_support_service",
    # Knowledge services
    "kb_article_service",
    "faq_service",
    # Chat services
    "chat_session_service",
    "chat_message_service",
    # Other services
    "feedback_service",
    "support_analytics_service",
]
