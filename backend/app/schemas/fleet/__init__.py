"""Fleet Management Pydantic schemas"""

from app.schemas.fleet.courier import (
    CourierBase, CourierCreate, CourierUpdate, CourierResponse, CourierList,
    CourierOption, CourierBulkUpdate, CourierStats, CourierDocumentStatus
)
from app.schemas.fleet.vehicle import (
    VehicleBase, VehicleCreate, VehicleUpdate, VehicleResponse, VehicleList,
    VehicleOption, VehicleStats, VehicleDocumentStatus, VehicleBulkUpdate
)
from app.schemas.fleet.assignment import (
    AssignmentBase, AssignmentCreate, AssignmentUpdate, AssignmentResponse, AssignmentList
)
from app.schemas.fleet.vehicle_log import (
    VehicleLogBase, VehicleLogCreate, VehicleLogUpdate, VehicleLogResponse, VehicleLogList
)
from app.schemas.fleet.maintenance import (
    MaintenanceBase, MaintenanceCreate, MaintenanceUpdate, MaintenanceResponse, MaintenanceList
)
from app.schemas.fleet.inspection import (
    InspectionBase, InspectionCreate, InspectionUpdate, InspectionResponse, InspectionList
)
from app.schemas.fleet.accident_log import (
    AccidentLogBase, AccidentLogCreate, AccidentLogUpdate, AccidentLogResponse, AccidentLogList
)

__all__ = [
    # Courier
    "CourierBase", "CourierCreate", "CourierUpdate", "CourierResponse", "CourierList",
    "CourierOption", "CourierBulkUpdate", "CourierStats", "CourierDocumentStatus",

    # Vehicle
    "VehicleBase", "VehicleCreate", "VehicleUpdate", "VehicleResponse", "VehicleList",
    "VehicleOption", "VehicleStats", "VehicleDocumentStatus", "VehicleBulkUpdate",

    # Assignment
    "AssignmentBase", "AssignmentCreate", "AssignmentUpdate", "AssignmentResponse", "AssignmentList",

    # Vehicle Log
    "VehicleLogBase", "VehicleLogCreate", "VehicleLogUpdate", "VehicleLogResponse", "VehicleLogList",

    # Maintenance
    "MaintenanceBase", "MaintenanceCreate", "MaintenanceUpdate", "MaintenanceResponse", "MaintenanceList",

    # Inspection
    "InspectionBase", "InspectionCreate", "InspectionUpdate", "InspectionResponse", "InspectionList",

    # Accident Log
    "AccidentLogBase", "AccidentLogCreate", "AccidentLogUpdate", "AccidentLogResponse", "AccidentLogList",
]
