from app.models.accommodation.allocation import Allocation
from app.models.accommodation.bed import Bed, BedStatus

# ============================================================================
# Accommodation Models - Working relationships
# ============================================================================
from app.models.accommodation.building import Building
from app.models.accommodation.room import Room, RoomStatus

# ============================================================================
# Security Models - Password Reset
# ============================================================================
from app.models.password_reset_token import PasswordResetToken

# ============================================================================
# Admin Models - System Management
# ============================================================================
from app.models.admin.api_key import ApiKey, ApiKeyStatus
from app.models.admin.backup import Backup, BackupStatus, BackupStorage, BackupType
from app.models.admin.integration import Integration, IntegrationStatus, IntegrationType
from app.models.admin.system_setting import SettingCategory, SettingType, SystemSetting
from app.models.analytics.dashboard import Dashboard
from app.models.analytics.kpi import KPI, KPIPeriod, KPITrend
from app.models.analytics.metric_snapshot import MetricSnapshot

# ============================================================================
# Analytics Models - Working relationships
# ============================================================================
from app.models.analytics.performance import PerformanceData
from app.models.analytics.report import Report, ReportFormat, ReportStatus, ReportType
from app.models.audit_log import AuditAction, AuditLog
from app.models.base import BaseModel
from app.models.fleet.accident_log import AccidentLog
from app.models.fleet.assignment import CourierVehicleAssignment
from app.models.fleet.courier import Courier
from app.models.fleet.document import Document, DocumentEntity, DocumentType

# ============================================================================
# Fleet Models - Fixed bidirectional relationships
# ============================================================================
from app.models.fleet.fuel_log import FuelLog
from app.models.fleet.inspection import Inspection
from app.models.fleet.maintenance import VehicleMaintenance
from app.models.fleet.vehicle import Vehicle
from app.models.fleet.vehicle_log import VehicleLog
from app.models.hr.asset import Asset, AssetStatus, AssetType
from app.models.hr.attendance import Attendance, AttendanceStatus
from app.models.hr.bonus import Bonus, BonusType, PaymentStatus

# ============================================================================
# HR Models - Fixed bidirectional relationships
# ============================================================================
from app.models.hr.leave import Leave, LeaveStatus, LeaveType
from app.models.hr.loan import Loan, LoanStatus
from app.models.hr.salary import Salary

# ============================================================================
# Operations Models - Working relationships
# ============================================================================
from app.models.operations.cod import COD, CODStatus
from app.models.operations.delivery import Delivery, DeliveryStatus
from app.models.operations.incident import Incident, IncidentStatus, IncidentType
from app.models.operations.route import Route

# ============================================================================
# RBAC Models - Fixed bidirectional relationships
# ============================================================================
from app.models.role import Permission, PermissionAction, PermissionResource, Role

# ============================================================================
# Support Models - Working relationships
# ============================================================================
from app.models.support.ticket import Ticket, TicketCategory, TicketPriority, TicketStatus

# ============================================================================
# Tenant Models - Working relationships
# ============================================================================
from app.models.tenant.organization import Organization, SubscriptionPlan, SubscriptionStatus
from app.models.tenant.organization_user import OrganizationRole, OrganizationUser
from app.models.user import User
from app.models.workflow.analytics import (
    WorkflowMetrics,
    WorkflowPerformanceSnapshot,
    WorkflowStepMetrics,
    WorkflowUserMetrics,
)
from app.models.workflow.approval_chain import (
    ApprovalChain,
    ApprovalChainApprover,
    ApprovalRequest,
    ApprovalStatus,
)
from app.models.workflow.attachment import AttachmentType, WorkflowAttachment
from app.models.workflow.automation import (
    AutomationActionType,
    AutomationExecutionLog,
    AutomationStatus,
    AutomationTriggerType,
    WorkflowAutomation,
)
from app.models.workflow.comment import WorkflowComment
from app.models.workflow.history import (
    WorkflowHistory,
    WorkflowHistoryEventType,
    WorkflowStepHistory,
)
from app.models.workflow.instance import WorkflowInstance, WorkflowStatus
from app.models.workflow.notification import (
    NotificationChannel,
    NotificationPreference,
    NotificationStatus,
    NotificationType,
    WorkflowNotification,
    WorkflowNotificationTemplate,
)
from app.models.workflow.sla import (
    SLAEvent,
    SLAPriority,
    SLAStatus,
    WorkflowSLA,
    WorkflowSLAInstance,
)

# ============================================================================
# Workflow Models - Complete workflow engine
# ============================================================================
from app.models.workflow.template import WorkflowTemplate, WorkflowTemplateCategory
from app.models.workflow.trigger import (
    TriggerEventType,
    TriggerExecution,
    TriggerType,
    WorkflowTrigger,
)

__all__ = [
    # Base
    "BaseModel",
    "User",
    "AuditLog",
    "AuditAction",
    # Security
    "PasswordResetToken",
    # RBAC
    "Role",
    "Permission",
    "PermissionAction",
    "PermissionResource",
    # Admin
    "ApiKey",
    "ApiKeyStatus",
    "Integration",
    "IntegrationType",
    "IntegrationStatus",
    "SystemSetting",
    "SettingType",
    "SettingCategory",
    "Backup",
    "BackupType",
    "BackupStatus",
    "BackupStorage",
    # Fleet
    "Courier",
    "Vehicle",
    "CourierVehicleAssignment",
    "VehicleMaintenance",
    "Inspection",
    "AccidentLog",
    "VehicleLog",
    "FuelLog",
    "Document",
    "DocumentType",
    "DocumentEntity",
    # HR
    "Leave",
    "LeaveType",
    "LeaveStatus",
    "Loan",
    "LoanStatus",
    "Attendance",
    "AttendanceStatus",
    "Salary",
    "Asset",
    "AssetType",
    "AssetStatus",
    "Bonus",
    "BonusType",
    "PaymentStatus",
    # Operations
    "COD",
    "CODStatus",
    "Delivery",
    "DeliveryStatus",
    "Route",
    "Incident",
    "IncidentType",
    "IncidentStatus",
    # Accommodation
    "Building",
    "Room",
    "RoomStatus",
    "Bed",
    "BedStatus",
    "Allocation",
    # Workflow - Template & Instance
    "WorkflowTemplate",
    "WorkflowTemplateCategory",
    "WorkflowInstance",
    "WorkflowStatus",
    # Workflow - Approval
    "ApprovalChain",
    "ApprovalChainApprover",
    "ApprovalRequest",
    "ApprovalStatus",
    # Workflow - SLA
    "WorkflowSLA",
    "WorkflowSLAInstance",
    "SLAEvent",
    "SLAStatus",
    "SLAPriority",
    # Workflow - Automation
    "WorkflowAutomation",
    "AutomationExecutionLog",
    "AutomationTriggerType",
    "AutomationActionType",
    "AutomationStatus",
    # Workflow - Trigger
    "WorkflowTrigger",
    "TriggerExecution",
    "TriggerType",
    "TriggerEventType",
    # Workflow - Analytics
    "WorkflowMetrics",
    "WorkflowStepMetrics",
    "WorkflowPerformanceSnapshot",
    "WorkflowUserMetrics",
    # Workflow - Comment & Attachment
    "WorkflowComment",
    "WorkflowAttachment",
    "AttachmentType",
    # Workflow - History
    "WorkflowHistory",
    "WorkflowStepHistory",
    "WorkflowHistoryEventType",
    # Workflow - Notification
    "WorkflowNotificationTemplate",
    "WorkflowNotification",
    "NotificationPreference",
    "NotificationType",
    "NotificationChannel",
    "NotificationStatus",
    # Analytics
    "PerformanceData",
    "MetricSnapshot",
    "Report",
    "ReportType",
    "ReportStatus",
    "ReportFormat",
    "Dashboard",
    "KPI",
    "KPIPeriod",
    "KPITrend",
    # Tenant
    "Organization",
    "SubscriptionPlan",
    "SubscriptionStatus",
    "OrganizationUser",
    "OrganizationRole",
    # Support
    "Ticket",
    "TicketCategory",
    "TicketPriority",
    "TicketStatus",
]
