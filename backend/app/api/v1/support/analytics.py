"""Support Analytics API Routes"""
from typing import Dict
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.support import (
    TicketMetrics, SLAMetrics, ResponseTimeMetrics, CustomerSatisfactionMetrics,
    SupportAnalytics, EscalationAnalytics, KBAnalytics, ChatAnalytics
)
from app.services.support import support_analytics_service


router = APIRouter()


@router.get("/tickets", response_model=TicketMetrics)
def get_ticket_metrics(
    db: Session = Depends(get_db),
    start_date: date = Query(None, description="Start date for filtering"),
    end_date: date = Query(None, description="End date for filtering"),
    current_user: User = Depends(get_current_user),
):
    """Get ticket volume and status metrics"""
    return support_analytics_service.get_ticket_metrics(
        db,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/response-times", response_model=ResponseTimeMetrics)
def get_response_time_metrics(
    db: Session = Depends(get_db),
    start_date: date = Query(None, description="Start date for filtering"),
    end_date: date = Query(None, description="End date for filtering"),
    current_user: User = Depends(get_current_user),
):
    """Get response and resolution time metrics"""
    return support_analytics_service.get_response_time_metrics(
        db,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/agent-performance")
def get_agent_performance(
    db: Session = Depends(get_db),
    start_date: date = Query(None, description="Start date for filtering"),
    end_date: date = Query(None, description="End date for filtering"),
    current_user: User = Depends(get_current_user),
):
    """Get agent performance metrics"""
    return support_analytics_service.get_agent_performance(
        db,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/customer-satisfaction", response_model=CustomerSatisfactionMetrics)
def get_customer_satisfaction(
    db: Session = Depends(get_db),
    start_date: date = Query(None, description="Start date for filtering"),
    end_date: date = Query(None, description="End date for filtering"),
    current_user: User = Depends(get_current_user),
):
    """Get customer satisfaction metrics"""
    return support_analytics_service.get_customer_satisfaction(
        db,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/trends")
def get_trend_data(
    db: Session = Depends(get_db),
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    current_user: User = Depends(get_current_user),
):
    """Get daily trend data for tickets"""
    return support_analytics_service.get_trend_data(
        db,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/knowledge-base", response_model=KBAnalytics)
def get_kb_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get knowledge base analytics"""
    return support_analytics_service.get_kb_analytics(db)


@router.get("/chat", response_model=ChatAnalytics)
def get_chat_analytics(
    db: Session = Depends(get_db),
    start_date: date = Query(None, description="Start date for filtering"),
    end_date: date = Query(None, description="End date for filtering"),
    current_user: User = Depends(get_current_user),
):
    """Get live chat analytics"""
    return support_analytics_service.get_chat_analytics(
        db,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/sla", response_model=SLAMetrics)
def get_sla_metrics(
    db: Session = Depends(get_db),
    start_date: date = Query(None, description="Start date for filtering"),
    end_date: date = Query(None, description="End date for filtering"),
    current_user: User = Depends(get_current_user),
):
    """Get SLA compliance metrics"""
    return support_analytics_service.get_sla_metrics(
        db,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/escalations", response_model=EscalationAnalytics)
def get_escalation_analytics(
    db: Session = Depends(get_db),
    start_date: date = Query(None, description="Start date for filtering"),
    end_date: date = Query(None, description="End date for filtering"),
    current_user: User = Depends(get_current_user),
):
    """Get escalation analytics"""
    return support_analytics_service.get_escalation_analytics(
        db,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/dashboard")
def get_support_dashboard(
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    current_user: User = Depends(get_current_user),
):
    """
    Get comprehensive support analytics dashboard
    Combines all key metrics for overview
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    return {
        "period": {"start_date": start_date, "end_date": end_date, "days": days},
        "tickets": support_analytics_service.get_ticket_metrics(
            db, start_date=start_date, end_date=end_date
        ),
        "response_times": support_analytics_service.get_response_time_metrics(
            db, start_date=start_date, end_date=end_date
        ),
        "sla": support_analytics_service.get_sla_metrics(
            db, start_date=start_date, end_date=end_date
        ),
        "escalations": support_analytics_service.get_escalation_analytics(
            db, start_date=start_date, end_date=end_date
        ),
        "customer_satisfaction": support_analytics_service.get_customer_satisfaction(
            db, start_date=start_date, end_date=end_date
        ),
        "knowledge_base": support_analytics_service.get_kb_analytics(db),
        "chat": support_analytics_service.get_chat_analytics(
            db, start_date=start_date, end_date=end_date
        ),
    }
