"""Support Analytics Service"""

from datetime import date, datetime, timedelta, timezone
from typing import Dict, List

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.support import (
    ChatSession,
    EscalationLevel,
    Feedback,
    KBArticle,
    Ticket,
    TicketPriority,
    TicketStatus,
)


class SupportAnalyticsService:
    """Service for support analytics and reporting"""

    def get_ticket_metrics(
        self, db: Session, *, start_date: date = None, end_date: date = None
    ) -> Dict:
        """Get ticket volume and status metrics"""
        query = db.query(Ticket)

        if start_date and end_date:
            query = query.filter(
                and_(Ticket.created_at >= start_date, Ticket.created_at <= end_date)
            )

        total_tickets = query.count()

        # By status - use .value for native PostgreSQL enum comparison
        open_tickets = query.filter(Ticket.status == TicketStatus.OPEN.value).count()
        in_progress_tickets = query.filter(Ticket.status == TicketStatus.IN_PROGRESS.value).count()
        resolved_tickets = query.filter(Ticket.status == TicketStatus.RESOLVED.value).count()
        closed_tickets = query.filter(Ticket.status == TicketStatus.CLOSED.value).count()

        # By priority
        by_priority = dict(
            query.with_entities(Ticket.priority, func.count(Ticket.id))
            .group_by(Ticket.priority)
            .all()
        )

        # By category
        by_category = dict(
            query.with_entities(Ticket.category, func.count(Ticket.id))
            .group_by(Ticket.category)
            .all()
        )

        # Waiting tickets
        pending_tickets = query.filter(Ticket.status == TicketStatus.PENDING.value).count()

        # By escalation
        by_escalation = dict(
            query.with_entities(Ticket.escalation_level, func.count(Ticket.id))
            .group_by(Ticket.escalation_level)
            .all()
        )

        escalated_count = query.filter(Ticket.escalation_level != EscalationLevel.NONE.value).count()

        merged_count = query.filter(Ticket.is_merged == True).count()

        return {
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "in_progress_tickets": in_progress_tickets,
            "pending_tickets": pending_tickets,
            "resolved_tickets": resolved_tickets,
            "closed_tickets": closed_tickets,
            "by_priority": {k.value: v for k, v in by_priority.items()},
            "by_category": {k.value: v for k, v in by_category.items()},
            "by_escalation": {k.value: v for k, v in by_escalation.items()},
            "escalated_count": escalated_count,
            "merged_count": merged_count,
        }

    def get_response_time_metrics(
        self, db: Session, *, start_date: date = None, end_date: date = None
    ) -> Dict:
        """Get response and resolution time metrics"""
        query = db.query(Ticket).filter(Ticket.resolved_at.isnot(None))

        if start_date and end_date:
            query = query.filter(
                and_(Ticket.created_at >= start_date, Ticket.created_at <= end_date)
            )

        # Calculate resolution times
        resolution_times = []
        for ticket in query.all():
            if ticket.resolved_at and ticket.created_at:
                delta = ticket.resolved_at - ticket.created_at
                hours = delta.total_seconds() / 3600
                resolution_times.append(hours)

        if resolution_times:
            avg_resolution = sum(resolution_times) / len(resolution_times)
            sorted_times = sorted(resolution_times)
            median_resolution = sorted_times[len(sorted_times) // 2]
        else:
            avg_resolution = 0.0
            median_resolution = 0.0

        return {
            "avg_first_response_minutes": 0.0,  # TODO: Calculate from first reply
            "median_first_response_minutes": 0.0,
            "avg_resolution_time_hours": round(avg_resolution, 2),
            "median_resolution_time_hours": round(median_resolution, 2),
        }

    def get_agent_performance(
        self, db: Session, *, start_date: date = None, end_date: date = None
    ) -> List[Dict]:
        """Get agent performance metrics"""
        query = db.query(Ticket)

        if start_date and end_date:
            query = query.filter(
                and_(Ticket.created_at >= start_date, Ticket.created_at <= end_date)
            )

        # Group by assignee
        agent_stats = (
            query.filter(Ticket.assigned_to.isnot(None))
            .with_entities(
                Ticket.assigned_to,
                func.count(Ticket.id).label("total"),
                func.sum(func.case((Ticket.status == TicketStatus.RESOLVED.value, 1), else_=0)).label(
                    "resolved"
                ),
            )
            .group_by(Ticket.assigned_to)
            .all()
        )

        results = []
        for agent_id, total, resolved in agent_stats:
            results.append(
                {
                    "agent_id": agent_id,
                    "agent_name": f"Agent {agent_id}",  # TODO: Get actual name
                    "tickets_assigned": total,
                    "tickets_resolved": resolved or 0,
                    "avg_resolution_time_hours": 0.0,  # TODO: Calculate
                    "customer_satisfaction_score": None,
                }
            )

        return results

    def get_customer_satisfaction(
        self, db: Session, *, start_date: date = None, end_date: date = None
    ) -> Dict:
        """Get customer satisfaction metrics"""
        query = db.query(Feedback).filter(Feedback.rating.isnot(None))

        if start_date and end_date:
            query = query.filter(
                and_(Feedback.created_at >= start_date, Feedback.created_at <= end_date)
            )

        total_feedbacks = query.count()
        avg_rating = query.with_entities(func.avg(Feedback.rating)).scalar() or 0.0

        positive_count = query.filter(Feedback.rating >= 4).count()
        negative_count = query.filter(Feedback.rating <= 2).count()

        satisfaction_percentage = (
            (positive_count / total_feedbacks * 100) if total_feedbacks > 0 else 0.0
        )

        return {
            "total_feedbacks": total_feedbacks,
            "average_rating": round(avg_rating, 2),
            "positive_feedback_count": positive_count,
            "negative_feedback_count": negative_count,
            "satisfaction_percentage": round(satisfaction_percentage, 2),
        }

    def get_trend_data(self, db: Session, *, start_date: date, end_date: date) -> List[Dict]:
        """Get daily trend data for tickets"""
        trends = []
        current_date = start_date

        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)

            ticket_count = (
                db.query(Ticket)
                .filter(and_(Ticket.created_at >= current_date, Ticket.created_at < next_date))
                .count()
            )

            resolved_count = (
                db.query(Ticket)
                .filter(and_(Ticket.resolved_at >= current_date, Ticket.resolved_at < next_date))
                .count()
            )

            trends.append(
                {
                    "date": current_date,
                    "ticket_count": ticket_count,
                    "resolved_count": resolved_count,
                    "avg_resolution_hours": 0.0,  # TODO: Calculate
                }
            )

            current_date = next_date

        return trends

    def get_kb_analytics(self, db: Session) -> Dict:
        """Get knowledge base analytics"""
        from app.models.support import ArticleStatus

        total_articles = db.query(KBArticle).count()
        published_articles = (
            db.query(KBArticle).filter(KBArticle.status == ArticleStatus.PUBLISHED.value).count()
        )

        total_views = db.query(func.sum(KBArticle.view_count)).scalar() or 0

        # Average helpfulness
        articles_with_votes = (
            db.query(KBArticle)
            .filter((KBArticle.helpful_count + KBArticle.not_helpful_count) > 0)
            .all()
        )

        if articles_with_votes:
            avg_helpfulness = sum(
                a.helpful_count / (a.helpful_count + a.not_helpful_count)
                for a in articles_with_votes
            ) / len(articles_with_votes)
        else:
            avg_helpfulness = 0.0

        # Top articles
        top_articles = (
            db.query(KBArticle)
            .filter(KBArticle.status == ArticleStatus.PUBLISHED.value)
            .order_by(KBArticle.view_count.desc())
            .limit(10)
            .all()
        )

        # By category
        articles_by_category = dict(
            db.query(KBArticle.category, func.count(KBArticle.id))
            .filter(KBArticle.status == ArticleStatus.PUBLISHED.value)
            .group_by(KBArticle.category)
            .all()
        )

        return {
            "total_articles": total_articles,
            "published_articles": published_articles,
            "total_views": total_views,
            "avg_helpfulness_score": round(avg_helpfulness, 2),
            "top_articles": [
                {"id": a.id, "title": a.title, "views": a.view_count} for a in top_articles
            ],
            "articles_by_category": articles_by_category,
        }

    def get_chat_analytics(
        self, db: Session, *, start_date: date = None, end_date: date = None
    ) -> Dict:
        """Get live chat analytics"""
        from app.models.support import ChatMessage, ChatStatus

        query = db.query(ChatSession)

        if start_date and end_date:
            query = query.filter(
                and_(ChatSession.created_at >= start_date, ChatSession.created_at <= end_date)
            )

        total_sessions = query.count()
        active_sessions = query.filter(ChatSession.status == ChatStatus.ACTIVE.value).count()

        # Calculate wait times
        waiting_sessions = query.filter(
            and_(ChatSession.started_at.isnot(None), ChatSession.created_at.isnot(None))
        ).all()

        wait_times = [
            (s.started_at - s.created_at).total_seconds() / 60
            for s in waiting_sessions
            if s.started_at and s.created_at
        ]
        avg_wait_time = sum(wait_times) / len(wait_times) if wait_times else 0.0

        # Calculate chat durations
        ended_sessions = query.filter(
            and_(ChatSession.ended_at.isnot(None), ChatSession.started_at.isnot(None))
        ).all()

        durations = [
            (s.ended_at - s.started_at).total_seconds() / 60
            for s in ended_sessions
            if s.ended_at and s.started_at
        ]
        avg_duration = sum(durations) / len(durations) if durations else 0.0

        # Total messages
        total_messages = db.query(ChatMessage).count()

        # Sessions by agent
        sessions_by_agent = dict(
            query.filter(ChatSession.agent_id.isnot(None))
            .with_entities(ChatSession.agent_id, func.count(ChatSession.id))
            .group_by(ChatSession.agent_id)
            .all()
        )

        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "avg_wait_time_minutes": round(avg_wait_time, 2),
            "avg_chat_duration_minutes": round(avg_duration, 2),
            "total_messages": total_messages,
            "sessions_by_agent": {str(k): v for k, v in sessions_by_agent.items()},
        }

    def get_sla_metrics(
        self, db: Session, *, start_date: date = None, end_date: date = None
    ) -> Dict:
        """Get SLA compliance metrics"""
        query = db.query(Ticket).filter(Ticket.sla_due_at.isnot(None))

        if start_date and end_date:
            query = query.filter(
                and_(Ticket.created_at >= start_date, Ticket.created_at <= end_date)
            )

        total_with_sla = query.count()
        sla_breached = query.filter(Ticket.sla_breached == True).count()
        sla_met = total_with_sla - sla_breached

        compliance_rate = (sla_met / total_with_sla * 100) if total_with_sla > 0 else 0.0

        # At risk tickets
        now = datetime.now(timezone.utc)
        hours_threshold = timedelta(hours=2)
        at_risk_count = query.filter(
            and_(
                Ticket.sla_breached == False,
                Ticket.sla_due_at <= now + hours_threshold,
                Ticket.status.in_(
                    [TicketStatus.OPEN.value, TicketStatus.IN_PROGRESS.value, TicketStatus.PENDING.value]
                ),
            )
        ).count()

        # SLA by priority
        by_priority = {}
        for priority in TicketPriority:
            priority_query = query.filter(Ticket.priority == priority.value)
            priority_total = priority_query.count()
            priority_breached = priority_query.filter(Ticket.sla_breached == True).count()
            by_priority[priority.value] = {
                "total": priority_total,
                "breached": priority_breached,
                "met": priority_total - priority_breached,
                "compliance_rate": round(
                    (
                        ((priority_total - priority_breached) / priority_total * 100)
                        if priority_total > 0
                        else 0.0
                    ),
                    2,
                ),
            }

        return {
            "total_with_sla": total_with_sla,
            "sla_met": sla_met,
            "sla_breached": sla_breached,
            "compliance_rate": round(compliance_rate, 2),
            "avg_time_to_breach_hours": 0.0,  # TODO: Calculate
            "at_risk_count": at_risk_count,
            "by_priority": by_priority,
        }

    def get_escalation_analytics(
        self, db: Session, *, start_date: date = None, end_date: date = None
    ) -> Dict:
        """Get escalation analytics"""
        query = db.query(Ticket).filter(Ticket.escalation_level != EscalationLevel.NONE.value)

        if start_date and end_date:
            query = query.filter(
                and_(Ticket.created_at >= start_date, Ticket.created_at <= end_date)
            )

        total_escalated = query.count()

        # By level
        by_level = dict(
            query.with_entities(Ticket.escalation_level, func.count(Ticket.id))
            .group_by(Ticket.escalation_level)
            .all()
        )

        # Total tickets for rate calculation
        total_tickets = db.query(Ticket)
        if start_date and end_date:
            total_tickets = total_tickets.filter(
                and_(Ticket.created_at >= start_date, Ticket.created_at <= end_date)
            )
        total_count = total_tickets.count()

        escalation_rate = (total_escalated / total_count * 100) if total_count > 0 else 0.0

        return {
            "total_escalated": total_escalated,
            "by_level": {k.value: v for k, v in by_level.items()},
            "avg_time_to_escalate_hours": 0.0,  # TODO: Calculate
            "escalation_rate": round(escalation_rate, 2),
            "top_reasons": [],  # TODO: Get top escalation reasons
        }


# Create service instance
support_analytics_service = SupportAnalyticsService()
