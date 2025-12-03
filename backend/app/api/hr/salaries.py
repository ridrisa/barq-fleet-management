from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from app.crud.hr.salary import salary as crud_salary
from app.schemas.hr.salary import SalaryCreate, SalaryUpdate, SalaryResponse
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.fleet.courier import Courier

router = APIRouter()

@router.get("/", response_model=List[SalaryResponse])
def list_salaries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all salaries"""
    salaries = crud_salary.get_multi(db, skip=skip, limit=limit)
    return salaries

@router.get("/{salary_id}", response_model=SalaryResponse)
def get_salary(
    salary_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific salary by ID"""
    salary = crud_salary.get(db, id=salary_id)
    if not salary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salary not found"
        )
    return salary

@router.post("/", response_model=SalaryResponse, status_code=status.HTTP_201_CREATED)
def create_salary(
    salary_in: SalaryCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new salary"""
    salary = crud_salary.create(db, obj_in=salary_in)
    return salary

@router.put("/{salary_id}", response_model=SalaryResponse)
def update_salary(
    salary_id: int,
    salary_in: SalaryUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a salary"""
    salary = crud_salary.get(db, id=salary_id)
    if not salary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salary not found"
        )
    salary = crud_salary.update(db, db_obj=salary, obj_in=salary_in)
    return salary

@router.delete("/{salary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_salary(
    salary_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a salary"""
    salary = crud_salary.get(db, id=salary_id)
    if not salary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salary not found"
        )
    crud_salary.remove(db, id=salary_id)
    return None


@router.post("/calculate", response_model=Dict[str, Any])
def calculate_salary(
    salary_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate salary based on provided data"""
    courier_id = salary_data.get("courier_id")
    base_salary = salary_data.get("base_salary", 0)
    bonuses = salary_data.get("bonuses", 0)
    deductions = salary_data.get("deductions", 0)

    # Get courier info if courier_id provided
    courier = None
    if courier_id:
        courier = db.query(Courier).filter(Courier.id == courier_id).first()
        if not courier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Courier not found"
            )

    # Calculate total salary
    total_salary = base_salary + bonuses - deductions

    return {
        "courier_id": courier_id,
        "courier_name": courier.full_name if courier else None,
        "base_salary": base_salary,
        "bonuses": bonuses,
        "deductions": deductions,
        "total_salary": total_salary
    }


@router.get("/history/{courier_id}", response_model=List[SalaryResponse])
def get_salary_history(
    courier_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get salary history for a specific courier"""
    # Verify courier exists
    courier = db.query(Courier).filter(Courier.id == courier_id).first()
    if not courier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found"
        )

    # Get all salaries for this courier
    from app.models.hr.salary import Salary
    salaries = db.query(Salary).filter(Salary.courier_id == courier_id).order_by(Salary.created_at.desc()).all()

    return salaries
