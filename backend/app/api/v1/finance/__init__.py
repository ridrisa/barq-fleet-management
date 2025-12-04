from fastapi import APIRouter

from app.api.v1.finance import budgets, expenses, reports, tax

router = APIRouter()

router.include_router(expenses.router, prefix="/expenses", tags=["expenses"])
router.include_router(budgets.router, prefix="/budgets", tags=["budgets"])
router.include_router(reports.router, prefix="/reports", tags=["reports"])
router.include_router(tax.router, prefix="/tax", tags=["tax"])

__all__ = ["router"]
