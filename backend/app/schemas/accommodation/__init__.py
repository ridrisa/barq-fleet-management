"""Accommodation Schemas"""

from app.schemas.accommodation.allocation import (
    AllocationBase,
    AllocationCreate,
    AllocationResponse,
    AllocationUpdate,
)
from app.schemas.accommodation.bed import BedBase, BedCreate, BedResponse, BedStatus, BedUpdate
from app.schemas.accommodation.building import (
    BuildingBase,
    BuildingCreate,
    BuildingResponse,
    BuildingUpdate,
)
from app.schemas.accommodation.room import (
    RoomBase,
    RoomCreate,
    RoomResponse,
    RoomStatus,
    RoomUpdate,
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
