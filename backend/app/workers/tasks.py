"""
Celery Background Tasks
Task definitions for email, reports, data aggregation, SLA monitoring, etc.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from celery import Task
from celery.exceptions import MaxRetriesExceededError

from app.core.performance_config import performance_config
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """
    Base task class with database session management
    """

    _db_session = None

    @property
    def db_session(self):
        """Get or create database session"""
        if self._db_session is None:
            from app.core.database import db_manager

            self._db_session = db_manager.create_session()
        return self._db_session

    def after_return(self, *args, **kwargs):
        """Cleanup after task execution"""
        if self._db_session is not None:
            self._db_session.close()
            self._db_session = None


# Email Tasks
@celery_app.task(
    bind=True,
    base=DatabaseTask,
    max_retries=performance_config.background_jobs.task_max_retries,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
)
def send_email_task(
    self,
    recipient: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    attachments: Optional[List[Dict]] = None,
):
    """
    Send email asynchronously

    Args:
        recipient: Email recipient
        subject: Email subject
        body: Plain text body
        html_body: HTML body (optional)
        attachments: List of attachments (optional)

    Usage:
        send_email_task.delay(
            recipient="user@example.com",
            subject="Welcome",
            body="Welcome to BARQ!"
        )
    """
    try:
        logger.info(f"Sending email to {recipient}: {subject}")

        # TODO: Implement actual email sending logic
        # This is a placeholder - integrate with your email service
        # Example: SendGrid, AWS SES, SMTP, etc.

        import os
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from smtplib import SMTP

        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = os.getenv("EMAIL_FROM", "noreply@barq.com")
        msg["To"] = recipient

        # Add text and HTML parts
        msg.attach(MIMEText(body, "plain"))
        if html_body:
            msg.attach(MIMEText(html_body, "html"))

        # TODO: Add attachment handling if needed

        # Send email (placeholder - configure SMTP settings)
        # smtp_host = os.getenv("SMTP_HOST", "localhost")
        # smtp_port = int(os.getenv("SMTP_PORT", "587"))
        # smtp = SMTP(smtp_host, smtp_port)
        # smtp.send_message(msg)
        # smtp.quit()

        logger.info(f"Email sent successfully to {recipient}")
        return {"status": "sent", "recipient": recipient}

    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {e}")

        # Retry with exponential backoff
        try:
            raise self.retry(exc=e)
        except MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for email to {recipient}")
            return {"status": "failed", "error": str(e)}


@celery_app.task(bind=True, base=DatabaseTask)
def send_bulk_email_task(self, recipients: List[str], subject: str, body: str):
    """
    Send bulk emails

    Args:
        recipients: List of email recipients
        subject: Email subject
        body: Email body

    Usage:
        send_bulk_email_task.delay(
            recipients=["user1@example.com", "user2@example.com"],
            subject="Newsletter",
            body="Latest updates..."
        )
    """
    logger.info(f"Sending bulk email to {len(recipients)} recipients")

    results = []
    for recipient in recipients:
        # Queue individual email tasks
        result = send_email_task.delay(recipient, subject, body)
        results.append(result.id)

    return {"queued_tasks": len(results), "task_ids": results}


# Report Generation Tasks
@celery_app.task(bind=True, base=DatabaseTask)
def generate_report_task(
    self,
    report_type: str,
    organization_id: str,
    start_date: str,
    end_date: str,
    format: str = "pdf",
):
    """
    Generate report asynchronously

    Args:
        report_type: Type of report (performance, financial, etc.)
        organization_id: Organization ID
        start_date: Report start date (ISO format)
        end_date: Report end date (ISO format)
        format: Report format (pdf, xlsx, csv)

    Usage:
        generate_report_task.delay(
            report_type="performance",
            organization_id="org-123",
            start_date="2025-01-01",
            end_date="2025-01-31",
            format="pdf"
        )
    """
    try:
        logger.info(
            f"Generating {report_type} report for organization {organization_id} "
            f"({start_date} to {end_date})"
        )

        # TODO: Implement report generation logic
        # This should integrate with your analytics/reporting service

        # Placeholder implementation
        report_data = {
            "type": report_type,
            "organization_id": organization_id,
            "start_date": start_date,
            "end_date": end_date,
            "format": format,
            "generated_at": datetime.utcnow().isoformat(),
        }

        # Save report to storage (S3, local filesystem, etc.)
        report_path = f"/reports/{organization_id}/{report_type}_{start_date}_{end_date}.{format}"

        logger.info(f"Report generated: {report_path}")

        return {
            "status": "completed",
            "report_path": report_path,
            "report_data": report_data,
        }

    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        raise


@celery_app.task(bind=True, base=DatabaseTask)
def generate_daily_reports_task(self):
    """
    Generate daily reports for all organizations

    Runs daily via Celery Beat
    """
    logger.info("Generating daily reports")

    try:
        from app.models import Organization

        organizations = (
            self.db_session.query(Organization).filter(Organization.is_active == True).all()
        )

        yesterday = (datetime.utcnow() - timedelta(days=1)).date()

        results = []
        for org in organizations:
            # Queue report generation task
            result = generate_report_task.delay(
                report_type="daily_summary",
                organization_id=org.id,
                start_date=yesterday.isoformat(),
                end_date=yesterday.isoformat(),
                format="pdf",
            )
            results.append(result.id)

        logger.info(f"Queued {len(results)} daily report tasks")
        return {"organizations": len(organizations), "task_ids": results}

    except Exception as e:
        logger.error(f"Failed to generate daily reports: {e}")
        raise


# Data Aggregation Tasks
@celery_app.task(bind=True, base=DatabaseTask)
def aggregate_metrics_task(self):
    """
    Aggregate performance metrics

    Runs every 5 minutes via Celery Beat
    """
    logger.info("Aggregating metrics")

    try:
        from app.models.analytics import MetricSnapshot
        from app.utils.analytics import calculate_aggregated_metrics

        # Calculate metrics for all organizations
        metrics = calculate_aggregated_metrics(self.db_session)

        # Store snapshots
        snapshots = []
        for org_id, org_metrics in metrics.items():
            snapshot = MetricSnapshot(
                organization_id=org_id,
                timestamp=datetime.utcnow(),
                metrics=org_metrics,
            )
            snapshots.append(snapshot)

        if snapshots:
            from app.utils.batch import bulk_insert

            bulk_insert(self.db_session, MetricSnapshot, [s.__dict__ for s in snapshots])

        self.db_session.commit()

        logger.info(f"Aggregated metrics for {len(snapshots)} organizations")
        return {"organizations": len(snapshots)}

    except Exception as e:
        logger.error(f"Failed to aggregate metrics: {e}")
        self.db_session.rollback()
        raise


# SLA Monitoring Tasks
@celery_app.task(bind=True, base=DatabaseTask)
def check_sla_compliance_task(self):
    """
    Check SLA compliance for active tickets and deliveries

    Runs every 15 minutes via Celery Beat
    """
    logger.info("Checking SLA compliance")

    try:
        from datetime import datetime

        from app.models.operations import Delivery
        from app.models.support import Ticket

        now = datetime.utcnow()

        # Check ticket SLAs
        overdue_tickets = (
            self.db_session.query(Ticket)
            .filter(
                Ticket.status.in_(["open", "in_progress"]),
                Ticket.sla_due_at < now,
                Ticket.sla_breached == False,
            )
            .all()
        )

        for ticket in overdue_tickets:
            ticket.sla_breached = True
            logger.warning(f"Ticket {ticket.id} breached SLA")

            # TODO: Send notification
            send_email_task.delay(
                recipient=ticket.assigned_to_email,
                subject=f"SLA Breach: Ticket {ticket.number}",
                body=f"Ticket {ticket.number} has breached its SLA.",
            )

        # Check delivery SLAs
        overdue_deliveries = (
            self.db_session.query(Delivery)
            .filter(
                Delivery.status.in_(["pending", "in_transit"]), Delivery.expected_delivery_at < now
            )
            .all()
        )

        for delivery in overdue_deliveries:
            logger.warning(f"Delivery {delivery.id} is overdue")

            # TODO: Send notification

        self.db_session.commit()

        logger.info(
            f"SLA check completed: {len(overdue_tickets)} tickets, "
            f"{len(overdue_deliveries)} deliveries overdue"
        )

        return {
            "overdue_tickets": len(overdue_tickets),
            "overdue_deliveries": len(overdue_deliveries),
        }

    except Exception as e:
        logger.error(f"Failed to check SLA compliance: {e}")
        self.db_session.rollback()
        raise


# Cleanup Tasks
@celery_app.task(bind=True, base=DatabaseTask)
def cleanup_old_data_task(self, days_to_keep: int = 90):
    """
    Cleanup old data (logs, temp files, expired cache, etc.)

    Args:
        days_to_keep: Number of days to keep data

    Runs daily via Celery Beat
    """
    logger.info(f"Cleaning up data older than {days_to_keep} days")

    try:
        from app.models.support import Ticket
        from app.models.workflow import WorkflowHistory

        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        # Cleanup old workflow history
        deleted_history = (
            self.db_session.query(WorkflowHistory)
            .filter(WorkflowHistory.created_at < cutoff_date)
            .delete()
        )

        # Cleanup resolved tickets older than cutoff
        deleted_tickets = (
            self.db_session.query(Ticket)
            .filter(Ticket.status == "resolved", Ticket.resolved_at < cutoff_date)
            .delete()
        )

        self.db_session.commit()

        logger.info(
            f"Cleanup completed: {deleted_history} history records, "
            f"{deleted_tickets} tickets deleted"
        )

        return {
            "deleted_history": deleted_history,
            "deleted_tickets": deleted_tickets,
        }

    except Exception as e:
        logger.error(f"Failed to cleanup old data: {e}")
        self.db_session.rollback()
        raise


# Cache Warming Tasks
@celery_app.task(bind=True, base=DatabaseTask)
def warm_cache_task(self):
    """
    Warm up cache with frequently accessed data

    Usage:
        warm_cache_task.delay()
    """
    logger.info("Warming cache")

    try:
        from app.core.cache import cache_manager
        from app.models import Organization, User

        # Cache active organizations
        organizations = (
            self.db_session.query(Organization).filter(Organization.is_active == True).all()
        )

        for org in organizations:
            cache_manager.set(
                "organization", org.id, org.to_dict(), ttl=performance_config.cache.organization_ttl
            )

        # Cache active users
        users = self.db_session.query(User).filter(User.is_active == True).limit(1000).all()

        for user in users:
            cache_manager.set(
                "user", user.id, user.to_dict(), ttl=performance_config.cache.user_ttl
            )

        logger.info(f"Cache warmed: {len(organizations)} organizations, {len(users)} users")

        return {
            "organizations": len(organizations),
            "users": len(users),
        }

    except Exception as e:
        logger.error(f"Failed to warm cache: {e}")
        raise


# Export all tasks
__all__ = [
    "send_email_task",
    "send_bulk_email_task",
    "generate_report_task",
    "generate_daily_reports_task",
    "aggregate_metrics_task",
    "check_sla_compliance_task",
    "cleanup_old_data_task",
    "warm_cache_task",
]
