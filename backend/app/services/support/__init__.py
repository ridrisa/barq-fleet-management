"""Support Services"""

from app.services.support.analytics_service import support_analytics_service
from app.services.support.canned_response_service import canned_response_service
from app.services.support.chat_service import chat_message_service, chat_session_service
from app.services.support.contact_service import contact_support_service
from app.services.support.faq_service import faq_service
from app.services.support.feedback_service import feedback_service
from app.services.support.kb_article_service import kb_article_service
from app.services.support.template_service import ticket_template_service
from app.services.support.ticket_reply_service import ticket_reply_service
from app.services.support.ticket_service import ticket_service

__all__ = [
    "ticket_service",
    "ticket_reply_service",
    "ticket_template_service",
    "canned_response_service",
    "kb_article_service",
    "faq_service",
    "chat_session_service",
    "chat_message_service",
    "feedback_service",
    "contact_support_service",
    "support_analytics_service",
]
