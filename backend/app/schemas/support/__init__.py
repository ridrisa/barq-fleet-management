"""Support Module Schemas"""

# Ticket schemas
# Re-export enums for convenience
from app.models.support import (
    ArticleStatus,
    ChatStatus,
    EscalationLevel,
    FeedbackCategory,
    FeedbackStatus,
    TicketCategory,
    TicketPriority,
    TicketStatus,
)

# Analytics schemas
from app.schemas.support.analytics import (
    AgentPerformanceMetrics,
    ChatAnalytics,
    CustomerSatisfactionMetrics,
    DateRangeFilter,
    EscalationAnalytics,
    KBAnalytics,
    ResponseTimeMetrics,
    SLAMetrics,
    SupportAnalytics,
    SupportTrendData,
    TicketMetrics,
)

# Chat schemas
from app.schemas.support.chat import (
    ChatMessageBase,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatMessageWithSender,
    ChatSessionAssign,
    ChatSessionBase,
    ChatSessionCreate,
    ChatSessionList,
    ChatSessionResponse,
    ChatSessionTransfer,
    ChatSessionUpdate,
    ChatSessionWithMessages,
    ChatTranscript,
)

# Contact schemas
from app.schemas.support.contact import (
    ContactFormResponse,
    ContactFormSubmit,
    ContactPreferences,
    DepartmentInfo,
)

# FAQ schemas
from app.schemas.support.faq import (
    FAQBase,
    FAQByCategory,
    FAQCategoryList,
    FAQCreate,
    FAQList,
    FAQResponse,
    FAQUpdate,
)

# Feedback schemas
from app.schemas.support.feedback import (
    FeedbackBase,
    FeedbackCreate,
    FeedbackList,
    FeedbackRespond,
    FeedbackResponse,
    FeedbackStatistics,
    FeedbackUpdate,
    FeedbackWithUser,
)

# Knowledge Base schemas
from app.schemas.support.kb_article import (
    KBArticleBase,
    KBArticleCreate,
    KBArticleList,
    KBArticlePublish,
    KBArticleResponse,
    KBArticleSearch,
    KBArticleUpdate,
    KBArticleVote,
    KBArticleWithAuthor,
)
from app.schemas.support.ticket import (
    CannedResponseCreate,
    CannedResponseResponse,
    CannedResponseUpdate,
    TicketAssign,
    TicketAttachmentCreate,
    TicketAttachmentResponse,
    TicketBase,
    TicketBulkAction,
    TicketCreate,
    TicketCreateFromTemplate,
    TicketEscalate,
    TicketList,
    TicketMerge,
    TicketResolve,
    TicketResponse,
    TicketSLAConfig,
    TicketStatistics,
    TicketTemplateCreate,
    TicketTemplateResponse,
    TicketTemplateUpdate,
    TicketUpdate,
    TicketWithRelations,
)

# Ticket reply schemas
from app.schemas.support.ticket_reply import (
    TicketReplyBase,
    TicketReplyCreate,
    TicketReplyResponse,
    TicketReplyUpdate,
    TicketReplyWithUser,
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
