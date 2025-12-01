from app.crud.base import CRUDBase
from app.models.fleet.maintenance import VehicleMaintenance
from app.schemas.fleet.maintenance import MaintenanceCreate, MaintenanceUpdate

maintenance = CRUDBase[VehicleMaintenance, MaintenanceCreate, MaintenanceUpdate](VehicleMaintenance)
