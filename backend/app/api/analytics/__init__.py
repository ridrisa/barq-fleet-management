from fastapi import APIRouter
from app.api.analytics import performance

router = APIRouter()

router.include_router(performance.router, prefix="/performance", tags=["performance"])

__all__ = ["router"]
