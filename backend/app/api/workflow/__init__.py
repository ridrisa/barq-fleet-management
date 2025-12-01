from fastapi import APIRouter
from .templates import router as templates_router
from .instances import router as instances_router
from .approvals import router as approvals_router
from .sla import router as sla_router
from .automations import router as automations_router
from .triggers import router as triggers_router
from .analytics import router as analytics_router

router = APIRouter()

router.include_router(templates_router, prefix="/templates", tags=["workflow-templates"])
router.include_router(instances_router, prefix="/instances", tags=["workflow-instances"])
router.include_router(approvals_router, prefix="/approvals", tags=["workflow-approvals"])
router.include_router(sla_router, prefix="/sla", tags=["workflow-sla"])
router.include_router(automations_router, prefix="/automations", tags=["workflow-automations"])
router.include_router(triggers_router, prefix="/triggers", tags=["workflow-triggers"])
router.include_router(analytics_router, prefix="/analytics", tags=["workflow-analytics"])

__all__ = ["router"]
