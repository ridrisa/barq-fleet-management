"""Accommodation Schemas"""
from app.schemas.accommodation.building import (
    BuildingBase,
    BuildingCreate,
    BuildingUpdate,
    BuildingResponse
)
from app.schemas.accommodation.room import (
    RoomBase,
    RoomCreate,
    RoomUpdate,
    RoomResponse,
    RoomStatus
)
from app.schemas.accommodation.bed import (
    BedBase,
    BedCreate,
    BedUpdate,
    BedResponse,
    BedStatus
)
from app.schemas.accommodation.allocation import (
    AllocationBase,
    AllocationCreate,
    AllocationUpdate,
    AllocationResponse
)

__all__ = [
    # Building
    "BuildingBase",
    "BuildingCreate",
    "BuildingUpdate",
    "BuildingResponse",
    # Room
    "RoomBase",
    "RoomCreate",
    "RoomUpdate",
    "RoomResponse",
    "RoomStatus",
    # Bed
    "BedBase",
    "BedCreate",
    "BedUpdate",
    "BedResponse",
    "BedStatus",
    # Allocation
    "AllocationBase",
    "AllocationCreate",
    "AllocationUpdate",
    "AllocationResponse",
]
