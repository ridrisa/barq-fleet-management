from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import date

class AllocationBase(BaseModel):
    courier_id: int = Field(..., description="Courier ID")
    bed_id: int = Field(..., description="Bed ID")
    allocation_date: date = Field(..., description="Date of allocation")
    release_date: Optional[date] = Field(None, description="Date of release/checkout")

    @field_validator('release_date')
    @classmethod
    def validate_release_date(cls, v, info):
        if v and 'allocation_date' in info.data:
            if v < info.data['allocation_date']:
                raise ValueError('Release date cannot be before allocation date')
        return v

class AllocationCreate(AllocationBase):
    pass

class AllocationUpdate(BaseModel):
    courier_id: Optional[int] = None
    bed_id: Optional[int] = None
    allocation_date: Optional[date] = None
    release_date: Optional[date] = None

    @field_validator('release_date')
    @classmethod
    def validate_release_date(cls, v, info):
        if v and 'allocation_date' in info.data and info.data['allocation_date']:
            if v < info.data['allocation_date']:
                raise ValueError('Release date cannot be before allocation date')
        return v

class AllocationResponse(AllocationBase):
    id: int
    created_at: date
    updated_at: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)
