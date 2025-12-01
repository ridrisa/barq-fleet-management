from sqlalchemy import Column, String, Integer, Date, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Route(BaseModel):
    __tablename__ = "routes"

    route_name = Column(String, nullable=False)
    courier_id = Column(Integer, ForeignKey("couriers.id"))
    date = Column(Date, nullable=False)
    waypoints = Column(JSON)
    total_distance = Column(Integer)
    estimated_time = Column(Integer)
    notes = Column(String)

    courier = relationship("Courier")
