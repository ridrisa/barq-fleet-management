from app.models.base import BaseModel
from app.models.user import User
from app.models.audit_log import AuditLog, AuditAction

# ============================================================================
# RBAC Models - Fixed bidirectional relationships
# ============================================================================
from app.models.role import Role, Permission, PermissionAction, PermissionResource

# ============================================================================
# Admin Models - System Management
# ============================================================================
from app.models.admin.api_key import ApiKey, ApiKeyStatus
from app.models.admin.integration import Integration, IntegrationType, IntegrationStatus
from app.models.admin.system_setting import SystemSetting, SettingType, SettingCategory
from app.models.admin.backup import Backup, BackupType, BackupStatus, BackupStorage

# ============================================================================
# Fleet Models - Fixed bidirectional relationships
# ============================================================================
from app.models.fleet.fuel_log import FuelLog
from app.models.fleet.vehicle import Vehicle
from app.models.fleet.courier import Courier
from app.models.fleet.assignment import CourierVehicleAssignment
from app.models.fleet.maintenance import VehicleMaintenance
from app.models.fleet.inspection import Inspection
from app.models.fleet.accident_log import AccidentLog
from app.models.fleet.vehicle_log import VehicleLog
from app.models.fleet.document import Document, DocumentType, DocumentEntity

# ============================================================================
# HR Models - Fixed bidirectional relationships
# ============================================================================
from app.models.hr.leave import Leave, LeaveType, LeaveStatus
from app.models.hr.loan import Loan, LoanStatus
from app.models.hr.attendance import Attendance, AttendanceStatus
from app.models.hr.salary import Salary
from app.models.hr.asset import Asset, AssetType, AssetStatus
from app.models.hr.bonus import Bonus, BonusType, PaymentStatus

# ============================================================================
# Operations Models - Working relationships
# ============================================================================
from app.models.operations.cod import COD, CODStatus
from app.models.operations.delivery import Delivery, DeliveryStatus
from app.models.operations.route import Route
from app.models.operations.incident import Incident, IncidentType, IncidentStatus

# ============================================================================
# Accommodation Models - Working relationships
# ============================================================================
from app.models.accommodation.building import Building
from app.models.accommodation.room import Room, RoomStatus
from app.models.accommodation.bed import Bed, BedStatus
from app.models.accommodation.allocation import Allocation

# ============================================================================
# Workflow Models - Working relationships
# ============================================================================
from app.models.workflow.template import WorkflowTemplate
from app.models.workflow.instance import WorkflowInstance, WorkflowStatus

# ============================================================================
# Analytics Models - Working relationships
# ============================================================================
from app.models.analytics.performance import PerformanceData

# ============================================================================
# Tenant Models - Working relationships
# ============================================================================
from app.models.tenant.organization import Organization, SubscriptionPlan, SubscriptionStatus
from app.models.tenant.organization_user import OrganizationUser, OrganizationRole

# ============================================================================
# Support Models - Working relationships
# ============================================================================
from app.models.support.ticket import Ticket, TicketCategory, TicketPriority, TicketStatus

__all__ = [
    # Base
    "BaseModel",
    "User",
    "AuditLog",
    "AuditAction",
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
    # Workflow
    "WorkflowTemplate",
    "WorkflowInstance",
    "WorkflowStatus",
    # Analytics
    "PerformanceData",
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
