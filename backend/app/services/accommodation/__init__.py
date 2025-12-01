"""Accommodation Services"""
from app.services.accommodation.building_service import BuildingService, building_service
from app.services.accommodation.room_service import RoomService, room_service
from app.services.accommodation.bed_service import BedService, bed_service
from app.services.accommodation.allocation_service import AllocationService, allocation_service

__all__ = [
    "BuildingService",
    "building_service",
    "RoomService",
    "room_service",
    "BedService",
    "bed_service",
    "AllocationService",
    "allocation_service",
]
