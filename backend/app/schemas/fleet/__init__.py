"""Fleet Management Pydantic schemas"""

from app.schemas.fleet.accident_log import (
    AccidentLogBase,
    AccidentLogCreate,
    AccidentLogList,
    AccidentLogResponse,
    AccidentLogUpdate,
)
from app.schemas.fleet.assignment import (
    AssignmentBase,
    AssignmentCreate,
    AssignmentList,
    AssignmentResponse,
    AssignmentUpdate,
    CurrentAssignment,
)
from app.schemas.fleet.courier import (
    CourierBase,
    CourierBulkUpdate,
    CourierCreate,
    CourierDocumentStatus,
    CourierList,
    CourierOption,
    CourierResponse,
    CourierStats,
    CourierUpdate,
)
from app.schemas.fleet.inspection import (
    InspectionBase,
    InspectionCreate,
    InspectionList,
    InspectionResponse,
    InspectionUpdate,
)
from app.schemas.fleet.maintenance import (
    MaintenanceBase,
    MaintenanceCreate,
    MaintenanceList,
    MaintenanceResponse,
    MaintenanceUpdate,
)
from app.schemas.fleet.vehicle import (
    VehicleBase,
    VehicleBulkUpdate,
    VehicleCreate,
    VehicleDocumentStatus,
    VehicleList,
    VehicleOption,
    VehicleResponse,
    VehicleStats,
    VehicleUpdate,
)
from app.schemas.fleet.vehicle_log import (
    VehicleLogBase,
    VehicleLogCreate,
    VehicleLogList,
    VehicleLogResponse,
    VehicleLogUpdate,
)

__all__ = [
    # Courier
    "CourierBase",
    "CourierCreate",
    "CourierUpdate",
    "CourierResponse",
    "CourierList",
    "CourierOption",
    "CourierBulkUpdate",
    "CourierStats",
    "CourierDocumentStatus",
    # Vehicle
    "VehicleBase",
    "VehicleCreate",
    "VehicleUpdate",
    "VehicleResponse",
    "VehicleList",
    "VehicleOption",
    "VehicleStats",
    "VehicleDocumentStatus",
    "VehicleBulkUpdate",
    # Assignment
    "AssignmentBase",
    "AssignmentCreate",
    "AssignmentUpdate",
    "AssignmentResponse",
    "AssignmentList",
    "CurrentAssignment",
    # Vehicle Log
    "VehicleLogBase",
    "VehicleLogCreate",
    "VehicleLogUpdate",
    "VehicleLogResponse",
    "VehicleLogList",
    # Maintenance
    "MaintenanceBase",
    "MaintenanceCreate",
    "MaintenanceUpdate",
    "MaintenanceResponse",
    "MaintenanceList",
    # Inspection
    "InspectionBase",
    "InspectionCreate",
    "InspectionUpdate",
    "InspectionResponse",
    "InspectionList",
    # Accident Log
    "AccidentLogBase",
    "AccidentLogCreate",
    "AccidentLogUpdate",
    "AccidentLogResponse",
    "AccidentLogList",
]
