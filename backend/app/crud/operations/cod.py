from app.crud.base import CRUDBase
from app.models.operations.cod import COD
from app.schemas.operations.cod import CODCreate, CODUpdate

cod = CRUDBase[COD, CODCreate, CODUpdate](COD)
