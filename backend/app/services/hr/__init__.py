"""HR Services Package"""
from app.services.hr.leave_service import LeaveService, leave_service
from app.services.hr.attendance_service import AttendanceService, attendance_service
from app.services.hr.loan_service import LoanService, loan_service
from app.services.hr.salary_service import SalaryService, salary_service
from app.services.hr.asset_service import AssetService, asset_service
from app.services.hr.gosi_calculator_service import GOSICalculatorService, gosi_calculator_service
from app.services.hr.eos_calculator_service import EOSCalculatorService, eos_calculator_service
from app.services.hr.payroll_engine_service import PayrollEngineService, payroll_engine_service

__all__ = [
    # Service classes
    "LeaveService",
    "AttendanceService",
    "LoanService",
    "SalaryService",
    "AssetService",
    "GOSICalculatorService",
    "EOSCalculatorService",
    "PayrollEngineService",
    # Service instances
    "leave_service",
    "attendance_service",
    "loan_service",
    "salary_service",
    "asset_service",
    "gosi_calculator_service",
    "eos_calculator_service",
    "payroll_engine_service",
]
