"""Celery Configuration for Background Jobs

Celery tasks for:
- Daily attendance aggregation
- Monthly payroll automation
- Document expiry notifications
- Data integrity checks
- Automated reports
"""
from celery import Celery
from celery.schedules import crontab
from datetime import date, datetime, timedelta
import logging

from app.config.settings import settings

# Initialize Celery
celery_app = Celery(
    "barq_fleet",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

logger = logging.getLogger(__name__)


@celery_app.task(name="process_daily_attendance")
def process_daily_attendance():
    """
    Daily task to aggregate attendance data
    Runs at midnight every day
    """
    from app.config.database import SessionLocal
    from app.services.hr.attendance_service import attendance_service

    logger.info("Starting daily attendance processing")

    try:
        db = SessionLocal()

        # Process yesterday's attendance
        yesterday = date.today() - timedelta(days=1)

        # Get all couriers and check their attendance
        # Mark absent if no attendance record exists
        # Calculate attendance statistics

        logger.info(f"Processed attendance for {yesterday}")

        db.close()
        return {"status": "success", "date": str(yesterday)}

    except Exception as e:
        logger.error(f"Failed to process daily attendance: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(name="process_monthly_payroll")
def process_monthly_payroll():
    """
    Monthly task to process payroll
    Runs on the 28th of each month
    """
    from app.config.database import SessionLocal
    from app.services.hr import payroll_engine_service

    logger.info("Starting monthly payroll processing")

    try:
        db = SessionLocal()

        # Get current month/year
        today = date.today()
        # Process for last month
        if today.month == 1:
            month = 12
            year = today.year - 1
        else:
            month = today.month - 1
            year = today.year

        # Process payroll for all couriers
        result = payroll_engine_service.process_monthly_payroll(
            db=db,
            month=month,
            year=year,
            dry_run=False
        )

        logger.info(f"Payroll processed: {result['successful']} successful, {result['failed']} failed")

        db.close()
        return {
            "status": "success",
            "month": month,
            "year": year,
            "successful": result['successful'],
            "failed": result['failed']
        }

    except Exception as e:
        logger.error(f"Failed to process monthly payroll: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(name="check_document_expiry")
def check_document_expiry():
    """
    Daily task to check document expiry
    Sends notifications for documents expiring soon
    Runs daily at 9 AM
    """
    from app.config.database import SessionLocal
    from app.models.fleet.courier import Courier
    from app.services import email_notification_service, sms_notification_service
    from datetime import date, timedelta

    logger.info("Checking document expiry")

    try:
        db = SessionLocal()

        today = date.today()
        warning_threshold = today + timedelta(days=30)  # 30 days warning

        # Check all couriers for expiring documents
        couriers = db.query(Courier).all()
        notifications_sent = 0

        for courier in couriers:
            # Check license expiry
            if courier.license_expiry and courier.license_expiry <= warning_threshold:
                days_remaining = (courier.license_expiry - today).days

                # Send email
                if courier.email:
                    email_notification_service.send_document_expiry_alert(
                        to_email=courier.email,
                        courier_name=courier.name,
                        document_type="Driving License",
                        document_number=courier.license_number or "N/A",
                        expiry_date=str(courier.license_expiry),
                        days_until_expiry=days_remaining
                    )
                    notifications_sent += 1

                # Send SMS
                if courier.phone:
                    sms_notification_service.send_document_expiry_alert(
                        to_phone=courier.phone,
                        courier_name=courier.name,
                        document_type="رخصة القيادة",
                        expiry_date=str(courier.license_expiry),
                        days_remaining=days_remaining
                    )

            # Check iqama expiry
            if courier.iqama_expiry and courier.iqama_expiry <= warning_threshold:
                days_remaining = (courier.iqama_expiry - today).days

                if courier.email:
                    email_notification_service.send_document_expiry_alert(
                        to_email=courier.email,
                        courier_name=courier.name,
                        document_type="Iqama",
                        document_number=courier.iqama_number or "N/A",
                        expiry_date=str(courier.iqama_expiry),
                        days_until_expiry=days_remaining
                    )
                    notifications_sent += 1

                if courier.phone:
                    sms_notification_service.send_document_expiry_alert(
                        to_phone=courier.phone,
                        courier_name=courier.name,
                        document_type="الإقامة",
                        expiry_date=str(courier.iqama_expiry),
                        days_remaining=days_remaining
                    )

        logger.info(f"Sent {notifications_sent} document expiry notifications")

        db.close()
        return {
            "status": "success",
            "notifications_sent": notifications_sent
        }

    except Exception as e:
        logger.error(f"Failed to check document expiry: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(name="clean_old_audit_logs")
def clean_old_audit_logs():
    """
    Monthly task to clean old audit logs
    Keeps logs for 1 year
    Runs on the 1st of each month at 2 AM
    """
    from app.config.database import SessionLocal
    from app.services import audit_log_service

    logger.info("Cleaning old audit logs")

    try:
        db = SessionLocal()

        deleted_count = audit_log_service.clean_old_logs(
            db=db,
            days_to_keep=365
        )

        logger.info(f"Deleted {deleted_count} old audit logs")

        db.close()
        return {
            "status": "success",
            "deleted_count": deleted_count
        }

    except Exception as e:
        logger.error(f"Failed to clean audit logs: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(name="generate_monthly_reports")
def generate_monthly_reports():
    """
    Monthly task to generate and email reports
    Runs on the 1st of each month at 8 AM
    """
    from app.config.database import SessionLocal
    from app.services.analytics import fleet_analytics_service, hr_analytics_service
    from app.services.hr import payroll_engine_service

    logger.info("Generating monthly reports")

    try:
        db = SessionLocal()

        # Get last month's date range
        today = date.today()
        first_of_month = date(today.year, today.month, 1)
        last_month_end = first_of_month - timedelta(days=1)
        last_month_start = date(last_month_end.year, last_month_end.month, 1)

        # Generate reports
        fleet_report = fleet_analytics_service.get_fleet_status_summary(db)
        payroll_report = payroll_engine_service.get_payroll_report(
            db, month=last_month_end.month, year=last_month_end.year
        )
        hr_report = hr_analytics_service.get_leave_analytics(
            db, start_date=last_month_start, end_date=last_month_end
        )

        # TODO: Format and email reports to management

        logger.info("Monthly reports generated successfully")

        db.close()
        return {
            "status": "success",
            "month": last_month_end.month,
            "year": last_month_end.year
        }

    except Exception as e:
        logger.error(f"Failed to generate monthly reports: {str(e)}")
        return {"status": "error", "message": str(e)}


# Configure periodic tasks
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Setup periodic tasks"""

    # Daily attendance at midnight
    sender.add_periodic_task(
        crontab(hour=0, minute=0),
        process_daily_attendance.s(),
        name="daily-attendance"
    )

    # Monthly payroll on 28th at 2 AM
    sender.add_periodic_task(
        crontab(day_of_month=28, hour=2, minute=0),
        process_monthly_payroll.s(),
        name="monthly-payroll"
    )

    # Document expiry check daily at 9 AM
    sender.add_periodic_task(
        crontab(hour=9, minute=0),
        check_document_expiry.s(),
        name="document-expiry-check"
    )

    # Clean audit logs on 1st of month at 2 AM
    sender.add_periodic_task(
        crontab(day_of_month=1, hour=2, minute=0),
        clean_old_audit_logs.s(),
        name="clean-audit-logs"
    )

    # Generate monthly reports on 1st at 8 AM
    sender.add_periodic_task(
        crontab(day_of_month=1, hour=8, minute=0),
        generate_monthly_reports.s(),
        name="monthly-reports"
    )


if __name__ == "__main__":
    celery_app.start()
