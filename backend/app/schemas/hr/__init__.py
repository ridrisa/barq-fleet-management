from app.schemas.hr.leave import (
    LeaveType, LeaveStatus,
    LeaveBase, LeaveCreate, LeaveUpdate, LeaveResponse
)
from app.schemas.hr.loan import (
    LoanStatus,
    LoanBase, LoanCreate, LoanUpdate, LoanResponse
)
from app.schemas.hr.attendance import (
    AttendanceStatus,
    AttendanceBase, AttendanceCreate, AttendanceUpdate, AttendanceResponse
)
from app.schemas.hr.salary import (
    SalaryBase, SalaryCreate, SalaryUpdate, SalaryResponse
)
from app.schemas.hr.asset import (
    AssetType, AssetStatus,
    AssetBase, AssetCreate, AssetUpdate, AssetResponse
)

__all__ = [
    "LeaveType", "LeaveStatus",
    "LeaveBase", "LeaveCreate", "LeaveUpdate", "LeaveResponse",
    "LoanStatus",
    "LoanBase", "LoanCreate", "LoanUpdate", "LoanResponse",
    "AttendanceStatus",
    "AttendanceBase", "AttendanceCreate", "AttendanceUpdate", "AttendanceResponse",
    "SalaryBase", "SalaryCreate", "SalaryUpdate", "SalaryResponse",
    "AssetType", "AssetStatus",
    "AssetBase", "AssetCreate", "AssetUpdate", "AssetResponse",
]
