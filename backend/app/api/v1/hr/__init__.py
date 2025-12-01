"""HR Management API routes"""

from fastapi import APIRouter
from app.api.v1.hr import (
    leave,
    attendance,
    loan,
    salary,
    asset,
)

# Create main HR router
hr_router = APIRouter()

# Include all sub-routers
hr_router.include_router(leave.router, prefix="/leave", tags=["hr-leave"])
hr_router.include_router(attendance.router, prefix="/attendance", tags=["hr-attendance"])
hr_router.include_router(loan.router, prefix="/loan", tags=["hr-loan"])
hr_router.include_router(salary.router, prefix="/salary", tags=["hr-salary"])
hr_router.include_router(asset.router, prefix="/asset", tags=["hr-asset"])

__all__ = ["hr_router"]
