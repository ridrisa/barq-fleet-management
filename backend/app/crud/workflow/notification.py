from app.crud.base import CRUDBase
from app.models.workflow.notification import (
    WorkflowNotificationTemplate,
    WorkflowNotification,
    NotificationPreference,
)
from app.schemas.workflow.notification import (
    WorkflowNotificationTemplateCreate,
    WorkflowNotificationTemplateUpdate,
    WorkflowNotificationCreate,
    WorkflowNotificationUpdate,
    NotificationPreferenceCreate,
    NotificationPreferenceUpdate,
)

workflow_notification_template = CRUDBase[
    WorkflowNotificationTemplate,
    WorkflowNotificationTemplateCreate,
    WorkflowNotificationTemplateUpdate
](WorkflowNotificationTemplate)

workflow_notification = CRUDBase[
    WorkflowNotification,
    WorkflowNotificationCreate,
    WorkflowNotificationUpdate
](WorkflowNotification)

notification_preference = CRUDBase[
    NotificationPreference,
    NotificationPreferenceCreate,
    NotificationPreferenceUpdate
](NotificationPreference)
