"""End of Service (EOS) Calculator Service

Calculates end of service benefits according to Saudi Arabia labor law.

EOS Calculation Rules (Saudi Labor Law):
- For resignation (employee leaves voluntarily):
  * Less than 2 years: No EOS
  * 2-5 years: One-third of full EOS
  * 5-10 years: Two-thirds of full EOS
  * More than 10 years: Full EOS

- For termination by employer (without cause) or retirement:
  * Full EOS for all service years

- EOS Amount Calculation:
  * First 5 years: Half month salary per year
  * After 5 years: Full month salary per year
"""
from decimal import Decimal
from datetime import date, datetime
from typing import Literal
from enum import Enum
from pydantic import BaseModel, Field


class TerminationType(str, Enum):
    """Type of employment termination"""
    RESIGNATION = "resignation"  # Employee voluntary resignation
    TERMINATION = "termination"  # Employer termination
    RETIREMENT = "retirement"    # Retirement
    END_OF_CONTRACT = "end_of_contract"  # Fixed-term contract end


class EOSCalculationInput(BaseModel):
    """Input schema for EOS calculation"""
    basic_salary: Decimal = Field(..., gt=0, description="Current monthly basic salary")
    hire_date: date = Field(..., description="Date of employment start")
    termination_date: date = Field(..., description="Date of termination")
    termination_type: TerminationType = Field(..., description="Type of termination")


class EOSCalculationResult(BaseModel):
    """Result schema for EOS calculation"""
    basic_salary: Decimal
    hire_date: date
    termination_date: date
    termination_type: str
    years_of_service: Decimal
    months_of_service: int
    days_of_service: int
    eos_full_amount: Decimal
    eos_eligibility_percentage: Decimal
    eos_payable_amount: Decimal
    calculation_breakdown: dict


class EOSCalculatorService:
    """
    Service for calculating End of Service (EOS) benefits
    according to Saudi Arabia labor law requirements.
    """

    def calculate_service_duration(
        self,
        hire_date: date,
        termination_date: date
    ) -> tuple[Decimal, int, int]:
        """
        Calculate the exact service duration

        Args:
            hire_date: Employment start date
            termination_date: Employment end date

        Returns:
            Tuple of (years as Decimal, total months, total days)
        """
        if termination_date < hire_date:
            raise ValueError("Termination date cannot be before hire date")

        # Calculate total days
        delta = termination_date - hire_date
        total_days = delta.days

        # Calculate years, months, days
        years = termination_date.year - hire_date.year
        months = termination_date.month - hire_date.month
        days = termination_date.day - hire_date.day

        # Adjust for negative months or days
        if days < 0:
            months -= 1
            # Get days in previous month
            prev_month = termination_date.month - 1 if termination_date.month > 1 else 12
            prev_year = termination_date.year if termination_date.month > 1 else termination_date.year - 1

            if prev_month in [1, 3, 5, 7, 8, 10, 12]:
                days_in_prev_month = 31
            elif prev_month in [4, 6, 9, 11]:
                days_in_prev_month = 30
            else:  # February
                days_in_prev_month = 29 if prev_year % 4 == 0 and (prev_year % 100 != 0 or prev_year % 400 == 0) else 28

            days += days_in_prev_month

        if months < 0:
            years -= 1
            months += 12

        total_months = years * 12 + months

        # Calculate years as decimal (for precise calculation)
        years_decimal = Decimal(str(total_days / 365.25))

        return years_decimal, total_months, total_days

    def calculate_full_eos(
        self,
        basic_salary: Decimal,
        years_of_service: Decimal
    ) -> tuple[Decimal, dict]:
        """
        Calculate full EOS amount before applying eligibility percentage

        Formula:
        - First 5 years: 0.5 month salary per year
        - After 5 years: 1 month salary per year

        Args:
            basic_salary: Monthly basic salary
            years_of_service: Total years of service

        Returns:
            Tuple of (total EOS amount, breakdown dictionary)
        """
        breakdown = {}
        total_eos = Decimal("0")

        if years_of_service <= 5:
            # All years at half month salary
            amount = basic_salary * Decimal("0.5") * years_of_service
            total_eos = amount
            breakdown["first_5_years"] = {
                "years": float(years_of_service),
                "rate": 0.5,
                "amount": float(amount)
            }
        else:
            # First 5 years at half month
            first_5_amount = basic_salary * Decimal("0.5") * Decimal("5")
            breakdown["first_5_years"] = {
                "years": 5,
                "rate": 0.5,
                "amount": float(first_5_amount)
            }

            # Remaining years at full month
            remaining_years = years_of_service - Decimal("5")
            remaining_amount = basic_salary * Decimal("1") * remaining_years
            breakdown["after_5_years"] = {
                "years": float(remaining_years),
                "rate": 1.0,
                "amount": float(remaining_amount)
            }

            total_eos = first_5_amount + remaining_amount

        breakdown["total"] = float(total_eos)

        return total_eos.quantize(Decimal("0.01")), breakdown

    def calculate_eligibility_percentage(
        self,
        years_of_service: Decimal,
        termination_type: TerminationType
    ) -> Decimal:
        """
        Calculate EOS eligibility percentage based on termination type and service duration

        Args:
            years_of_service: Total years of service
            termination_type: Type of termination

        Returns:
            Eligibility percentage (0.0 to 1.0)
        """
        # Full EOS for termination by employer or retirement
        if termination_type in [TerminationType.TERMINATION, TerminationType.RETIREMENT, TerminationType.END_OF_CONTRACT]:
            return Decimal("1.0")  # 100%

        # For resignation (employee voluntary leave)
        if termination_type == TerminationType.RESIGNATION:
            if years_of_service < 2:
                return Decimal("0")  # 0% - no EOS
            elif years_of_service < 5:
                return Decimal("0.333333")  # 33.33% - one-third
            elif years_of_service < 10:
                return Decimal("0.666667")  # 66.67% - two-thirds
            else:
                return Decimal("1.0")  # 100% - full EOS

        return Decimal("1.0")  # Default to full EOS

    def calculate(
        self,
        basic_salary: Decimal,
        hire_date: date,
        termination_date: date,
        termination_type: TerminationType
    ) -> EOSCalculationResult:
        """
        Calculate complete EOS benefit

        Args:
            basic_salary: Current monthly basic salary
            hire_date: Date of employment start
            termination_date: Date of termination
            termination_type: Type of termination

        Returns:
            EOSCalculationResult with complete calculation details

        Example:
            >>> service = EOSCalculatorService()
            >>> result = service.calculate(
            ...     basic_salary=Decimal("5000"),
            ...     hire_date=date(2015, 1, 1),
            ...     termination_date=date(2023, 6, 30),
            ...     termination_type=TerminationType.RESIGNATION
            ... )
            >>> print(result.eos_payable_amount)
        """
        # Calculate service duration
        years_decimal, total_months, total_days = self.calculate_service_duration(
            hire_date, termination_date
        )

        # Calculate full EOS amount
        full_eos_amount, calculation_breakdown = self.calculate_full_eos(
            basic_salary, years_decimal
        )

        # Calculate eligibility percentage
        eligibility_percentage = self.calculate_eligibility_percentage(
            years_decimal, termination_type
        )

        # Calculate payable amount
        payable_amount = (full_eos_amount * eligibility_percentage).quantize(
            Decimal("0.01")
        )

        # Add eligibility info to breakdown
        calculation_breakdown["eligibility"] = {
            "termination_type": termination_type.value,
            "years_of_service": float(years_decimal),
            "eligibility_percentage": float(eligibility_percentage),
            "full_eos_amount": float(full_eos_amount),
            "payable_amount": float(payable_amount)
        }

        return EOSCalculationResult(
            basic_salary=basic_salary,
            hire_date=hire_date,
            termination_date=termination_date,
            termination_type=termination_type.value,
            years_of_service=years_decimal,
            months_of_service=total_months,
            days_of_service=total_days,
            eos_full_amount=full_eos_amount,
            eos_eligibility_percentage=eligibility_percentage,
            eos_payable_amount=payable_amount,
            calculation_breakdown=calculation_breakdown
        )

    def get_eos_summary(
        self,
        basic_salary: Decimal,
        hire_date: date,
        termination_date: date
    ) -> dict:
        """
        Get EOS summary for all termination types

        Useful for showing employee what they would get under different scenarios

        Args:
            basic_salary: Current monthly basic salary
            hire_date: Date of employment start
            termination_date: Projected termination date

        Returns:
            Dictionary with EOS amounts for each termination type
        """
        summary = {}

        for term_type in TerminationType:
            result = self.calculate(
                basic_salary=basic_salary,
                hire_date=hire_date,
                termination_date=termination_date,
                termination_type=term_type
            )

            summary[term_type.value] = {
                "eligibility_percentage": float(result.eos_eligibility_percentage),
                "eos_amount": float(result.eos_payable_amount)
            }

        return {
            "basic_salary": float(basic_salary),
            "years_of_service": float(result.years_of_service),
            "full_eos_amount": float(result.eos_full_amount),
            "scenarios": summary
        }


# Singleton instance
eos_calculator_service = EOSCalculatorService()
