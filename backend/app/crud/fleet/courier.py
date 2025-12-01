from app.crud.base import CRUDBase
from app.models.fleet.courier import Courier
from app.schemas.fleet.courier import CourierCreate, CourierUpdate

courier = CRUDBase[Courier, CourierCreate, CourierUpdate](Courier)
