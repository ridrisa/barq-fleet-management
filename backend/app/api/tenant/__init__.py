"""Tenant API module router"""

from fastapi import APIRouter

from app.api.v1.tenant import tenant_router

router = APIRouter()

# Include tenant router from v1
router.include_router(tenant_router)

__all__ = ["router"]
