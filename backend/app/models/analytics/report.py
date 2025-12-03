"""Report Model - Generated reports management"""
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.mixins import TenantMixin
import enum


class ReportType(str, enum.Enum):
    """Report types"""
    COURIER_PERFORMANCE = "courier_performance"
    FLEET_UTILIZATION = "fleet_utilization"
    DELIVERY_ANALYTICS = "delivery_analytics"
    FINANCIAL_SUMMARY = "financial_summary"
    HR_ATTENDANCE = "hr_attendance"
    MAINTENANCE_REPORT = "maintenance_report"
    COD_RECONCILIATION = "cod_reconciliation"
    CUSTOM = "custom"


class ReportStatus(str, enum.Enum):
    """Report generation status"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    SCHEDULED = "scheduled"


class ReportFormat(str, enum.Enum):
    """Report output format"""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"


class Report(TenantMixin, BaseModel):
    """
    Generated reports with parameters and storage paths.
    Supports scheduled and on-demand report generation.
    """

    __tablename__ = "reports"

    # Report metadata
    name = Column(String(255), nullable=False, index=True, comment="Report name")
    description = Column(Text, nullable=True, comment="Report description")
    report_type = Column(SQLEnum(ReportType), nullable=False, index=True, comment="Type of report")

    # Generation details
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.PENDING, nullable=False, index=True)
    format = Column(SQLEnum(ReportFormat), default=ReportFormat.PDF, nullable=False)

    # Parameters and filters
    parameters = Column(JSONB, nullable=True, comment="Report parameters (date range, filters, etc.)")

    # Timestamps
    generated_at = Column(DateTime(timezone=True), nullable=True, comment="When report was generated")
    scheduled_at = Column(DateTime(timezone=True), nullable=True, comment="For scheduled reports")

    # Storage
    file_path = Column(String(500), nullable=True, comment="Path to generated report file")
    file_size_bytes = Column(Integer, nullable=True, comment="File size in bytes")

    # User tracking
    generated_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Error tracking
    error_message = Column(Text, nullable=True, comment="Error message if generation failed")

    # Relationships
    generated_by = relationship("User", backref="generated_reports")

    # Indexes
    __table_args__ = (
        Index('idx_report_type_status', 'report_type', 'status'),
        Index('idx_report_generated_at', 'generated_at'),
        Index('idx_report_user', 'generated_by_user_id', 'generated_at'),
    )

    def __repr__(self):
        return f"<Report {self.name} ({self.report_type.value}) - {self.status.value}>"
