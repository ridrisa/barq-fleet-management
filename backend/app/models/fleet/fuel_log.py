from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class FuelLog(TenantMixin, BaseModel):
    __tablename__ = "fuel_logs"

    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False)
    courier_id = Column(Integer, ForeignKey("couriers.id", ondelete="SET NULL"), nullable=True)

    fuel_date = Column(Date, nullable=False)
    odometer_reading = Column(Numeric(10, 2), nullable=False)
    fuel_quantity = Column(Numeric(10, 2), nullable=False)  # Liters
    fuel_cost = Column(Numeric(10, 2), nullable=False)
    cost_per_liter = Column(Numeric(10, 2), nullable=False)

    fuel_station = Column(String(200))
    fuel_type = Column(String(50))  # Diesel, Petrol, etc.

    receipt_number = Column(String(100))
    receipt_image_url = Column(String(500))

    notes = Column(String(500))

    # Relationships
    vehicle = relationship("Vehicle", back_populates="fuel_logs")
    courier = relationship("Courier", back_populates="fuel_logs")
