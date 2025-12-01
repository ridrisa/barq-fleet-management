from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date

class BuildingBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200, description="Building name")
    address: str = Field(..., min_length=5, description="Building address")
    notes: Optional[str] = Field(None, description="Additional notes")

class BuildingCreate(BuildingBase):
    pass

class BuildingUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    address: Optional[str] = Field(None, min_length=5)
    total_rooms: Optional[int] = Field(None, ge=0)
    total_capacity: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None

class BuildingResponse(BuildingBase):
    id: int
    total_rooms: int
    total_capacity: int
    created_at: date
    updated_at: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)
