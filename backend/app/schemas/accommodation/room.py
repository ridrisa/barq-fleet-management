from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date
from enum import Enum

class RoomStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"

class RoomBase(BaseModel):
    building_id: int = Field(..., description="Building ID")
    room_number: str = Field(..., min_length=1, max_length=50, description="Room number")
    capacity: int = Field(..., ge=1, description="Room capacity (number of beds)")

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    building_id: Optional[int] = None
    room_number: Optional[str] = Field(None, min_length=1, max_length=50)
    capacity: Optional[int] = Field(None, ge=1)
    occupied: Optional[int] = Field(None, ge=0)
    status: Optional[RoomStatus] = None

class RoomResponse(RoomBase):
    id: int
    occupied: int
    status: RoomStatus
    created_at: date
    updated_at: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)
