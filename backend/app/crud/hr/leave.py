from app.crud.base import CRUDBase
from app.models.hr.leave import Leave
from app.schemas.hr.leave import LeaveCreate, LeaveUpdate

leave = CRUDBase[Leave, LeaveCreate, LeaveUpdate](Leave)
