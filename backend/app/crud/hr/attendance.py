from app.crud.base import CRUDBase
from app.models.hr.attendance import Attendance
from app.schemas.hr.attendance import AttendanceCreate, AttendanceUpdate

attendance = CRUDBase[Attendance, AttendanceCreate, AttendanceUpdate](Attendance)
