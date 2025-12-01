from app.crud.base import CRUDBase
from app.models.fleet.fuel_log import FuelLog
from app.schemas.fleet.fuel_log import FuelLogCreate, FuelLogUpdate

fuel_log = CRUDBase[FuelLog, FuelLogCreate, FuelLogUpdate](FuelLog)
