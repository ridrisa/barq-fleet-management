from app.crud.base import CRUDBase
from app.models.accommodation.allocation import Allocation
from app.schemas.accommodation.allocation import AllocationCreate, AllocationUpdate

allocation = CRUDBase[Allocation, AllocationCreate, AllocationUpdate](Allocation)
