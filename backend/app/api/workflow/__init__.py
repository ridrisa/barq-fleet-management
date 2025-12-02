from fastapi import APIRouter
from .templates import router as templates_router
from .instances import router as instances_router
from .approvals import router as approvals_router
from .sla import router as sla_router
from .automations import router as automations_router
from .triggers import router as triggers_router
from .analytics import router as analytics_router
from .comments import router as comments_router
from .attachments import router as attachments_router
from .history import router as history_router
from .notifications import router as notifications_router

router = APIRouter()

# Core workflow routes
router.include_router(templates_router, prefix="/templates", tags=["workflow-templates"])
router.include_router(instances_router, prefix="/instances", tags=["workflow-instances"])

# Approval and SLA routes
router.include_router(approvals_router, prefix="/approvals", tags=["workflow-approvals"])
router.include_router(sla_router, prefix="/sla", tags=["workflow-sla"])

# Automation routes
router.include_router(automations_router, prefix="/automations", tags=["workflow-automations"])
router.include_router(triggers_router, prefix="/triggers", tags=["workflow-triggers"])

# Collaboration routes
router.include_router(comments_router, prefix="/comments", tags=["workflow-comments"])
router.include_router(attachments_router, prefix="/attachments", tags=["workflow-attachments"])

# Audit and notifications
router.include_router(history_router, prefix="/history", tags=["workflow-history"])
router.include_router(notifications_router, prefix="/notifications", tags=["workflow-notifications"])

# Analytics routes
router.include_router(analytics_router, prefix="/analytics", tags=["workflow-analytics"])

__all__ = ["router"]
