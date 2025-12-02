"""Support Module Schemas"""

# Ticket schemas
from app.schemas.support.ticket import (
    TicketBase,
    TicketCreate,
    TicketCreateFromTemplate,
    TicketUpdate,
    TicketAssign,
    TicketResolve,
    TicketEscalate,
    TicketMerge,
    TicketBulkAction,
    TicketSLAConfig,
    TicketResponse,
    TicketList,
    TicketStatistics,
    TicketWithRelations,
    TicketAttachmentCreate,
    TicketAttachmentResponse,
    TicketTemplateCreate,
    TicketTemplateUpdate,
    TicketTemplateResponse,
    CannedResponseCreate,
    CannedResponseUpdate,
    CannedResponseResponse,
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
    SLAMetrics,
    ResponseTimeMetrics,
    AgentPerformanceMetrics,
    CustomerSatisfactionMetrics,
    SupportTrendData,
    SupportAnalytics,
    EscalationAnalytics,
    KBAnalytics,
    ChatAnalytics,
    DateRangeFilter,
)

# Contact schemas
from app.schemas.support.contact import (
    ContactFormSubmit,
    ContactFormResponse,
    ContactPreferences,
    DepartmentInfo,
)

# Re-export enums for convenience
from app.models.support import (
    TicketCategory,
    TicketPriority,
    TicketStatus,
    EscalationLevel,
    ArticleStatus,
    ChatStatus,
    FeedbackCategory,
    FeedbackStatus,
)

__all__ = [
    # Ticket schemas
    "TicketBase",
    "TicketCreate",
    "TicketCreateFromTemplate",
    "TicketUpdate",
    "TicketAssign",
    "TicketResolve",
    "TicketEscalate",
    "TicketMerge",
    "TicketBulkAction",
    "TicketSLAConfig",
    "TicketResponse",
    "TicketList",
    "TicketStatistics",
    "TicketWithRelations",
    "TicketAttachmentCreate",
    "TicketAttachmentResponse",
    "TicketTemplateCreate",
    "TicketTemplateUpdate",
    "TicketTemplateResponse",
    "CannedResponseCreate",
    "CannedResponseUpdate",
    "CannedResponseResponse",
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
    "SLAMetrics",
    "ResponseTimeMetrics",
    "AgentPerformanceMetrics",
    "CustomerSatisfactionMetrics",
    "SupportTrendData",
    "SupportAnalytics",
    "EscalationAnalytics",
    "KBAnalytics",
    "ChatAnalytics",
    "DateRangeFilter",
    # Contact schemas
    "ContactFormSubmit",
    "ContactFormResponse",
    "ContactPreferences",
    "DepartmentInfo",
    # Enums
    "TicketCategory",
    "TicketPriority",
    "TicketStatus",
    "EscalationLevel",
    "ArticleStatus",
    "ChatStatus",
    "FeedbackCategory",
    "FeedbackStatus",
]
