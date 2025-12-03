from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class IncidentType(str, Enum):
    ACCIDENT = "accident"
    THEFT = "theft"
    DAMAGE = "damage"
    VIOLATION = "violation"
    OTHER = "other"


class IncidentStatus(str, Enum):
    REPORTED = "reported"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentBase(BaseModel):
    courier_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    incident_type: IncidentType
    incident_date: datetime
    location: Optional[str] = None
    description: str = Field(..., min_length=10)
    severity: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")


class IncidentCreate(IncidentBase):
    pass


class IncidentUpdate(BaseModel):
    courier_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    incident_type: Optional[IncidentType] = None
    incident_date: Optional[datetime] = None
    location: Optional[str] = None
    description: Optional[str] = Field(None, min_length=10)
    severity: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    status: Optional[IncidentStatus] = None
    resolution: Optional[str] = None
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None


class IncidentResponse(IncidentBase):
    id: int
    status: IncidentStatus
    resolution: Optional[str] = None
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None
    created_at: date
    updated_at: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)
