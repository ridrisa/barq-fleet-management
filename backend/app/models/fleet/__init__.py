"""Fleet Management models"""

from app.models.fleet.accident_log import (
    AccidentLog,
    AccidentSeverity,
    AccidentStatus,
    AccidentType,
    FaultStatus,
)
from app.models.fleet.assignment import (
    AssignmentStatus,
    AssignmentType,
    CourierVehicleAssignment,
)
from app.models.fleet.courier import Courier, CourierStatus, ProjectType, SponsorshipStatus
from app.models.fleet.inspection import (
    Inspection,
    InspectionStatus,
    InspectionType,
    VehicleCondition,
)
from app.models.fleet.maintenance import (
    MaintenanceStatus,
    MaintenanceType,
    ServiceProvider,
    VehicleMaintenance,
)
from app.models.fleet.vehicle import (
    FuelType,
    OwnershipType,
    Vehicle,
    VehicleStatus,
    VehicleType,
)
from app.models.fleet.vehicle_log import FuelProvider, LogType, VehicleLog

__all__ = [
    # Models
    "Courier",
    "Vehicle",
    "CourierVehicleAssignment",
    "VehicleLog",
    "VehicleMaintenance",
    "Inspection",
    "AccidentLog",
    # Courier Enums
    "CourierStatus",
    "SponsorshipStatus",
    "ProjectType",
    # Vehicle Enums
    "VehicleStatus",
    "VehicleType",
    "FuelType",
    "OwnershipType",
    # Assignment Enums
    "AssignmentStatus",
    "AssignmentType",
    # Vehicle Log Enums
    "LogType",
    "FuelProvider",
    # Maintenance Enums
    "MaintenanceType",
    "MaintenanceStatus",
    "ServiceProvider",
    # Inspection Enums
    "InspectionType",
    "InspectionStatus",
    "VehicleCondition",
    # Accident Log Enums
    "AccidentSeverity",
    "AccidentType",
    "FaultStatus",
    "AccidentStatus",
]
