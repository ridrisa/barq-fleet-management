from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date
from enum import Enum

class BedStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"

class BedBase(BaseModel):
    room_id: int = Field(..., description="Room ID")
    bed_number: int = Field(..., ge=1, description="Bed number within room")

class BedCreate(BedBase):
    pass

class BedUpdate(BaseModel):
    room_id: Optional[int] = None
    bed_number: Optional[int] = Field(None, ge=1)
    status: Optional[BedStatus] = None

class BedResponse(BedBase):
    id: int
    status: BedStatus
    created_at: date
    updated_at: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)
