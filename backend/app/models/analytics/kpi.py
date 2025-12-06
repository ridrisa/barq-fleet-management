"""KPI Model - Key Performance Indicators tracking"""

import enum

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class KPIPeriod(str, enum.Enum):
    """KPI measurement period"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class KPITrend(str, enum.Enum):
    """KPI trend direction"""

    UP = "up"
    DOWN = "down"
    STABLE = "stable"


class KPI(TenantMixin, BaseModel):
    """
    Key Performance Indicators with targets and thresholds.
    Tracks organizational and operational KPIs over time.
    """

    __tablename__ = "kpis"

    # KPI metadata
    name = Column(String(255), nullable=False, index=True, comment="KPI name")
    code = Column(String(100), unique=True, nullable=False, index=True, comment="Unique KPI code")
    description = Column(Text, nullable=True, comment="KPI description")
    category = Column(
        String(100),
        nullable=False,
        index=True,
        comment="KPI category (e.g., 'operations', 'hr', 'finance')",
    )

    # Current value
    current_value = Column(Numeric(20, 4), nullable=True, comment="Current KPI value")
    previous_value = Column(Numeric(20, 4), nullable=True, comment="Previous period value")

    # Targets and thresholds
    target_value = Column(Numeric(20, 4), nullable=True, comment="Target value to achieve")
    warning_threshold = Column(Numeric(20, 4), nullable=True, comment="Warning threshold")
    critical_threshold = Column(Numeric(20, 4), nullable=True, comment="Critical threshold")

    # Trend analysis
    trend = Column(SQLEnum(KPITrend, values_callable=lambda e: [m.value for m in e]), nullable=True, comment="Trend direction")
    trend_percentage = Column(Numeric(10, 2), nullable=True, comment="Trend percentage change")

    # Period configuration
    period = Column(SQLEnum(KPIPeriod, values_callable=lambda e: [m.value for m in e]), default=KPIPeriod.MONTHLY, nullable=False)
    period_start = Column(DateTime(timezone=True), nullable=True, comment="Period start date")
    period_end = Column(DateTime(timezone=True), nullable=True, comment="Period end date")

    # Calculation details
    calculation_formula = Column(
        Text, nullable=True, comment="Formula or query for calculating KPI"
    )
    unit = Column(String(50), nullable=True, comment="Unit of measurement (%, SAR, count, etc.)")

    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Historical data (stored as time series)
    historical_data = Column(JSONB, nullable=True, comment="Historical values [{date, value}]")

    # Last calculation
    last_calculated_at = Column(DateTime(timezone=True), nullable=True)

    # Indexes
    __table_args__ = (
        Index("idx_kpi_category_active", "category", "is_active"),
        Index("idx_kpi_period_dates", "period", "period_start", "period_end"),
    )

    def __repr__(self):
        return f"<KPI {self.code}: {self.current_value} / {self.target_value}>"

    @property
    def achievement_percentage(self) -> float:
        """Calculate achievement percentage vs target"""
        if not self.current_value or not self.target_value:
            return 0.0
        return float((self.current_value / self.target_value) * 100)

    @property
    def is_on_target(self) -> bool:
        """Check if KPI is meeting target"""
        if not self.current_value or not self.target_value:
            return False
        return self.current_value >= self.target_value

    @property
    def status_color(self) -> str:
        """Return status color based on thresholds"""
        if not self.current_value:
            return "gray"

        if self.critical_threshold and self.current_value <= self.critical_threshold:
            return "red"

        if self.warning_threshold and self.current_value <= self.warning_threshold:
            return "yellow"

        if self.is_on_target:
            return "green"

        return "blue"
