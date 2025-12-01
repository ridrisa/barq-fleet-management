from app.crud.base import CRUDBase
from app.models.fleet.vehicle_log import VehicleLog
from app.schemas.fleet.vehicle_log import VehicleLogCreate, VehicleLogUpdate

vehicle_log = CRUDBase[VehicleLog, VehicleLogCreate, VehicleLogUpdate](VehicleLog)
