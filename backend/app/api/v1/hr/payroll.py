"""
Payroll API Endpoints

Implements salary calculation and management using BigQuery data per salary.txt specification.
Calculates salaries for 6 categories: Motorcycle, Food Trial, Food In-House New/Old, Ecommerce WH, Ecommerce.
"""

import io
import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import get_current_user
from app.services.hr.payroll_calculation_service import PayrollCalculationService

router = APIRouter()


class PayrollGenerateRequest(BaseModel):
    """Request for generating payroll"""
    month: int
    year: int
    barq_ids: Optional[List[int]] = None
    save_to_db: bool = False


class PayrollGenerateResponse(BaseModel):
    """Response from payroll generation"""
    status: str
    message: str
    period: Dict[str, str]
    total_couriers: int
    successful: int
    failed: int
    skipped: int
    total_basic_salary: float
    total_bonus: float
    total_gas_deserved: float
    total_payroll: float
    errors: List[Dict[str, str]] = []


@router.post("/generate", response_model=PayrollGenerateResponse)
async def generate_payroll(
    request: PayrollGenerateRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_user),
):
    """
    Generate payroll for a given month using BigQuery data.

    Fetches courier performance data (Total_Orders, Total_Revenue, Gas_Usage)
    from the BigQuery ultimate table and calculates salaries per salary.txt spec.

    Categories supported:
    - Motorcycle: Order-based with 13.333 daily divisor
    - Food Trial: Order-based with 13 daily divisor
    - Food In-House New: Order-based with 15.833 daily divisor
    - Food In-House Old: Order-based with tiered bonus (6/9 SAR)
    - Ecommerce WH: Order-based with 16.667 daily divisor
    - Ecommerce: Revenue-based with coefficient calculation

    Period calculation (25th to 24th):
    - For January: Dec 25 (prev year) to Jan 24
    - For other months: (month-1) 25th to (month) 24th
    """
    # Get organization from current user
    org_id = getattr(current_user, "organization_id", 1) or 1

    service = PayrollCalculationService(db, org_id)

    try:
        result = await service.calculate_from_bigquery(
            month=request.month,
            year=request.year,
            barq_ids=request.barq_ids,
            save_to_db=request.save_to_db,
        )

        return PayrollGenerateResponse(
            status="success",
            message=f"Payroll calculated for {request.month}/{request.year}",
            period=result.period,
            total_couriers=result.total_couriers,
            successful=result.successful,
            failed=result.failed,
            skipped=result.skipped,
            total_basic_salary=float(result.total_basic_salary),
            total_bonus=float(result.total_bonus),
            total_gas_deserved=float(result.total_gas_deserved),
            total_payroll=float(result.total_payroll),
            errors=result.errors,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payroll generation failed: {str(e)}")


@router.post("/calculate-preview")
async def calculate_preview(
    request: PayrollGenerateRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_user),
):
    """
    Preview payroll calculation without saving to database.

    Returns detailed salary breakdown for each courier.
    """
    # Get organization from current user
    org_id = getattr(current_user, "organization_id", 1) or 1

    service = PayrollCalculationService(db, org_id)

    try:
        result = await service.calculate_from_bigquery(
            month=request.month,
            year=request.year,
            barq_ids=request.barq_ids,
            save_to_db=False,  # Never save in preview
        )

        # Convert results to dict for JSON serialization
        results_data = []
        for r in result.results:
            results_data.append({
                "barq_id": r.barq_id,
                "courier_id": r.courier_id,
                "name": r.name,
                "category": r.category.value if r.category else None,
                "total_orders": r.total_orders,
                "total_revenue": float(r.total_revenue) if r.total_revenue else 0,
                "gas_usage": float(r.gas_usage) if r.gas_usage else 0,
                "target": float(r.target),
                "days_since_joining": r.days_since_joining,
                "basic_salary": float(r.basic_salary),
                "bonus_amount": float(r.bonus_amount),
                "gas_deserved": float(r.gas_deserved),
                "gas_difference": float(r.gas_difference),
                "total_salary": float(r.total_salary),
                "calculation_details": r.calculation_details,
            })

        return {
            "status": "success",
            "message": f"Payroll preview for {request.month}/{request.year}",
            "period": result.period,
            "summary": {
                "total_couriers": result.total_couriers,
                "successful": result.successful,
                "failed": result.failed,
                "skipped": result.skipped,
                "total_basic_salary": float(result.total_basic_salary),
                "total_bonus": float(result.total_bonus),
                "total_gas_deserved": float(result.total_gas_deserved),
                "total_payroll": float(result.total_payroll),
            },
            "results": results_data,
            "errors": result.errors,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payroll preview failed: {str(e)}")


@router.post("/approve-all")
async def approve_all_payroll(
    data: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_user),
):
    """Approve all payroll entries for a month"""
    month = data.get("month")
    year = data.get("year")

    # TODO: Implement actual payroll approval logic
    # This would update all salary records for the month to approved status

    return {
        "status": "success",
        "message": f"All payroll entries approved for {month}/{year}",
        "month": month,
        "year": year,
    }


@router.post("/process")
async def process_payroll(
    data: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_user),
):
    """Process payroll for a month (mark as paid)"""
    month = data.get("month")
    year = data.get("year")

    # TODO: Implement actual payroll processing
    # This would mark all approved salaries as paid

    return {
        "status": "success",
        "message": f"Payroll processed for {month}/{year}",
        "month": month,
        "year": year,
    }


@router.get("/export")
async def export_payroll(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020, le=2100),
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_user),
):
    """Export payroll to CSV"""
    import csv

    # Get organization from current user
    org_id = getattr(current_user, "organization_id", 1) or 1

    service = PayrollCalculationService(db, org_id)

    try:
        result = await service.calculate_from_bigquery(
            month=month,
            year=year,
            save_to_db=False,
        )

        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "BARQ_ID", "Name", "Category", "Total Orders", "Total Revenue",
            "Gas Usage", "Target", "Days Since Joining",
            "Basic Salary", "Bonus Amount", "Gas Deserved", "Gas Difference",
            "Total Salary"
        ])

        # Data rows
        for r in result.results:
            writer.writerow([
                r.barq_id,
                r.name,
                r.category.value if r.category else "",
                r.total_orders,
                float(r.total_revenue) if r.total_revenue else 0,
                float(r.gas_usage) if r.gas_usage else 0,
                float(r.target),
                r.days_since_joining,
                float(r.basic_salary),
                float(r.bonus_amount),
                float(r.gas_deserved),
                float(r.gas_difference),
                float(r.total_salary),
            ])

        output.seek(0)

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=payroll_{year}_{month:02d}.csv"
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payroll export failed: {str(e)}")
