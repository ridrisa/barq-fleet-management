from app.crud.base import CRUDBase
from app.models.fleet.assignment import CourierVehicleAssignment
from app.schemas.fleet.assignment import AssignmentCreate, AssignmentUpdate

assignment = CRUDBase[CourierVehicleAssignment, AssignmentCreate, AssignmentUpdate](
    CourierVehicleAssignment
)
