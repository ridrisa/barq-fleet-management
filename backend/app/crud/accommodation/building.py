from app.crud.base import CRUDBase
from app.models.accommodation.building import Building
from app.schemas.accommodation.building import BuildingCreate, BuildingUpdate

building = CRUDBase[Building, BuildingCreate, BuildingUpdate](Building)
