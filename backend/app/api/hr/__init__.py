from fastapi import APIRouter

from app.api.hr import (
    assets,
    attendance,
    bonuses,
    eos,
    gosi,
    leaves,
    loans,
    payroll,
    penalties,
    salaries,
)

router = APIRouter()

router.include_router(leaves.router, prefix="/leaves", tags=["leaves"])
router.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
router.include_router(loans.router, prefix="/loans", tags=["loans"])
router.include_router(assets.router, prefix="/assets", tags=["assets"])
router.include_router(salaries.router, prefix="/salary", tags=["salary"])
router.include_router(bonuses.router, prefix="/bonuses", tags=["bonuses"])
router.include_router(penalties.router, prefix="/penalties", tags=["penalties"])
router.include_router(payroll.router, prefix="/payroll", tags=["payroll"])
router.include_router(gosi.router, prefix="/gosi", tags=["gosi"])
router.include_router(eos.router, prefix="/eos", tags=["eos"])

__all__ = ["router"]
