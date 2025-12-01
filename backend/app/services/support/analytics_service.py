"""Support Analytics Service"""
from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, date, timedelta

from app.models.support import (
    Ticket, TicketStatus, Feedback, KBArticle, ChatSession
)


class SupportAnalyticsService:
    """Service for support analytics and reporting"""

    def get_ticket_metrics(
        self,
        db: Session,
        *,
        start_date: date = None,
        end_date: date = None
    ) -> Dict:
        """Get ticket volume and status metrics"""
        query = db.query(Ticket)

        if start_date and end_date:
            query = query.filter(
                and_(
                    Ticket.created_at >= start_date,
                    Ticket.created_at <= end_date
                )
            )

        total_tickets = query.count()

        # By status
        open_tickets = query.filter(Ticket.status == TicketStatus.OPEN).count()
        in_progress_tickets = query.filter(Ticket.status == TicketStatus.IN_PROGRESS).count()
        resolved_tickets = query.filter(Ticket.status == TicketStatus.RESOLVED).count()
        closed_tickets = query.filter(Ticket.status == TicketStatus.CLOSED).count()

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

        return {
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "in_progress_tickets": in_progress_tickets,
            "resolved_tickets": resolved_tickets,
            "closed_tickets": closed_tickets,
            "by_priority": {k.value: v for k, v in by_priority.items()},
            "by_category": {k.value: v for k, v in by_category.items()},
        }

    def get_response_time_metrics(
        self,
        db: Session,
        *,
        start_date: date = None,
        end_date: date = None
    ) -> Dict:
        """Get response and resolution time metrics"""
        query = db.query(Ticket).filter(Ticket.resolved_at.isnot(None))

        if start_date and end_date:
            query = query.filter(
                and_(
                    Ticket.created_at >= start_date,
                    Ticket.created_at <= end_date
                )
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
        self,
        db: Session,
        *,
        start_date: date = None,
        end_date: date = None
    ) -> List[Dict]:
        """Get agent performance metrics"""
        query = db.query(Ticket)

        if start_date and end_date:
            query = query.filter(
                and_(
                    Ticket.created_at >= start_date,
                    Ticket.created_at <= end_date
                )
            )

        # Group by assignee
        agent_stats = (
            query.filter(Ticket.assigned_to.isnot(None))
            .with_entities(
                Ticket.assigned_to,
                func.count(Ticket.id).label("total"),
                func.sum(
                    func.case(
                        (Ticket.status == TicketStatus.RESOLVED, 1),
                        else_=0
                    )
                ).label("resolved")
            )
            .group_by(Ticket.assigned_to)
            .all()
        )

        results = []
        for agent_id, total, resolved in agent_stats:
            results.append({
                "agent_id": agent_id,
                "agent_name": f"Agent {agent_id}",  # TODO: Get actual name
                "tickets_assigned": total,
                "tickets_resolved": resolved or 0,
                "avg_resolution_time_hours": 0.0,  # TODO: Calculate
                "customer_satisfaction_score": None,
            })

        return results

    def get_customer_satisfaction(
        self,
        db: Session,
        *,
        start_date: date = None,
        end_date: date = None
    ) -> Dict:
        """Get customer satisfaction metrics"""
        query = db.query(Feedback).filter(Feedback.rating.isnot(None))

        if start_date and end_date:
            query = query.filter(
                and_(
                    Feedback.created_at >= start_date,
                    Feedback.created_at <= end_date
                )
            )

        total_feedbacks = query.count()
        avg_rating = query.with_entities(func.avg(Feedback.rating)).scalar() or 0.0

        positive_count = query.filter(Feedback.rating >= 4).count()
        negative_count = query.filter(Feedback.rating <= 2).count()

        satisfaction_percentage = (positive_count / total_feedbacks * 100) if total_feedbacks > 0 else 0.0

        return {
            "total_feedbacks": total_feedbacks,
            "average_rating": round(avg_rating, 2),
            "positive_feedback_count": positive_count,
            "negative_feedback_count": negative_count,
            "satisfaction_percentage": round(satisfaction_percentage, 2),
        }

    def get_trend_data(
        self,
        db: Session,
        *,
        start_date: date,
        end_date: date
    ) -> List[Dict]:
        """Get daily trend data for tickets"""
        trends = []
        current_date = start_date

        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)

            ticket_count = db.query(Ticket).filter(
                and_(
                    Ticket.created_at >= current_date,
                    Ticket.created_at < next_date
                )
            ).count()

            resolved_count = db.query(Ticket).filter(
                and_(
                    Ticket.resolved_at >= current_date,
                    Ticket.resolved_at < next_date
                )
            ).count()

            trends.append({
                "date": current_date,
                "ticket_count": ticket_count,
                "resolved_count": resolved_count,
                "avg_resolution_hours": 0.0,  # TODO: Calculate
            })

            current_date = next_date

        return trends

    def get_kb_analytics(self, db: Session) -> Dict:
        """Get knowledge base analytics"""
        from app.models.support import ArticleStatus

        total_articles = db.query(KBArticle).count()
        published_articles = db.query(KBArticle).filter(
            KBArticle.status == ArticleStatus.PUBLISHED
        ).count()

        total_views = db.query(func.sum(KBArticle.view_count)).scalar() or 0

        # Average helpfulness
        articles_with_votes = db.query(KBArticle).filter(
            (KBArticle.helpful_count + KBArticle.not_helpful_count) > 0
        ).all()

        if articles_with_votes:
            avg_helpfulness = sum(
                a.helpful_count / (a.helpful_count + a.not_helpful_count)
                for a in articles_with_votes
            ) / len(articles_with_votes)
        else:
            avg_helpfulness = 0.0

        # Top articles
        top_articles = db.query(KBArticle).filter(
            KBArticle.status == ArticleStatus.PUBLISHED
        ).order_by(KBArticle.view_count.desc()).limit(10).all()

        # By category
        articles_by_category = dict(
            db.query(KBArticle.category, func.count(KBArticle.id))
            .filter(KBArticle.status == ArticleStatus.PUBLISHED)
            .group_by(KBArticle.category)
            .all()
        )

        return {
            "total_articles": total_articles,
            "published_articles": published_articles,
            "total_views": total_views,
            "avg_helpfulness_score": round(avg_helpfulness, 2),
            "top_articles": [
                {"id": a.id, "title": a.title, "views": a.view_count}
                for a in top_articles
            ],
            "articles_by_category": articles_by_category,
        }

    def get_chat_analytics(
        self,
        db: Session,
        *,
        start_date: date = None,
        end_date: date = None
    ) -> Dict:
        """Get live chat analytics"""
        from app.models.support import ChatStatus, ChatMessage

        query = db.query(ChatSession)

        if start_date and end_date:
            query = query.filter(
                and_(
                    ChatSession.created_at >= start_date,
                    ChatSession.created_at <= end_date
                )
            )

        total_sessions = query.count()
        active_sessions = query.filter(ChatSession.status == ChatStatus.ACTIVE).count()

        # Calculate wait times
        waiting_sessions = query.filter(
            and_(
                ChatSession.started_at.isnot(None),
                ChatSession.created_at.isnot(None)
            )
        ).all()

        wait_times = [
            (s.started_at - s.created_at).total_seconds() / 60
            for s in waiting_sessions
            if s.started_at and s.created_at
        ]
        avg_wait_time = sum(wait_times) / len(wait_times) if wait_times else 0.0

        # Calculate chat durations
        ended_sessions = query.filter(
            and_(
                ChatSession.ended_at.isnot(None),
                ChatSession.started_at.isnot(None)
            )
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


# Create service instance
support_analytics_service = SupportAnalyticsService()
