"""
End of Service (EOS) Benefits Calculation and Export API

Calculates End of Service benefits according to Saudi Arabian Labor Law.
Generates EOS reports for terminated employees.
"""

import csv
import io
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.dependencies import get_current_organization, get_current_user
from app.models.tenant.organization import Organization
from app.models.fleet.courier import Courier, CourierStatus
from app.models.hr.salary import Salary

router = APIRouter()


class EOSCalculation(BaseModel):
    """EOS calculation result"""
    courier_id: int
    employee_id: str
    name: str
    joining_date: date
    termination_date: date
    years_of_service: float
    months_of_service: int
    days_of_service: int
    last_basic_salary: float
    eos_amount: float
    calculation_type: str  # full, two_thirds, one_third, resignation
    calculation_breakdown: dict


class EOSSummary(BaseModel):
    """EOS summary for multiple employees"""
    total_employees: int
    total_eos_amount: float
    by_termination_type: dict


def calculate_eos_benefit(
    joining_date: date,
    termination_date: date,
    basic_salary: Decimal,
    is_resignation: bool = False,
) -> dict:
    """
    Calculate End of Service benefits according to Saudi Labor Law.

    Per Saudi Labor Law Article 84-85:
    - First 5 years: 15 days salary per year (1/2 month)
    - After 5 years: 30 days salary per year (1 month)

    Resignation rules (Article 85):
    - Less than 2 years: No EOS
    - 2-5 years: 1/3 of total EOS
    - 5-10 years: 2/3 of total EOS
    - More than 10 years: Full EOS

    Termination by employer: Full EOS
    """
    # Calculate service period
    service_days = (termination_date - joining_date).days
    service_years = service_days / 365.25
    service_months = int(service_days / 30.4375)

    # Daily wage (salary / 30)
    daily_wage = basic_salary / Decimal("30")

    # Calculate full EOS first
    full_years = int(service_years)
    remaining_fraction = Decimal(str(service_years - full_years))

    # First 5 years: 15 days per year
    years_in_first_tier = min(full_years, 5)
    first_tier_eos = years_in_first_tier * daily_wage * Decimal("15")

    # Years after 5: 30 days per year
    years_in_second_tier = max(0, full_years - 5)
    second_tier_eos = years_in_second_tier * daily_wage * Decimal("30")

    # Fractional year calculation
    if full_years < 5:
        fractional_eos = remaining_fraction * daily_wage * Decimal("15")
    else:
        fractional_eos = remaining_fraction * daily_wage * Decimal("30")

    full_eos = first_tier_eos + second_tier_eos + fractional_eos

    # Apply resignation discount if applicable
    calculation_type = "full"
    if is_resignation:
        if service_years < 2:
            final_eos = Decimal("0")
            calculation_type = "resignation_no_entitlement"
        elif service_years < 5:
            final_eos = full_eos / Decimal("3")
            calculation_type = "resignation_one_third"
        elif service_years < 10:
            final_eos = full_eos * Decimal("2") / Decimal("3")
            calculation_type = "resignation_two_thirds"
        else:
            final_eos = full_eos
            calculation_type = "resignation_full"
    else:
        final_eos = full_eos

    return {
        "years_of_service": round(service_years, 2),
        "months_of_service": service_months,
        "days_of_service": service_days,
        "daily_wage": float(daily_wage),
        "first_tier_years": years_in_first_tier,
        "first_tier_amount": float(first_tier_eos),
        "second_tier_years": years_in_second_tier,
        "second_tier_amount": float(second_tier_eos),
        "fractional_amount": float(fractional_eos),
        "full_eos": float(full_eos),
        "final_eos": float(round(final_eos, 2)),
        "calculation_type": calculation_type,
    }


@router.get("/export/{courier_id}")
def export_eos(
    courier_id: int,
    termination_date: date = Query(None, description="Termination date (defaults to today)"),
    is_resignation: bool = Query(False, description="Whether this is a resignation"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Export End of Service calculation report for a courier

    Generates a detailed EOS calculation report including:
    - Service period breakdown
    - Salary information
    - EOS calculation according to Saudi Labor Law
    - Final entitlement amount
    """
    # Get courier
    courier = (
        db.query(Courier)
        .filter(
            Courier.id == courier_id,
            Courier.organization_id == current_org.id,
        )
        .first()
    )

    if not courier:
        raise HTTPException(status_code=404, detail="Courier not found")

    if not courier.joining_date:
        raise HTTPException(status_code=400, detail="Courier joining date is not set")

    # Use provided termination date or today
    term_date = termination_date or date.today()

    # Get last salary to determine basic salary
    last_salary = (
        db.query(Salary)
        .filter(Salary.courier_id == courier_id)
        .order_by(Salary.year.desc(), Salary.month.desc())
        .first()
    )

    basic_salary = Decimal(str(last_salary.base_salary if last_salary else 3000))

    # Calculate EOS
    eos = calculate_eos_benefit(
        joining_date=courier.joining_date,
        termination_date=term_date,
        basic_salary=basic_salary,
        is_resignation=is_resignation,
    )

    # Create CSV report
    output = io.StringIO()
    writer = csv.writer(output)

    # Report header
    writer.writerow(["END OF SERVICE (EOS) CALCULATION REPORT"])
    writer.writerow(["مكافأة نهاية الخدمة"])
    writer.writerow([])

    # Employee information
    writer.writerow(["EMPLOYEE INFORMATION / معلومات الموظف"])
    writer.writerow(["Employee ID / رقم الموظف", courier.employee_id or courier.barq_id])
    writer.writerow(["Name / الاسم", courier.full_name])
    writer.writerow(["National ID / رقم الهوية", courier.national_id or "N/A"])
    writer.writerow(["Iqama Number / رقم الإقامة", courier.iqama_number or "N/A"])
    writer.writerow(["Nationality / الجنسية", courier.nationality or "N/A"])
    writer.writerow([])

    # Service period
    writer.writerow(["SERVICE PERIOD / فترة الخدمة"])
    writer.writerow(["Joining Date / تاريخ الالتحاق", courier.joining_date.isoformat()])
    writer.writerow(["Termination Date / تاريخ انتهاء الخدمة", term_date.isoformat()])
    writer.writerow(["Years of Service / سنوات الخدمة", eos["years_of_service"]])
    writer.writerow(["Months of Service / أشهر الخدمة", eos["months_of_service"]])
    writer.writerow(["Days of Service / أيام الخدمة", eos["days_of_service"]])
    writer.writerow([])

    # Salary information
    writer.writerow(["SALARY INFORMATION / معلومات الراتب"])
    writer.writerow(["Last Basic Salary / آخر راتب أساسي (SAR)", float(basic_salary)])
    writer.writerow(["Daily Wage / الأجر اليومي (SAR)", eos["daily_wage"]])
    writer.writerow([])

    # EOS calculation
    writer.writerow(["EOS CALCULATION / حساب مكافأة نهاية الخدمة"])
    writer.writerow(["Termination Type / نوع الإنهاء", "Resignation" if is_resignation else "Employer Termination"])
    writer.writerow([])

    writer.writerow(["First 5 Years (15 days/year) / أول 5 سنوات"])
    writer.writerow(["  Years in Tier / السنوات", eos["first_tier_years"]])
    writer.writerow(["  Amount / المبلغ (SAR)", eos["first_tier_amount"]])
    writer.writerow([])

    writer.writerow(["After 5 Years (30 days/year) / بعد 5 سنوات"])
    writer.writerow(["  Years in Tier / السنوات", eos["second_tier_years"]])
    writer.writerow(["  Amount / المبلغ (SAR)", eos["second_tier_amount"]])
    writer.writerow([])

    writer.writerow(["Fractional Year / الجزء المتبقي (SAR)", eos["fractional_amount"]])
    writer.writerow([])

    writer.writerow(["Full EOS Entitlement / المستحق الكامل (SAR)", eos["full_eos"]])
    writer.writerow(["Calculation Type / نوع الحساب", eos["calculation_type"]])
    writer.writerow([])

    # Final amount
    writer.writerow(["=" * 50])
    writer.writerow(["FINAL EOS AMOUNT / المبلغ النهائي (SAR)", eos["final_eos"]])
    writer.writerow(["=" * 50])
    writer.writerow([])

    # Legal reference
    writer.writerow(["Legal Reference / المرجع القانوني"])
    writer.writerow(["Saudi Labor Law Articles 84-85 / نظام العمل السعودي المواد 84-85"])
    writer.writerow([])

    # Report generation info
    writer.writerow(["Report Generated / تاريخ إصدار التقرير", datetime.now().isoformat()])
    writer.writerow(["Generated By / صادر من", f"User {getattr(current_user, 'id', 'N/A')}"])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=eos_report_{courier.barq_id}_{term_date.isoformat()}.csv"
        },
    )


@router.get("/calculate/{courier_id}", response_model=EOSCalculation)
def calculate_eos(
    courier_id: int,
    termination_date: date = Query(None, description="Termination date (defaults to today)"),
    is_resignation: bool = Query(False, description="Whether this is a resignation"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Calculate End of Service benefits for a courier

    Returns the calculated EOS amount based on:
    - Service period
    - Last basic salary
    - Termination type (resignation vs employer termination)
    """
    # Get courier
    courier = (
        db.query(Courier)
        .filter(
            Courier.id == courier_id,
            Courier.organization_id == current_org.id,
        )
        .first()
    )

    if not courier:
        raise HTTPException(status_code=404, detail="Courier not found")

    if not courier.joining_date:
        raise HTTPException(status_code=400, detail="Courier joining date is not set")

    # Use provided termination date or today
    term_date = termination_date or date.today()

    # Get last salary
    last_salary = (
        db.query(Salary)
        .filter(Salary.courier_id == courier_id)
        .order_by(Salary.year.desc(), Salary.month.desc())
        .first()
    )

    basic_salary = Decimal(str(last_salary.base_salary if last_salary else 3000))

    # Calculate EOS
    eos = calculate_eos_benefit(
        joining_date=courier.joining_date,
        termination_date=term_date,
        basic_salary=basic_salary,
        is_resignation=is_resignation,
    )

    return EOSCalculation(
        courier_id=courier_id,
        employee_id=courier.employee_id or courier.barq_id,
        name=courier.full_name,
        joining_date=courier.joining_date,
        termination_date=term_date,
        years_of_service=eos["years_of_service"],
        months_of_service=eos["months_of_service"],
        days_of_service=eos["days_of_service"],
        last_basic_salary=float(basic_salary),
        eos_amount=eos["final_eos"],
        calculation_type=eos["calculation_type"],
        calculation_breakdown={
            "first_tier": {
                "years": eos["first_tier_years"],
                "amount": eos["first_tier_amount"],
            },
            "second_tier": {
                "years": eos["second_tier_years"],
                "amount": eos["second_tier_amount"],
            },
            "fractional": eos["fractional_amount"],
            "full_eos": eos["full_eos"],
            "daily_wage": eos["daily_wage"],
        },
    )


@router.get("/batch-export")
def batch_export_eos(
    status_filter: str = Query("TERMINATED", description="Courier status to filter"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Export EOS for all terminated employees

    Generates a summary CSV for all employees matching the status filter.
    """
    # Get terminated couriers
    couriers = (
        db.query(Courier)
        .filter(
            Courier.organization_id == current_org.id,
            Courier.status == CourierStatus.TERMINATED,
            Courier.joining_date.isnot(None),
            Courier.last_working_day.isnot(None),
        )
        .all()
    )

    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Employee ID",
        "Name",
        "Joining Date",
        "Termination Date",
        "Years of Service",
        "Last Basic Salary (SAR)",
        "Full EOS (SAR)",
        "Final EOS (SAR)",
        "Calculation Type",
    ])

    total_eos = Decimal("0")

    for courier in couriers:
        # Get last salary
        last_salary = (
            db.query(Salary)
            .filter(Salary.courier_id == courier.id)
            .order_by(Salary.year.desc(), Salary.month.desc())
            .first()
        )

        basic_salary = Decimal(str(last_salary.base_salary if last_salary else 3000))
        term_date = courier.last_working_day or date.today()

        # Calculate EOS (assuming employer termination for batch)
        eos = calculate_eos_benefit(
            joining_date=courier.joining_date,
            termination_date=term_date,
            basic_salary=basic_salary,
            is_resignation=False,
        )

        total_eos += Decimal(str(eos["final_eos"]))

        writer.writerow([
            courier.employee_id or courier.barq_id,
            courier.full_name,
            courier.joining_date.isoformat(),
            term_date.isoformat(),
            eos["years_of_service"],
            float(basic_salary),
            eos["full_eos"],
            eos["final_eos"],
            eos["calculation_type"],
        ])

    # Summary
    writer.writerow([])
    writer.writerow(["TOTAL", "", "", "", "", "", "", float(total_eos), ""])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=eos_batch_report_{date.today().isoformat()}.csv"
        },
    )
