"""
API Router Configuration

This module configures the main API router with all v1 endpoints.
Legacy (non-v1) routers have been removed as part of the API consolidation.
"""

from fastapi import APIRouter

# V1 Core routes
from app.api.v1 import auth, dashboard, health
from app.api.v1.admin import router as admin_router
from app.api.v1.performance import router as performance_router
from app.api.v1.support import support_router

# V1 Module routers
from app.api.v1.fleet import fleet_router
from app.api.v1.hr import hr_router
from app.api.v1.operations import router as operations_router
from app.api.v1.accommodation import router as accommodation_router
from app.api.v1.workflow import workflow_router
from app.api.v1.tenant import tenant_router

api_router = APIRouter()

# Authentication & Core
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(performance_router, tags=["performance"])

# Admin routes - RBAC Management
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])

# Multi-tenancy routes (v1)
api_router.include_router(tenant_router, prefix="/tenant", tags=["tenant"])

# Module routes (v1)
api_router.include_router(fleet_router, prefix="/fleet", tags=["fleet"])
api_router.include_router(hr_router, prefix="/hr", tags=["hr"])
api_router.include_router(operations_router, prefix="/operations", tags=["operations"])
api_router.include_router(accommodation_router, prefix="/accommodation", tags=["accommodation"])
api_router.include_router(workflow_router, prefix="/workflow", tags=["workflow"])
api_router.include_router(support_router, prefix="/support", tags=["support"])
