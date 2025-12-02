"""Support Management API routes"""

from fastapi import APIRouter
from app.api.v1.support import tickets, kb, faq, chat, feedback, analytics, contact

# Create main support router
support_router = APIRouter()

# Include all sub-routers with prefixes and tags
support_router.include_router(tickets.router, prefix="/tickets", tags=["support-tickets"])
support_router.include_router(kb.router, prefix="/kb", tags=["support-knowledge-base"])
support_router.include_router(faq.router, prefix="/faq", tags=["support-faq"])
support_router.include_router(chat.router, prefix="/chat", tags=["support-chat"])
support_router.include_router(feedback.router, prefix="/feedback", tags=["support-feedback"])
support_router.include_router(analytics.router, prefix="/analytics", tags=["support-analytics"])
support_router.include_router(contact.router, prefix="/contact", tags=["support-contact"])

__all__ = ["support_router"]
