from app.crud.base import CRUDBase
from app.models.accommodation.bed import Bed
from app.schemas.accommodation.bed import BedCreate, BedUpdate

bed = CRUDBase[Bed, BedCreate, BedUpdate](Bed)
