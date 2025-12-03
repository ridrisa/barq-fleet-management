"""Support Module Models"""

from app.models.support.canned_response import CannedResponse
from app.models.support.chat_message import ChatMessage
from app.models.support.chat_session import ChatSession, ChatStatus
from app.models.support.faq import FAQ
from app.models.support.feedback import Feedback, FeedbackCategory, FeedbackStatus
from app.models.support.kb_article import ArticleStatus, KBArticle
from app.models.support.kb_category import KBCategory
from app.models.support.ticket import (
    EscalationLevel,
    Ticket,
    TicketCategory,
    TicketPriority,
    TicketStatus,
)
from app.models.support.ticket_attachment import TicketAttachment
from app.models.support.ticket_reply import TicketReply
from app.models.support.ticket_template import TicketTemplate

__all__ = [
    # Ticket models
    "Ticket",
    "TicketCategory",
    "TicketPriority",
    "TicketStatus",
    "EscalationLevel",
    "TicketReply",
    "TicketAttachment",
    "TicketTemplate",
    "CannedResponse",
    # Knowledge Base
    "KBArticle",
    "ArticleStatus",
    "KBCategory",
    # FAQ
    "FAQ",
    # Live Chat
    "ChatSession",
    "ChatStatus",
    "ChatMessage",
    # Feedback
    "Feedback",
    "FeedbackCategory",
    "FeedbackStatus",
]
