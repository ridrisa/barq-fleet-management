"""Support Module Models"""

from app.models.support.ticket import (
    Ticket,
    TicketCategory,
    TicketPriority,
    TicketStatus,
)
from app.models.support.ticket_reply import TicketReply
from app.models.support.kb_article import KBArticle, ArticleStatus
from app.models.support.faq import FAQ
from app.models.support.chat_session import ChatSession, ChatStatus
from app.models.support.chat_message import ChatMessage
from app.models.support.feedback import Feedback, FeedbackCategory, FeedbackStatus

__all__ = [
    # Ticket models
    "Ticket",
    "TicketCategory",
    "TicketPriority",
    "TicketStatus",
    "TicketReply",
    # Knowledge Base
    "KBArticle",
    "ArticleStatus",
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
