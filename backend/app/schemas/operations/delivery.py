from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DeliveryStatus(str, Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETURNED = "returned"


class DeliveryBase(BaseModel):
    tracking_number: str = Field(..., min_length=5, max_length=50)
    courier_id: int = Field(..., description="Courier ID")
    pickup_address: str = Field(..., min_length=10)
    delivery_address: str = Field(..., min_length=10)
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    notes: Optional[str] = None


class DeliveryCreate(DeliveryBase):
    pass


class DeliveryUpdate(BaseModel):
    courier_id: Optional[int] = None
    pickup_address: Optional[str] = None
    delivery_address: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    status: Optional[DeliveryStatus] = None
    delivered_at: Optional[datetime] = None
    notes: Optional[str] = None


class DeliveryResponse(DeliveryBase):
    id: int
    status: DeliveryStatus
    delivered_at: Optional[datetime] = None
    created_at: date
    updated_at: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)
