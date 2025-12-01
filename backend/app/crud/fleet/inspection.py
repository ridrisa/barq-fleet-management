from app.crud.base import CRUDBase
from app.models.fleet.inspection import Inspection
from app.schemas.fleet.inspection import InspectionCreate, InspectionUpdate

inspection = CRUDBase[Inspection, InspectionCreate, InspectionUpdate](Inspection)
