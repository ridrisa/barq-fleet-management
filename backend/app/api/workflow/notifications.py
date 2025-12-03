from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.crud.workflow import (
    notification_preference,
    workflow_notification,
    workflow_notification_template,
)
from app.models.workflow.notification import NotificationStatus
from app.schemas.workflow import (
    BulkNotificationRequest,
    NotificationPreferenceCreate,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
    NotificationSendRequest,
    NotificationStatistics,
    WorkflowNotificationCreate,
    WorkflowNotificationResponse,
    WorkflowNotificationTemplateCreate,
    WorkflowNotificationTemplateResponse,
    WorkflowNotificationTemplateUpdate,
    WorkflowNotificationUpdate,
)

router = APIRouter()


# ============================================================================
# Notification Templates
# ============================================================================


@router.get("/templates", response_model=List[WorkflowNotificationTemplateResponse])
def list_templates(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    """List all notification templates"""
    if is_active is not None:
        templates = (
            db.query(workflow_notification_template.model)
            .filter(workflow_notification_template.model.is_active == is_active)
            .offset(skip)
            .limit(limit)
            .all()
        )
    else:
        templates = workflow_notification_template.get_multi(db, skip=skip, limit=limit)
    return templates


@router.post("/templates", response_model=WorkflowNotificationTemplateResponse, status_code=201)
def create_template(
    template_in: WorkflowNotificationTemplateCreate,
    db: Session = Depends(get_db),
):
    """Create a new notification template"""
    template = workflow_notification_template.create(db, obj_in=template_in)
    return template


@router.get("/templates/{template_id}", response_model=WorkflowNotificationTemplateResponse)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
):
    """Get a notification template by ID"""
    template = workflow_notification_template.get(db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.put("/templates/{template_id}", response_model=WorkflowNotificationTemplateResponse)
def update_template(
    template_id: int,
    template_in: WorkflowNotificationTemplateUpdate,
    db: Session = Depends(get_db),
):
    """Update a notification template"""
    template = workflow_notification_template.get(db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    template = workflow_notification_template.update(db, db_obj=template, obj_in=template_in)
    return template


@router.delete("/templates/{template_id}", status_code=204)
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
):
    """Delete a notification template"""
    template = workflow_notification_template.get(db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    workflow_notification_template.remove(db, id=template_id)
    return None


# ============================================================================
# Notifications
# ============================================================================


@router.get("/", response_model=List[WorkflowNotificationResponse])
def list_notifications(
    recipient_id: Optional[int] = Query(None),
    status: Optional[NotificationStatus] = Query(None),
    unread_only: bool = Query(False),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List notifications with filtering options"""
    query = db.query(workflow_notification.model)

    if recipient_id:
        query = query.filter(workflow_notification.model.recipient_id == recipient_id)
    if status:
        query = query.filter(workflow_notification.model.status == status)
    if unread_only:
        query = query.filter(workflow_notification.model.read_at == None)

    notifications = (
        query.order_by(workflow_notification.model.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return notifications


@router.post("/send", response_model=WorkflowNotificationResponse, status_code=201)
def send_notification(
    request: NotificationSendRequest,
    db: Session = Depends(get_db),
):
    """Send a single notification using a template"""
    template = workflow_notification_template.get(db, id=request.template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # TODO: Render template with variables
    subject = template.subject_template
    body = template.body_template

    # Create notification
    notification_in = WorkflowNotificationCreate(
        workflow_instance_id=request.workflow_instance_id,
        template_id=request.template_id,
        recipient_id=request.recipient_id,
        notification_type=template.notification_type,
        subject=subject,
        body=body,
        channel=request.channel or template.channels[0],
        scheduled_at=request.scheduled_at,
    )

    notification = workflow_notification.create(db, obj_in=notification_in)

    # TODO: Actually send the notification via email/SMS/push
    # For now, mark as sent
    if not request.scheduled_at:
        notification.status = NotificationStatus.SENT
        notification.sent_at = datetime.utcnow()
        db.commit()
        db.refresh(notification)

    return notification


@router.post("/bulk-send", status_code=202)
def send_bulk_notifications(
    request: BulkNotificationRequest,
    db: Session = Depends(get_db),
):
    """Send notifications to multiple recipients"""
    template = workflow_notification_template.get(db, id=request.template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    notifications_created = []

    for recipient_id in request.recipient_ids:
        # TODO: Render template with variables
        subject = template.subject_template
        body = template.body_template

        notification_in = WorkflowNotificationCreate(
            workflow_instance_id=request.workflow_instance_id,
            template_id=request.template_id,
            recipient_id=recipient_id,
            notification_type=template.notification_type,
            subject=subject,
            body=body,
            channel=template.channels[0],
            scheduled_at=request.scheduled_at,
        )

        notification = workflow_notification.create(db, obj_in=notification_in)
        notifications_created.append(notification.id)

    return {
        "message": f"Created {len(notifications_created)} notifications",
        "notification_ids": notifications_created,
        "scheduled": request.scheduled_at is not None,
    }


@router.get("/{notification_id}", response_model=WorkflowNotificationResponse)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
):
    """Get a notification by ID"""
    notification = workflow_notification.get(db, id=notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


@router.post("/{notification_id}/mark-read", response_model=WorkflowNotificationResponse)
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
):
    """Mark a notification as read"""
    notification = workflow_notification.get(db, id=notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    if not notification.read_at:
        notification.read_at = datetime.utcnow()
        notification.status = NotificationStatus.READ
        db.commit()
        db.refresh(notification)

    return notification


@router.post("/mark-all-read")
def mark_all_as_read(
    recipient_id: int = Body(...),
    db: Session = Depends(get_db),
):
    """Mark all notifications as read for a recipient"""
    count = (
        db.query(workflow_notification.model)
        .filter(
            workflow_notification.model.recipient_id == recipient_id,
            workflow_notification.model.read_at == None,
        )
        .update({"read_at": datetime.utcnow(), "status": NotificationStatus.READ})
    )

    db.commit()

    return {"message": f"Marked {count} notifications as read"}


@router.get("/user/{user_id}/statistics", response_model=NotificationStatistics)
def get_user_notification_stats(
    user_id: int,
    db: Session = Depends(get_db),
):
    """Get notification statistics for a user"""
    total = (
        db.query(workflow_notification.model)
        .filter(workflow_notification.model.recipient_id == user_id)
        .count()
    )

    sent = (
        db.query(workflow_notification.model)
        .filter(
            workflow_notification.model.recipient_id == user_id,
            workflow_notification.model.status == NotificationStatus.SENT,
        )
        .count()
    )

    delivered = (
        db.query(workflow_notification.model)
        .filter(
            workflow_notification.model.recipient_id == user_id,
            workflow_notification.model.status == NotificationStatus.DELIVERED,
        )
        .count()
    )

    read = (
        db.query(workflow_notification.model)
        .filter(
            workflow_notification.model.recipient_id == user_id,
            workflow_notification.model.status == NotificationStatus.READ,
        )
        .count()
    )

    failed = (
        db.query(workflow_notification.model)
        .filter(
            workflow_notification.model.recipient_id == user_id,
            workflow_notification.model.status == NotificationStatus.FAILED,
        )
        .count()
    )

    pending = (
        db.query(workflow_notification.model)
        .filter(
            workflow_notification.model.recipient_id == user_id,
            workflow_notification.model.status == NotificationStatus.PENDING,
        )
        .count()
    )

    delivery_rate = (delivered / total * 100) if total > 0 else 0
    read_rate = (read / total * 100) if total > 0 else 0

    return NotificationStatistics(
        total_notifications=total,
        sent_count=sent,
        delivered_count=delivered,
        read_count=read,
        failed_count=failed,
        pending_count=pending,
        delivery_rate=delivery_rate,
        read_rate=read_rate,
    )


# ============================================================================
# Notification Preferences
# ============================================================================


@router.get("/preferences/{user_id}", response_model=List[NotificationPreferenceResponse])
def get_user_preferences(
    user_id: int,
    db: Session = Depends(get_db),
):
    """Get notification preferences for a user"""
    preferences = (
        db.query(notification_preference.model)
        .filter(notification_preference.model.user_id == user_id)
        .all()
    )
    return preferences


@router.post("/preferences", response_model=NotificationPreferenceResponse, status_code=201)
def create_preference(
    preference_in: NotificationPreferenceCreate,
    db: Session = Depends(get_db),
):
    """Create a notification preference"""
    preference = notification_preference.create(db, obj_in=preference_in)
    return preference


@router.put("/preferences/{preference_id}", response_model=NotificationPreferenceResponse)
def update_preference(
    preference_id: int,
    preference_in: NotificationPreferenceUpdate,
    db: Session = Depends(get_db),
):
    """Update notification preference"""
    preference = notification_preference.get(db, id=preference_id)
    if not preference:
        raise HTTPException(status_code=404, detail="Preference not found")

    preference = notification_preference.update(db, db_obj=preference, obj_in=preference_in)
    return preference
