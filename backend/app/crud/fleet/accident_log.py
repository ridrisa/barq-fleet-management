from app.crud.base import CRUDBase
from app.models.fleet.accident_log import AccidentLog
from app.schemas.fleet.accident_log import AccidentLogCreate, AccidentLogUpdate

accident_log = CRUDBase[AccidentLog, AccidentLogCreate, AccidentLogUpdate](AccidentLog)
