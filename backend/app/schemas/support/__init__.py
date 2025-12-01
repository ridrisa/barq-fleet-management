"""Support Module Schemas"""

# Ticket schemas
from app.schemas.support.ticket import (
    TicketBase,
    TicketCreate,
    TicketUpdate,
    TicketAssign,
    TicketResolve,
    TicketResponse,
    TicketList,
    TicketStatistics,
    TicketWithRelations,
)

# Ticket reply schemas
from app.schemas.support.ticket_reply import (
    TicketReplyBase,
    TicketReplyCreate,
    TicketReplyUpdate,
    TicketReplyResponse,
    TicketReplyWithUser,
)

# Knowledge Base schemas
from app.schemas.support.kb_article import (
    KBArticleBase,
    KBArticleCreate,
    KBArticleUpdate,
    KBArticlePublish,
    KBArticleVote,
    KBArticleResponse,
    KBArticleList,
    KBArticleWithAuthor,
    KBArticleSearch,
)

# FAQ schemas
from app.schemas.support.faq import (
    FAQBase,
    FAQCreate,
    FAQUpdate,
    FAQResponse,
    FAQList,
    FAQByCategory,
    FAQCategoryList,
)

# Chat schemas
from app.schemas.support.chat import (
    ChatMessageBase,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatMessageWithSender,
    ChatSessionBase,
    ChatSessionCreate,
    ChatSessionUpdate,
    ChatSessionAssign,
    ChatSessionTransfer,
    ChatSessionResponse,
    ChatSessionWithMessages,
    ChatSessionList,
    ChatTranscript,
)

# Feedback schemas
from app.schemas.support.feedback import (
    FeedbackBase,
    FeedbackCreate,
    FeedbackUpdate,
    FeedbackRespond,
    FeedbackResponse,
    FeedbackList,
    FeedbackWithUser,
    FeedbackStatistics,
)

# Analytics schemas
from app.schemas.support.analytics import (
    TicketMetrics,
    ResponseTimeMetrics,
    AgentPerformanceMetrics,
    CustomerSatisfactionMetrics,
    SupportTrendData,
    SupportAnalytics,
    KBAnalytics,
    ChatAnalytics,
    DateRangeFilter,
)

# Re-export enums for convenience
from app.models.support import (
    TicketCategory,
    TicketPriority,
    TicketStatus,
    ArticleStatus,
    ChatStatus,
    FeedbackCategory,
    FeedbackStatus,
)

__all__ = [
    # Ticket schemas
    "TicketBase",
    "TicketCreate",
    "TicketUpdate",
    "TicketAssign",
    "TicketResolve",
    "TicketResponse",
    "TicketList",
    "TicketStatistics",
    "TicketWithRelations",
    # Ticket reply schemas
    "TicketReplyBase",
    "TicketReplyCreate",
    "TicketReplyUpdate",
    "TicketReplyResponse",
    "TicketReplyWithUser",
    # KB schemas
    "KBArticleBase",
    "KBArticleCreate",
    "KBArticleUpdate",
    "KBArticlePublish",
    "KBArticleVote",
    "KBArticleResponse",
    "KBArticleList",
    "KBArticleWithAuthor",
    "KBArticleSearch",
    # FAQ schemas
    "FAQBase",
    "FAQCreate",
    "FAQUpdate",
    "FAQResponse",
    "FAQList",
    "FAQByCategory",
    "FAQCategoryList",
    # Chat schemas
    "ChatMessageBase",
    "ChatMessageCreate",
    "ChatMessageResponse",
    "ChatMessageWithSender",
    "ChatSessionBase",
    "ChatSessionCreate",
    "ChatSessionUpdate",
    "ChatSessionAssign",
    "ChatSessionTransfer",
    "ChatSessionResponse",
    "ChatSessionWithMessages",
    "ChatSessionList",
    "ChatTranscript",
    # Feedback schemas
    "FeedbackBase",
    "FeedbackCreate",
    "FeedbackUpdate",
    "FeedbackRespond",
    "FeedbackResponse",
    "FeedbackList",
    "FeedbackWithUser",
    "FeedbackStatistics",
    # Analytics schemas
    "TicketMetrics",
    "ResponseTimeMetrics",
    "AgentPerformanceMetrics",
    "CustomerSatisfactionMetrics",
    "SupportTrendData",
    "SupportAnalytics",
    "KBAnalytics",
    "ChatAnalytics",
    "DateRangeFilter",
    # Enums
    "TicketCategory",
    "TicketPriority",
    "TicketStatus",
    "ArticleStatus",
    "ChatStatus",
    "FeedbackCategory",
    "FeedbackStatus",
]
