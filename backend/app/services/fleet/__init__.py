"""Fleet Management services"""

from app.services.fleet.courier import courier_service, CourierService
from app.services.fleet.vehicle import vehicle_service, VehicleService
from app.services.fleet.assignment import assignment_service, AssignmentService
from app.services.fleet.vehicle_log import vehicle_log_service, VehicleLogService
from app.services.fleet.maintenance import maintenance_service, MaintenanceService
from app.services.fleet.inspection import inspection_service, InspectionService
from app.services.fleet.accident_log import accident_log_service, AccidentLogService

__all__ = [
    # Service instances (ready to use)
    "courier_service",
    "vehicle_service",
    "assignment_service",
    "vehicle_log_service",
    "maintenance_service",
    "inspection_service",
    "accident_log_service",

    # Service classes (for customization if needed)
    "CourierService",
    "VehicleService",
    "AssignmentService",
    "VehicleLogService",
    "MaintenanceService",
    "InspectionService",
    "AccidentLogService",
]
