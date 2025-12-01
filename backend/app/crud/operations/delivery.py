from app.crud.base import CRUDBase
from app.models.operations.delivery import Delivery
from app.schemas.operations.delivery import DeliveryCreate, DeliveryUpdate

delivery = CRUDBase[Delivery, DeliveryCreate, DeliveryUpdate](Delivery)
