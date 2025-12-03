"""Fleet Management services"""

from app.services.fleet.accident_log import AccidentLogService, accident_log_service
from app.services.fleet.assignment import AssignmentService, assignment_service
from app.services.fleet.courier import CourierService, courier_service
from app.services.fleet.inspection import InspectionService, inspection_service
from app.services.fleet.maintenance import MaintenanceService, maintenance_service
from app.services.fleet.vehicle import VehicleService, vehicle_service
from app.services.fleet.vehicle_log import VehicleLogService, vehicle_log_service

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
