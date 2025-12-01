from app.crud.base import CRUDBase
from app.models.fleet.vehicle import Vehicle
from app.schemas.fleet.vehicle import VehicleCreate, VehicleUpdate

vehicle = CRUDBase[Vehicle, VehicleCreate, VehicleUpdate](Vehicle)
