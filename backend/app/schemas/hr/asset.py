from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date
from enum import Enum

class AssetType(str, Enum):
    UNIFORM = "uniform"
    MOBILE_DEVICE = "mobile_device"
    EQUIPMENT = "equipment"
    TOOLS = "tools"

class AssetStatus(str, Enum):
    ASSIGNED = "assigned"
    RETURNED = "returned"
    DAMAGED = "damaged"
    LOST = "lost"

class AssetBase(BaseModel):
    courier_id: int = Field(..., description="Courier ID")
    asset_type: AssetType
    asset_name: str = Field(..., min_length=2, max_length=100)
    assigned_date: date
    serial_number: Optional[str] = None
    notes: Optional[str] = None

class AssetCreate(AssetBase):
    pass

class AssetUpdate(BaseModel):
    asset_type: Optional[AssetType] = None
    asset_name: Optional[str] = Field(None, min_length=2, max_length=100)
    assigned_date: Optional[date] = None
    return_date: Optional[date] = None
    serial_number: Optional[str] = None
    status: Optional[AssetStatus] = None
    notes: Optional[str] = None

class AssetResponse(AssetBase):
    id: int
    return_date: Optional[date] = None
    status: AssetStatus
    created_at: date
    updated_at: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)
