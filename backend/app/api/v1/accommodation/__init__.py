"""Accommodation API Router"""

from fastapi import APIRouter

from app.api.v1.accommodation import allocation, bed, building, room

router = APIRouter()

router.include_router(building.router, prefix="/buildings", tags=["Accommodation - Buildings"])
router.include_router(room.router, prefix="/rooms", tags=["Accommodation - Rooms"])
router.include_router(bed.router, prefix="/beds", tags=["Accommodation - Beds"])
router.include_router(
    allocation.router, prefix="/allocations", tags=["Accommodation - Allocations"]
)

__all__ = ["router"]
