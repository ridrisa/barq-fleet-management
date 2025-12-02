from fastapi import APIRouter

from app.api.v1 import auth, health, dashboard  # users module temporarily disabled
from app.api.v1.admin import router as admin_router
from app.api.v1.support import support_router
from app.api.v1.performance import router as performance_router
from app.api import fleet, hr, operations, accommodation, finance, workflow, fms, analytics
# from app.api import tenant  # temporarily disabled

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
# api_router.include_router(users.router, prefix="/users", tags=["users"])  # temporarily disabled
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(performance_router, tags=["performance"])

# Admin routes - RBAC Management
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])

# Module routes
api_router.include_router(fleet.router, prefix="/fleet", tags=["fleet"])
api_router.include_router(hr.router, prefix="/hr", tags=["hr"])
api_router.include_router(operations.router, prefix="/operations", tags=["operations"])
api_router.include_router(accommodation.router, prefix="/accommodation", tags=["accommodation"])
api_router.include_router(finance.router, prefix="/finance", tags=["finance"])
api_router.include_router(workflow.router, prefix="/workflow", tags=["workflow"])
api_router.include_router(support_router, prefix="/support", tags=["support"])
api_router.include_router(fms.router, prefix="/fms", tags=["FMS Tracking"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
# api_router.include_router(tenant.router, prefix="/tenant", tags=["tenant"])  # temporarily disabled
