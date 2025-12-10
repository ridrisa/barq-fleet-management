"""
GOSI (General Organization for Social Insurance) Export API

Generates GOSI-compliant export files for Saudi Arabia social insurance reporting.
"""

import csv
import io
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.database import get_db
from app.core.dependencies import get_current_organization, get_current_user
from app.models.tenant.organization import Organization
from app.models.fleet.courier import Courier, CourierStatus
from app.models.hr.salary import Salary

router = APIRouter()


class GOSISummary(BaseModel):
    """GOSI summary report"""
    month: int
    year: int
    total_employees: int
    total_saudi_employees: int
    total_non_saudi_employees: int
    total_basic_salary: float
    total_gosi_employee_share: float
    total_gosi_employer_share: float
    total_gosi_contribution: float


# GOSI contribution rates (as of 2024)
GOSI_RATES = {
    "saudi": {
        "employee": Decimal("0.0975"),  # 9.75% employee share
        "employer": Decimal("0.1175"),  # 11.75% employer share (including SANED 0.75%)
    },
    "non_saudi": {
        "employee": Decimal("0.00"),    # 0% employee share (only hazard insurance)
        "employer": Decimal("0.02"),    # 2% employer share (hazard insurance)
    }
}

# GOSI contribution ceiling (monthly)
GOSI_CEILING = Decimal("45000")


def calculate_gosi_contribution(
    basic_salary: Decimal,
    is_saudi: bool,
) -> dict:
    """
    Calculate GOSI contribution based on nationality and salary.

    Args:
        basic_salary: Monthly basic salary in SAR
        is_saudi: True if employee is Saudi national

    Returns:
        Dictionary with employee_share, employer_share, and total
    """
    # Apply ceiling
    contributable_salary = min(basic_salary, GOSI_CEILING)

    if is_saudi:
        rates = GOSI_RATES["saudi"]
    else:
        rates = GOSI_RATES["non_saudi"]

    employee_share = contributable_salary * rates["employee"]
    employer_share = contributable_salary * rates["employer"]

    return {
        "employee_share": float(round(employee_share, 2)),
        "employer_share": float(round(employer_share, 2)),
        "total": float(round(employee_share + employer_share, 2)),
        "contributable_salary": float(contributable_salary),
    }


@router.get("/export")
def export_gosi(
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(None, description="Year (defaults to current year)"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Export GOSI report for a specific month

    Generates a CSV file with GOSI-compliant format including:
    - Employee identification
    - Salary details
    - GOSI contribution breakdown (employee/employer shares)
    - Status and nationality information
    """
    if year is None:
        year = date.today().year

    # Get all active couriers with their salaries
    couriers = (
        db.query(Courier)
        .filter(
            Courier.organization_id == current_org.id,
            Courier.status.in_([CourierStatus.ACTIVE, CourierStatus.ON_LEAVE]),
        )
        .all()
    )

    # Get salaries for the month
    salaries_query = (
        db.query(Salary)
        .filter(
            Salary.organization_id == current_org.id,
            Salary.month == month,
            Salary.year == year,
        )
    )
    salaries_map = {s.courier_id: s for s in salaries_query.all()}

    # Build GOSI records
    records = []
    total_basic = Decimal("0")
    total_employee_share = Decimal("0")
    total_employer_share = Decimal("0")
    saudi_count = 0
    non_saudi_count = 0

    for courier in couriers:
        salary = salaries_map.get(courier.id)
        if not salary:
            continue

        # Determine if Saudi (Saudi nationality or has national_id starting with 1)
        is_saudi = (
            courier.nationality and courier.nationality.lower() in ["saudi", "saudi arabia", "sa", "ksa"]
        ) or (courier.national_id and courier.national_id.startswith("1"))

        if is_saudi:
            saudi_count += 1
        else:
            non_saudi_count += 1

        basic_salary = Decimal(str(salary.base_salary or 0))
        housing_allowance = basic_salary * Decimal("0.25")  # Standard 25% housing

        gosi = calculate_gosi_contribution(basic_salary, is_saudi)

        total_basic += basic_salary
        total_employee_share += Decimal(str(gosi["employee_share"]))
        total_employer_share += Decimal(str(gosi["employer_share"]))

        records.append({
            "employee_id": courier.employee_id or courier.barq_id,
            "name": courier.full_name,
            "national_id": courier.national_id or "",
            "iqama_number": courier.iqama_number or "",
            "nationality": courier.nationality or "Unknown",
            "date_of_birth": courier.date_of_birth.isoformat() if courier.date_of_birth else "",
            "joining_date": courier.joining_date.isoformat() if courier.joining_date else "",
            "basic_salary": float(basic_salary),
            "housing_allowance": float(housing_allowance),
            "total_salary": float(salary.net_salary or 0),
            "gosi_employee_share": gosi["employee_share"],
            "gosi_employer_share": gosi["employer_share"],
            "gosi_total": gosi["total"],
            "contributable_salary": gosi["contributable_salary"],
            "is_saudi": "Yes" if is_saudi else "No",
            "status": courier.status.value if courier.status else "Unknown",
        })

    # Create CSV output
    output = io.StringIO()
    writer = csv.writer(output)

    # Header row with Arabic/English column names (GOSI format)
    writer.writerow([
        "Employee ID / رقم الموظف",
        "Name / الاسم",
        "National ID / رقم الهوية",
        "Iqama Number / رقم الإقامة",
        "Nationality / الجنسية",
        "Date of Birth / تاريخ الميلاد",
        "Joining Date / تاريخ الالتحاق",
        "Basic Salary / الراتب الأساسي",
        "Housing Allowance / بدل السكن",
        "Total Salary / إجمالي الراتب",
        "Contributable Salary / الراتب الخاضع للاشتراك",
        "Employee Share / حصة الموظف",
        "Employer Share / حصة صاحب العمل",
        "Total GOSI / إجمالي التأمينات",
        "Saudi / سعودي",
        "Status / الحالة",
    ])

    # Data rows
    for record in records:
        writer.writerow([
            record["employee_id"],
            record["name"],
            record["national_id"],
            record["iqama_number"],
            record["nationality"],
            record["date_of_birth"],
            record["joining_date"],
            record["basic_salary"],
            record["housing_allowance"],
            record["total_salary"],
            record["contributable_salary"],
            record["gosi_employee_share"],
            record["gosi_employer_share"],
            record["gosi_total"],
            record["is_saudi"],
            record["status"],
        ])

    # Summary row
    writer.writerow([])
    writer.writerow(["SUMMARY / ملخص"])
    writer.writerow(["Month / الشهر", month])
    writer.writerow(["Year / السنة", year])
    writer.writerow(["Total Employees / إجمالي الموظفين", len(records)])
    writer.writerow(["Saudi Employees / الموظفين السعوديين", saudi_count])
    writer.writerow(["Non-Saudi Employees / الموظفين غير السعوديين", non_saudi_count])
    writer.writerow(["Total Basic Salary / إجمالي الراتب الأساسي", float(total_basic)])
    writer.writerow(["Total Employee Share / إجمالي حصة الموظفين", float(total_employee_share)])
    writer.writerow(["Total Employer Share / إجمالي حصة صاحب العمل", float(total_employer_share)])
    writer.writerow(["Total GOSI Contribution / إجمالي التأمينات", float(total_employee_share + total_employer_share)])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=gosi_report_{year}_{month:02d}.csv"
        },
    )


@router.get("/summary", response_model=GOSISummary)
def get_gosi_summary(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get GOSI summary for a specific month"""
    if year is None:
        year = date.today().year

    # Get all active couriers with their salaries
    couriers = (
        db.query(Courier)
        .filter(
            Courier.organization_id == current_org.id,
            Courier.status.in_([CourierStatus.ACTIVE, CourierStatus.ON_LEAVE]),
        )
        .all()
    )

    salaries_map = {
        s.courier_id: s
        for s in db.query(Salary).filter(
            Salary.organization_id == current_org.id,
            Salary.month == month,
            Salary.year == year,
        ).all()
    }

    total_basic = Decimal("0")
    total_employee_share = Decimal("0")
    total_employer_share = Decimal("0")
    saudi_count = 0
    non_saudi_count = 0
    employee_count = 0

    for courier in couriers:
        salary = salaries_map.get(courier.id)
        if not salary:
            continue

        employee_count += 1

        is_saudi = (
            courier.nationality and courier.nationality.lower() in ["saudi", "saudi arabia", "sa", "ksa"]
        ) or (courier.national_id and courier.national_id.startswith("1"))

        if is_saudi:
            saudi_count += 1
        else:
            non_saudi_count += 1

        basic_salary = Decimal(str(salary.base_salary or 0))
        gosi = calculate_gosi_contribution(basic_salary, is_saudi)

        total_basic += basic_salary
        total_employee_share += Decimal(str(gosi["employee_share"]))
        total_employer_share += Decimal(str(gosi["employer_share"]))

    return GOSISummary(
        month=month,
        year=year,
        total_employees=employee_count,
        total_saudi_employees=saudi_count,
        total_non_saudi_employees=non_saudi_count,
        total_basic_salary=float(total_basic),
        total_gosi_employee_share=float(total_employee_share),
        total_gosi_employer_share=float(total_employer_share),
        total_gosi_contribution=float(total_employee_share + total_employer_share),
    )
