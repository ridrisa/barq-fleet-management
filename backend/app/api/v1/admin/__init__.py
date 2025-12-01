"""Admin API Routes - Complete Admin Module"""
from fastapi import APIRouter

from app.api.v1.admin import (
    roles,
    permissions,
    audit_logs,
    users,
    monitoring,
    backups,
    integrations,
    api_keys,
)

router = APIRouter()

# Register sub-routers

# RBAC Management
router.include_router(roles.router, prefix="/roles", tags=["admin-roles"])
router.include_router(permissions.router, prefix="/permissions", tags=["admin-permissions"])
router.include_router(users.router, prefix="/users", tags=["admin-users"])

# Audit & Monitoring
router.include_router(audit_logs.router, prefix="/audit-logs", tags=["admin-audit"])
router.include_router(monitoring.router, prefix="/monitoring", tags=["admin-monitoring"])

# System Management
router.include_router(backups.router, prefix="/backups", tags=["admin-backups"])
router.include_router(integrations.router, prefix="/integrations", tags=["admin-integrations"])
router.include_router(api_keys.router, prefix="/api-keys", tags=["admin-api-keys"])
