from app.crud.base import CRUDBase
from app.models.workflow.notification import (
    NotificationPreference,
    WorkflowNotification,
    WorkflowNotificationTemplate,
)
from app.schemas.workflow.notification import (
    NotificationPreferenceCreate,
    NotificationPreferenceUpdate,
    WorkflowNotificationCreate,
    WorkflowNotificationTemplateCreate,
    WorkflowNotificationTemplateUpdate,
    WorkflowNotificationUpdate,
)

workflow_notification_template = CRUDBase[
    WorkflowNotificationTemplate,
    WorkflowNotificationTemplateCreate,
    WorkflowNotificationTemplateUpdate,
](WorkflowNotificationTemplate)

workflow_notification = CRUDBase[
    WorkflowNotification, WorkflowNotificationCreate, WorkflowNotificationUpdate
](WorkflowNotification)

notification_preference = CRUDBase[
    NotificationPreference, NotificationPreferenceCreate, NotificationPreferenceUpdate
](NotificationPreference)
