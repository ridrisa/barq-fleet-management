"""Workflow Management API routes"""

from fastapi import APIRouter
from app.api.v1.workflow import (
    template,
    instance,
)

# Create main workflow router
workflow_router = APIRouter()

# Include all sub-routers
workflow_router.include_router(template.router, prefix="/template", tags=["workflow-template"])
workflow_router.include_router(instance.router, prefix="/instance", tags=["workflow-instance"])

__all__ = ["workflow_router"]
