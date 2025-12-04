"""HR Management API routes"""

from fastapi import APIRouter

from app.api.v1.hr import (
    asset,
    attendance,
    leave,
    loan,
    salary,
)

# Additional v1 routers
from app.api.v1.hr import (
    bonuses,
    penalties,
    payroll,
    gosi,
    eos,
)

# Create main HR router
hr_router = APIRouter()

# Include all sub-routers
hr_router.include_router(leave.router, prefix="/leave", tags=["hr-leave"])
hr_router.include_router(attendance.router, prefix="/attendance", tags=["hr-attendance"])
hr_router.include_router(loan.router, prefix="/loan", tags=["hr-loan"])
hr_router.include_router(salary.router, prefix="/salary", tags=["hr-salary"])
hr_router.include_router(asset.router, prefix="/asset", tags=["hr-asset"])

# Include additional v1 routers
hr_router.include_router(bonuses.router, prefix="/bonuses", tags=["hr-bonuses"])
hr_router.include_router(penalties.router, prefix="/penalties", tags=["hr-penalties"])
hr_router.include_router(payroll.router, prefix="/payroll", tags=["hr-payroll"])
hr_router.include_router(gosi.router, prefix="/gosi", tags=["hr-gosi"])
hr_router.include_router(eos.router, prefix="/eos", tags=["hr-eos"])

__all__ = ["hr_router"]
