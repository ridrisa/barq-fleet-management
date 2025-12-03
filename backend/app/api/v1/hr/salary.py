"""Salary Management API Routes"""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_organization, get_current_user, get_db
from app.models.tenant.organization import Organization
from app.models.user import User
from app.schemas.hr import SalaryCreate, SalaryResponse, SalaryUpdate
from app.services.hr import salary_service

router = APIRouter()


@router.get("/", response_model=List[SalaryResponse])
def get_salaries(
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    courier_id: Optional[int] = None,
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = None,
    is_paid: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Get list of salary records with filtering

    Filters:
    - courier_id: Filter by courier ID
    - month: Filter by month (1-12)
    - year: Filter by year
    - is_paid: Filter by payment status
    """
    # If courier_id filter is provided
    if courier_id:
        return salary_service.get_by_courier(
            db, courier_id=courier_id, skip=skip, limit=limit, organization_id=current_org.id
        )

    # Build dynamic filters
    filters = {"organization_id": current_org.id}
    if month:
        filters["month"] = month
    if year:
        filters["year"] = year
    if is_paid is not None:
        filters["is_paid"] = is_paid

    return salary_service.get_multi(db, skip=skip, limit=limit, filters=filters)


@router.post("/", response_model=SalaryResponse, status_code=status.HTTP_201_CREATED)
def create_salary(
    salary_in: SalaryCreate,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_user),
):
    """Create new salary record"""
    # Check if salary already exists for courier in this month/year
    existing = salary_service.get_by_courier_month_year(
        db,
        courier_id=salary_in.courier_id,
        month=salary_in.month,
        year=salary_in.year,
        organization_id=current_org.id,
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="Salary record already exists for this courier in this month"
        )

    # Add organization_id to the create data
    create_data = salary_in.model_dump() if hasattr(salary_in, "model_dump") else salary_in.dict()
    create_data["organization_id"] = current_org.id
    return salary_service.create(db, obj_in=create_data)


@router.get("/{salary_id}", response_model=SalaryResponse)
def get_salary(
    salary_id: int,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_user),
):
    """Get salary record by ID"""
    salary = salary_service.get(db, id=salary_id)
    if not salary or salary.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Salary record not found")
    return salary


@router.put("/{salary_id}", response_model=SalaryResponse)
def update_salary(
    salary_id: int,
    salary_in: SalaryUpdate,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_user),
):
    """Update salary record"""
    salary = salary_service.get(db, id=salary_id)
    if not salary or salary.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Salary record not found")

    return salary_service.update(db, db_obj=salary, obj_in=salary_in)


@router.delete("/{salary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_salary(
    salary_id: int,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_user),
):
    """Delete salary record"""
    salary = salary_service.get(db, id=salary_id)
    if not salary or salary.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Salary record not found")

    salary_service.delete(db, id=salary_id)
    return None


@router.get("/courier/{courier_id}", response_model=List[SalaryResponse])
def get_courier_salaries(
    courier_id: int,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get all salary records for a specific courier"""
    return salary_service.get_by_courier(
        db, courier_id=courier_id, skip=skip, limit=limit, organization_id=current_org.id
    )


@router.post("/calculate", response_model=SalaryResponse, status_code=status.HTTP_201_CREATED)
def calculate_salary(
    courier_id: int = Body(...),
    month: int = Body(..., ge=1, le=12),
    year: int = Body(...),
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_user),
):
    """
    Calculate and create salary for a courier for a specific month

    Automatically calculates:
    - Base salary
    - Bonuses
    - Deductions (absences, loan payments, etc.)
    - Net salary
    """
    # Check if salary already exists
    existing = salary_service.get_by_courier_month_year(
        db, courier_id=courier_id, month=month, year=year, organization_id=current_org.id
    )
    if existing:
        raise HTTPException(status_code=400, detail="Salary already calculated for this period")

    # Calculate salary using service
    salary = salary_service.calculate_salary(
        db, courier_id=courier_id, month=month, year=year, organization_id=current_org.id
    )

    if not salary:
        raise HTTPException(
            status_code=400,
            detail="Unable to calculate salary. Courier may not exist or have required data.",
        )

    return salary


@router.post("/{salary_id}/mark-paid", response_model=SalaryResponse)
def mark_salary_paid(
    salary_id: int,
    payment_date: Optional[date] = Body(None, embed=True),
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_user),
):
    """
    Mark a salary as paid

    Updates the payment status and records payment date
    """
    salary = salary_service.get(db, id=salary_id)
    if not salary or salary.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Salary record not found")

    if salary.is_paid:
        raise HTTPException(status_code=400, detail="Salary has already been marked as paid")

    updated_salary = salary_service.mark_as_paid(
        db, salary_id=salary_id, payment_date=payment_date or date.today()
    )

    return updated_salary


@router.get("/statistics", response_model=dict)
def get_salary_statistics(
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Get salary statistics

    Returns:
    - total_salaries: Total number of salary records
    - paid_count: Number of paid salaries
    - unpaid_count: Number of unpaid salaries
    - total_gross: Total gross salary amount
    - total_net: Total net salary amount
    - total_deductions: Total deductions
    """
    return salary_service.get_statistics(db, month=month, year=year, organization_id=current_org.id)
