"""Fleet Management models"""

from app.models.fleet.courier import Courier, CourierStatus, SponsorshipStatus, ProjectType
from app.models.fleet.vehicle import (
    Vehicle,
    VehicleStatus,
    VehicleType,
    FuelType,
    OwnershipType,
)
from app.models.fleet.assignment import (
    CourierVehicleAssignment,
    AssignmentStatus,
    AssignmentType,
)
from app.models.fleet.vehicle_log import VehicleLog, LogType, FuelProvider
from app.models.fleet.maintenance import (
    VehicleMaintenance,
    MaintenanceType,
    MaintenanceStatus,
    ServiceProvider,
)
from app.models.fleet.inspection import (
    Inspection,
    InspectionType,
    InspectionStatus,
    VehicleCondition,
)
from app.models.fleet.accident_log import (
    AccidentLog,
    AccidentSeverity,
    AccidentType,
    FaultStatus,
    AccidentStatus,
)

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
