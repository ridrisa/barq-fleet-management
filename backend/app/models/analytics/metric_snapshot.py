"""Metric Snapshot Model - Time-series metrics storage"""

from sqlalchemy import JSON, Column, DateTime, Index, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class MetricSnapshot(TenantMixin, BaseModel):
    """
    Time-series metric snapshots for analytics.
    Stores point-in-time measurements with dimensions for flexible querying.
    """

    __tablename__ = "metric_snapshots"

    # Metric identification
    metric_name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Name of the metric (e.g., 'active_couriers', 'deliveries_completed')",
    )
    metric_type = Column(
        String(50), nullable=False, index=True, comment="Type: counter, gauge, histogram"
    )

    # Metric value
    value = Column(Numeric(20, 4), nullable=False, comment="Metric value")

    # Dimensions for filtering and grouping
    dimensions = Column(
        JSONB,
        nullable=True,
        comment="Flexible dimensions (e.g., {'city': 'Riyadh', 'zone': 'North'})",
    )

    # Timestamp
    timestamp = Column(
        DateTime(timezone=True), nullable=False, index=True, comment="When the metric was recorded"
    )

    # Optional metadata
    tags = Column(JSONB, nullable=True, comment="Additional tags for categorization")
    source = Column(String(100), nullable=True, comment="Source system or service")

    # Composite indexes for common query patterns
    __table_args__ = (
        Index("idx_metric_name_timestamp", "metric_name", "timestamp"),
        Index("idx_metric_type_timestamp", "metric_type", "timestamp"),
        Index("idx_dimensions_gin", "dimensions", postgresql_using="gin"),
        Index("idx_tags_gin", "tags", postgresql_using="gin"),
    )

    def __repr__(self):
        return f"<MetricSnapshot {self.metric_name}={self.value} at {self.timestamp}>"
