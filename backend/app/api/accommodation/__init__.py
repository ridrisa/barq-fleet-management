from fastapi import APIRouter

from app.api.accommodation import buildings, rooms

router = APIRouter()

router.include_router(buildings.router, prefix="/buildings", tags=["buildings"])
router.include_router(rooms.router, prefix="/rooms", tags=["rooms"])

__all__ = ["router"]
