"""GOSI Calculator Service

General Organization for Social Insurance (GOSI) calculator for Saudi Arabia.
Calculates employee and employer contributions based on Saudi labor law.

GOSI Contribution Rates:
- Employee: 9% of basic salary
- Employer: 12% of basic salary
"""

from decimal import Decimal
from typing import Dict

from pydantic import BaseModel, Field


class GOSICalculationInput(BaseModel):
    """Input schema for GOSI calculation"""

    basic_salary: Decimal = Field(..., gt=0, description="Basic monthly salary")


class GOSICalculationResult(BaseModel):
    """Result schema for GOSI calculation"""

    basic_salary: Decimal
    employee_contribution: Decimal
    employer_contribution: Decimal
    total_contribution: Decimal
    employee_rate: Decimal
    employer_rate: Decimal


class GOSICalculatorService:
    """
    Service for calculating GOSI (General Organization for Social Insurance) contributions
    according to Saudi Arabia labor law requirements.
    """

    # GOSI rates as per Saudi labor law
    EMPLOYEE_RATE = Decimal("0.09")  # 9%
    EMPLOYER_RATE = Decimal("0.12")  # 12%

    def calculate(self, basic_salary: Decimal) -> GOSICalculationResult:
        """
        Calculate GOSI contributions for employee and employer

        Args:
            basic_salary: The basic monthly salary amount

        Returns:
            GOSICalculationResult with breakdown of contributions

        Example:
            >>> service = GOSICalculatorService()
            >>> result = service.calculate(Decimal("5000"))
            >>> print(result.employee_contribution)  # 450.00
            >>> print(result.employer_contribution)  # 600.00
            >>> print(result.total_contribution)     # 1050.00
        """
        if basic_salary <= 0:
            raise ValueError("Basic salary must be greater than zero")

        # Calculate employee contribution (9%)
        employee_contribution = (basic_salary * self.EMPLOYEE_RATE).quantize(Decimal("0.01"))

        # Calculate employer contribution (12%)
        employer_contribution = (basic_salary * self.EMPLOYER_RATE).quantize(Decimal("0.01"))

        # Calculate total contribution
        total_contribution = employee_contribution + employer_contribution

        return GOSICalculationResult(
            basic_salary=basic_salary,
            employee_contribution=employee_contribution,
            employer_contribution=employer_contribution,
            total_contribution=total_contribution,
            employee_rate=self.EMPLOYEE_RATE,
            employer_rate=self.EMPLOYER_RATE,
        )

    def calculate_annual(self, basic_salary: Decimal, months: int = 12) -> Dict:
        """
        Calculate annual GOSI contributions

        Args:
            basic_salary: The basic monthly salary amount
            months: Number of months (default 12)

        Returns:
            Dictionary with annual contribution breakdown
        """
        monthly_result = self.calculate(basic_salary)

        return {
            "months": months,
            "monthly_basic_salary": float(basic_salary),
            "annual_basic_salary": float(basic_salary * months),
            "monthly_employee_contribution": float(monthly_result.employee_contribution),
            "monthly_employer_contribution": float(monthly_result.employer_contribution),
            "monthly_total_contribution": float(monthly_result.total_contribution),
            "annual_employee_contribution": float(monthly_result.employee_contribution * months),
            "annual_employer_contribution": float(monthly_result.employer_contribution * months),
            "annual_total_contribution": float(monthly_result.total_contribution * months),
        }

    def validate_contribution(
        self, basic_salary: Decimal, employee_contribution: Decimal, employer_contribution: Decimal
    ) -> Dict:
        """
        Validate if provided contributions match the calculated amounts

        Args:
            basic_salary: The basic monthly salary
            employee_contribution: Claimed employee contribution
            employer_contribution: Claimed employer contribution

        Returns:
            Dictionary with validation results
        """
        calculated = self.calculate(basic_salary)

        employee_match = employee_contribution == calculated.employee_contribution
        employer_match = employer_contribution == calculated.employer_contribution

        return {
            "is_valid": employee_match and employer_match,
            "employee_contribution_valid": employee_match,
            "employer_contribution_valid": employer_match,
            "expected_employee_contribution": float(calculated.employee_contribution),
            "expected_employer_contribution": float(calculated.employer_contribution),
            "provided_employee_contribution": float(employee_contribution),
            "provided_employer_contribution": float(employer_contribution),
            "employee_difference": float(calculated.employee_contribution - employee_contribution),
            "employer_difference": float(calculated.employer_contribution - employer_contribution),
        }


# Singleton instance
gosi_calculator_service = GOSICalculatorService()
