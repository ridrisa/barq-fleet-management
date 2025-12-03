from sqlalchemy import Column, String, Integer, Date, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class PerformanceData(TenantMixin, BaseModel):
    """Performance & Analytics model - Tracks courier performance metrics"""

    __tablename__ = "performance_data"

    # Core Fields
    courier_id = Column(Integer, ForeignKey("couriers.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True, comment="Performance date")

    # Order Metrics
    orders_completed = Column(Integer, default=0, nullable=False, comment="Total orders completed")
    orders_failed = Column(Integer, default=0, nullable=False, comment="Total orders failed/cancelled")
    on_time_deliveries = Column(Integer, default=0, nullable=False, comment="Deliveries on time")
    late_deliveries = Column(Integer, default=0, nullable=False, comment="Deliveries late")

    # Distance & Revenue
    distance_covered_km = Column(Numeric(10, 2), default=0.0, nullable=False, comment="Distance covered in KM")
    revenue_generated = Column(Numeric(12, 2), default=0.0, nullable=False, comment="Revenue generated (SAR)")
    cod_collected = Column(Numeric(12, 2), default=0.0, nullable=False, comment="Cash on Delivery collected (SAR)")

    # Quality Metrics
    average_rating = Column(Numeric(3, 2), default=0.0, nullable=False, comment="Average customer rating (0-5)")

    # Time Metrics
    working_hours = Column(Numeric(5, 2), default=0.0, nullable=False, comment="Working hours")

    # Performance Score (Calculated)
    efficiency_score = Column(Numeric(5, 2), default=0.0, nullable=False, comment="Efficiency score (0-100)")

    # Additional Notes
    notes = Column(Text, nullable=True, comment="Additional notes")

    # Relationships
    courier = relationship("Courier", backref="performance_records")

    def __repr__(self):
        return f"<PerformanceData courier_id={self.courier_id} date={self.date} score={self.efficiency_score}>"

    @property
    def total_orders(self) -> int:
        """Total orders (completed + failed)"""
        return self.orders_completed + self.orders_failed

    @property
    def success_rate(self) -> float:
        """Order success rate percentage"""
        if self.total_orders == 0:
            return 0.0
        return (self.orders_completed / self.total_orders) * 100

    @property
    def on_time_rate(self) -> float:
        """On-time delivery rate percentage"""
        if self.orders_completed == 0:
            return 0.0
        return (self.on_time_deliveries / self.orders_completed) * 100

    @property
    def orders_per_hour(self) -> float:
        """Orders per working hour"""
        if float(self.working_hours) == 0:
            return 0.0
        return self.orders_completed / float(self.working_hours)

    @property
    def revenue_per_order(self) -> float:
        """Average revenue per order"""
        if self.orders_completed == 0:
            return 0.0
        return float(self.revenue_generated) / self.orders_completed
