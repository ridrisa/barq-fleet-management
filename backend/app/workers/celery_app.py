"""
Celery Application Configuration
Main Celery app instance and configuration
"""

import logging

from celery import Celery
from celery.schedules import crontab

from app.core.performance_config import performance_config

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "barq_fleet",
    broker=performance_config.background_jobs.broker_url,
    backend=performance_config.background_jobs.result_backend,
)

# Configure Celery
celery_app.conf.update(
    # Task execution settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Task time limits
    task_soft_time_limit=performance_config.background_jobs.task_soft_time_limit,
    task_time_limit=performance_config.background_jobs.task_time_limit,
    # Task retry settings
    task_acks_late=True,  # Acknowledge task after execution
    task_reject_on_worker_lost=True,
    task_default_retry_delay=performance_config.background_jobs.task_default_retry_delay,
    # Worker settings
    worker_prefetch_multiplier=performance_config.background_jobs.worker_prefetch_multiplier,
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks (memory management)
    # Result backend settings
    result_expires=performance_config.background_jobs.result_expires,
    result_compression="gzip",
    # Task routing
    task_routes={
        "app.workers.tasks.send_email_task": {
            "queue": performance_config.background_jobs.high_priority_queue
        },
        "app.workers.tasks.generate_report_task": {
            "queue": performance_config.background_jobs.default_queue
        },
        "app.workers.tasks.aggregate_metrics_task": {
            "queue": performance_config.background_jobs.low_priority_queue
        },
        "app.workers.tasks.cleanup_old_data_task": {
            "queue": performance_config.background_jobs.low_priority_queue
        },
    },
    # Monitoring
    task_track_started=True,
    task_send_sent_event=True,
    # Periodic tasks (Celery Beat schedule)
    beat_schedule={
        # Aggregate metrics every 5 minutes
        "aggregate-metrics": {
            "task": "app.workers.tasks.aggregate_metrics_task",
            "schedule": crontab(minute="*/5"),
        },
        # Check SLA compliance every 15 minutes
        "check-sla-compliance": {
            "task": "app.workers.tasks.check_sla_compliance_task",
            "schedule": crontab(minute="*/15"),
        },
        # Cleanup old data daily at 2 AM
        "cleanup-old-data": {
            "task": "app.workers.tasks.cleanup_old_data_task",
            "schedule": crontab(hour=2, minute=0),
        },
        # Generate daily reports at 6 AM
        "daily-reports": {
            "task": "app.workers.tasks.generate_daily_reports_task",
            "schedule": crontab(hour=6, minute=0),
        },
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.workers"])

logger.info(
    f"Celery configured: broker={performance_config.background_jobs.broker_url}, "
    f"backend={performance_config.background_jobs.result_backend}"
)


# Task event handlers
@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery configuration"""
    logger.info(f"Request: {self.request!r}")
    return "Debug task completed"


__all__ = ["celery_app"]
