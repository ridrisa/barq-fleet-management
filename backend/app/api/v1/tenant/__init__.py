"""Tenant API routes"""

from fastapi import APIRouter
from app.api.v1.tenant import organization, organization_user

# Create tenant router
tenant_router = APIRouter()

# Include organization routes
tenant_router.include_router(
    organization.router,
    prefix="/organizations",
    tags=["Organizations"]
)

# Include organization user routes
tenant_router.include_router(
    organization_user.router,
    prefix="/organizations",
    tags=["Organization Users"]
)

__all__ = ["tenant_router"]
