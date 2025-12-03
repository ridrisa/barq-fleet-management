"""Support Analytics Schemas"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TicketMetrics(BaseModel):
    """Ticket volume and status metrics"""

    total_tickets: int = 0
    open_tickets: int = 0
    in_progress_tickets: int = 0
    waiting_tickets: int = 0
    resolved_tickets: int = 0
    closed_tickets: int = 0
    by_priority: Dict[str, int] = Field(default_factory=dict)
    by_category: Dict[str, int] = Field(default_factory=dict)
    by_escalation: Dict[str, int] = Field(default_factory=dict)
    escalated_count: int = 0
    merged_count: int = 0


class SLAMetrics(BaseModel):
    """SLA compliance metrics"""

    total_with_sla: int = 0
    sla_met: int = 0
    sla_breached: int = 0
    compliance_rate: float = 0.0
    avg_time_to_breach_hours: float = 0.0
    at_risk_count: int = 0
    by_priority: Dict[str, Dict[str, int]] = Field(default_factory=dict)


class ResponseTimeMetrics(BaseModel):
    """Response time metrics"""

    avg_first_response_minutes: float = 0.0
    median_first_response_minutes: float = 0.0
    avg_resolution_time_hours: float = 0.0
    median_resolution_time_hours: float = 0.0


class AgentPerformanceMetrics(BaseModel):
    """Individual agent performance metrics"""

    agent_id: int
    agent_name: str
    tickets_assigned: int = 0
    tickets_resolved: int = 0
    avg_resolution_time_hours: float = 0.0
    customer_satisfaction_score: Optional[float] = None


class CustomerSatisfactionMetrics(BaseModel):
    """Customer satisfaction metrics"""

    total_feedbacks: int = 0
    average_rating: float = 0.0
    positive_feedback_count: int = 0
    negative_feedback_count: int = 0
    satisfaction_percentage: float = 0.0


class SupportTrendData(BaseModel):
    """Trend data point"""

    date: date
    ticket_count: int = 0
    resolved_count: int = 0
    avg_resolution_hours: float = 0.0


class SupportAnalytics(BaseModel):
    """Comprehensive support analytics"""

    period_start: date
    period_end: date
    ticket_metrics: TicketMetrics
    response_time_metrics: ResponseTimeMetrics
    sla_metrics: Optional[SLAMetrics] = None
    customer_satisfaction: CustomerSatisfactionMetrics
    top_categories: List[Dict[str, int]]
    top_agents: List[AgentPerformanceMetrics]
    trend_data: List[SupportTrendData]


class EscalationAnalytics(BaseModel):
    """Escalation analytics"""

    total_escalated: int = 0
    by_level: Dict[str, int] = Field(default_factory=dict)
    avg_time_to_escalate_hours: float = 0.0
    escalation_rate: float = 0.0
    top_reasons: List[Dict[str, Any]] = Field(default_factory=list)


class KBAnalytics(BaseModel):
    """Knowledge base analytics"""

    total_articles: int = 0
    published_articles: int = 0
    total_views: int = 0
    avg_helpfulness_score: float = 0.0
    top_articles: List[Dict[str, Any]] = Field(default_factory=list)
    articles_by_category: Dict[str, int] = Field(default_factory=dict)


class ChatAnalytics(BaseModel):
    """Live chat analytics"""

    total_sessions: int = 0
    active_sessions: int = 0
    avg_wait_time_minutes: float = 0.0
    avg_chat_duration_minutes: float = 0.0
    total_messages: int = 0
    sessions_by_agent: Dict[str, int] = Field(default_factory=dict)


class DateRangeFilter(BaseModel):
    """Date range filter for analytics"""

    start_date: date = Field(..., description="Start date for analytics period")
    end_date: date = Field(..., description="End date for analytics period")
