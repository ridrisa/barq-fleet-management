"""
Unit Tests for EOS Calculator Service

Tests End of Service (EOS) benefit calculations:
- Service duration calculation
- Full EOS amount calculation
- Eligibility percentage calculation
- Complete EOS calculation
- EOS summary for all scenarios
"""

import pytest
from datetime import date
from decimal import Decimal

from app.services.hr.eos_calculator_service import (
    EOSCalculatorService,
    EOSCalculationResult,
    TerminationType,
    eos_calculator_service,
)


# ==================== Fixtures ====================

@pytest.fixture
def service():
    """Create EOSCalculatorService instance"""
    return EOSCalculatorService()


# ==================== Service Duration Tests ====================

class TestCalculateServiceDuration:
    """Tests for calculate_service_duration method"""

    def test_exact_years(self, service):
        """Should calculate exact years correctly"""
        hire_date = date(2020, 1, 1)
        termination_date = date(2025, 1, 1)

        years, months, days = service.calculate_service_duration(hire_date, termination_date)

        assert years >= Decimal("4.99")
        assert months == 60

    def test_partial_years(self, service):
        """Should calculate partial years correctly"""
        hire_date = date(2020, 1, 1)
        termination_date = date(2023, 7, 1)

        years, months, days = service.calculate_service_duration(hire_date, termination_date)

        assert years >= Decimal("3.4")
        assert months == 42

    def test_same_date_zero_duration(self, service):
        """Should return zero for same hire and termination date"""
        same_date = date(2025, 1, 15)

        years, months, days = service.calculate_service_duration(same_date, same_date)

        assert years == Decimal("0")
        assert months == 0
        assert days == 0

    def test_termination_before_hire_raises_error(self, service):
        """Should raise error if termination before hire"""
        hire_date = date(2025, 1, 1)
        termination_date = date(2024, 1, 1)

        with pytest.raises(ValueError, match="Termination date cannot be before hire date"):
            service.calculate_service_duration(hire_date, termination_date)

    def test_leap_year_handling(self, service):
        """Should handle leap years correctly"""
        hire_date = date(2020, 2, 29)  # Leap year
        termination_date = date(2024, 2, 29)  # Another leap year

        years, months, days = service.calculate_service_duration(hire_date, termination_date)

        assert years >= Decimal("3.99")

    def test_short_service(self, service):
        """Should calculate short service period"""
        hire_date = date(2025, 1, 1)
        termination_date = date(2025, 3, 15)

        years, months, days = service.calculate_service_duration(hire_date, termination_date)

        assert years < Decimal("1")
        assert months == 2


# ==================== Full EOS Calculation Tests ====================

class TestCalculateFullEOS:
    """Tests for calculate_full_eos method"""

    def test_under_5_years(self, service):
        """Should calculate EOS for under 5 years at half month rate"""
        basic_salary = Decimal("5000")
        years_of_service = Decimal("3")

        eos_amount, breakdown = service.calculate_full_eos(basic_salary, years_of_service)

        # 3 years * 0.5 * 5000 = 7500
        expected = Decimal("5000") * Decimal("0.5") * Decimal("3")
        assert eos_amount == expected.quantize(Decimal("0.01"))
        assert "first_5_years" in breakdown

    def test_exactly_5_years(self, service):
        """Should calculate EOS for exactly 5 years"""
        basic_salary = Decimal("5000")
        years_of_service = Decimal("5")

        eos_amount, breakdown = service.calculate_full_eos(basic_salary, years_of_service)

        # 5 years * 0.5 * 5000 = 12500
        expected = Decimal("5000") * Decimal("0.5") * Decimal("5")
        assert eos_amount == expected.quantize(Decimal("0.01"))

    def test_over_5_years(self, service):
        """Should calculate EOS for over 5 years with two rates"""
        basic_salary = Decimal("5000")
        years_of_service = Decimal("8")

        eos_amount, breakdown = service.calculate_full_eos(basic_salary, years_of_service)

        # First 5 years: 5 * 0.5 * 5000 = 12500
        # Remaining 3 years: 3 * 1.0 * 5000 = 15000
        # Total: 27500
        first_5 = Decimal("5") * Decimal("0.5") * Decimal("5000")
        remaining = Decimal("3") * Decimal("1.0") * Decimal("5000")
        expected = first_5 + remaining

        assert eos_amount == expected.quantize(Decimal("0.01"))
        assert "first_5_years" in breakdown
        assert "after_5_years" in breakdown

    def test_10_years_service(self, service):
        """Should calculate EOS for 10 years"""
        basic_salary = Decimal("5000")
        years_of_service = Decimal("10")

        eos_amount, breakdown = service.calculate_full_eos(basic_salary, years_of_service)

        # First 5 years: 5 * 0.5 * 5000 = 12500
        # Remaining 5 years: 5 * 1.0 * 5000 = 25000
        # Total: 37500
        expected = Decimal("12500") + Decimal("25000")
        assert eos_amount == expected.quantize(Decimal("0.01"))

    def test_breakdown_structure(self, service):
        """Should return proper breakdown structure"""
        basic_salary = Decimal("5000")
        years_of_service = Decimal("7")

        eos_amount, breakdown = service.calculate_full_eos(basic_salary, years_of_service)

        assert "first_5_years" in breakdown
        assert "after_5_years" in breakdown
        assert "total" in breakdown
        assert breakdown["first_5_years"]["rate"] == 0.5
        assert breakdown["after_5_years"]["rate"] == 1.0


# ==================== Eligibility Percentage Tests ====================

class TestCalculateEligibilityPercentage:
    """Tests for calculate_eligibility_percentage method"""

    def test_termination_full_eligibility(self, service):
        """Termination by employer should get 100%"""
        for years in [Decimal("1"), Decimal("3"), Decimal("8"), Decimal("12")]:
            percentage = service.calculate_eligibility_percentage(
                years, TerminationType.TERMINATION
            )
            assert percentage == Decimal("1.0")

    def test_retirement_full_eligibility(self, service):
        """Retirement should get 100%"""
        percentage = service.calculate_eligibility_percentage(
            Decimal("20"), TerminationType.RETIREMENT
        )
        assert percentage == Decimal("1.0")

    def test_end_of_contract_full_eligibility(self, service):
        """End of contract should get 100%"""
        percentage = service.calculate_eligibility_percentage(
            Decimal("2"), TerminationType.END_OF_CONTRACT
        )
        assert percentage == Decimal("1.0")

    def test_resignation_under_2_years(self, service):
        """Resignation under 2 years should get 0%"""
        percentage = service.calculate_eligibility_percentage(
            Decimal("1.5"), TerminationType.RESIGNATION
        )
        assert percentage == Decimal("0")

    def test_resignation_2_to_5_years(self, service):
        """Resignation 2-5 years should get ~33%"""
        percentage = service.calculate_eligibility_percentage(
            Decimal("3"), TerminationType.RESIGNATION
        )
        assert percentage == Decimal("0.333333")

    def test_resignation_5_to_10_years(self, service):
        """Resignation 5-10 years should get ~67%"""
        percentage = service.calculate_eligibility_percentage(
            Decimal("7"), TerminationType.RESIGNATION
        )
        assert percentage == Decimal("0.666667")

    def test_resignation_over_10_years(self, service):
        """Resignation over 10 years should get 100%"""
        percentage = service.calculate_eligibility_percentage(
            Decimal("12"), TerminationType.RESIGNATION
        )
        assert percentage == Decimal("1.0")

    def test_resignation_exactly_2_years(self, service):
        """Resignation at exactly 2 years should get 33%"""
        percentage = service.calculate_eligibility_percentage(
            Decimal("2"), TerminationType.RESIGNATION
        )
        assert percentage == Decimal("0.333333")

    def test_resignation_exactly_5_years(self, service):
        """Resignation at exactly 5 years should get 67%"""
        percentage = service.calculate_eligibility_percentage(
            Decimal("5"), TerminationType.RESIGNATION
        )
        assert percentage == Decimal("0.666667")

    def test_resignation_exactly_10_years(self, service):
        """Resignation at exactly 10 years should get 100%"""
        percentage = service.calculate_eligibility_percentage(
            Decimal("10"), TerminationType.RESIGNATION
        )
        assert percentage == Decimal("1.0")


# ==================== Complete Calculation Tests ====================

class TestCalculateComplete:
    """Tests for complete calculate method"""

    def test_complete_calculation_resignation_short(self, service):
        """Should calculate complete EOS for short resignation"""
        result = service.calculate(
            basic_salary=Decimal("5000"),
            hire_date=date(2024, 1, 1),
            termination_date=date(2025, 1, 1),
            termination_type=TerminationType.RESIGNATION,
        )

        assert isinstance(result, EOSCalculationResult)
        assert result.basic_salary == Decimal("5000")
        assert result.termination_type == "resignation"
        assert result.eos_eligibility_percentage == Decimal("0")  # Under 2 years
        assert result.eos_payable_amount == Decimal("0.00")

    def test_complete_calculation_termination(self, service):
        """Should calculate complete EOS for termination"""
        result = service.calculate(
            basic_salary=Decimal("5000"),
            hire_date=date(2020, 1, 1),
            termination_date=date(2025, 1, 1),
            termination_type=TerminationType.TERMINATION,
        )

        assert result.eos_eligibility_percentage == Decimal("1.0")
        assert result.eos_payable_amount == result.eos_full_amount

    def test_calculation_result_structure(self, service):
        """Should return proper result structure"""
        result = service.calculate(
            basic_salary=Decimal("5000"),
            hire_date=date(2015, 1, 1),
            termination_date=date(2025, 1, 1),
            termination_type=TerminationType.RESIGNATION,
        )

        assert hasattr(result, 'basic_salary')
        assert hasattr(result, 'hire_date')
        assert hasattr(result, 'termination_date')
        assert hasattr(result, 'termination_type')
        assert hasattr(result, 'years_of_service')
        assert hasattr(result, 'months_of_service')
        assert hasattr(result, 'days_of_service')
        assert hasattr(result, 'eos_full_amount')
        assert hasattr(result, 'eos_eligibility_percentage')
        assert hasattr(result, 'eos_payable_amount')
        assert hasattr(result, 'calculation_breakdown')

    def test_calculation_breakdown_contains_eligibility(self, service):
        """Breakdown should contain eligibility info"""
        result = service.calculate(
            basic_salary=Decimal("5000"),
            hire_date=date(2020, 1, 1),
            termination_date=date(2025, 1, 1),
            termination_type=TerminationType.RESIGNATION,
        )

        assert "eligibility" in result.calculation_breakdown
        assert "termination_type" in result.calculation_breakdown["eligibility"]


# ==================== EOS Summary Tests ====================

class TestGetEOSSummary:
    """Tests for get_eos_summary method"""

    def test_summary_all_scenarios(self, service):
        """Should return summary for all termination types"""
        summary = service.get_eos_summary(
            basic_salary=Decimal("5000"),
            hire_date=date(2020, 1, 1),
            termination_date=date(2025, 1, 1),
        )

        assert "basic_salary" in summary
        assert "years_of_service" in summary
        assert "full_eos_amount" in summary
        assert "scenarios" in summary

    def test_summary_contains_all_termination_types(self, service):
        """Summary should contain all termination types"""
        summary = service.get_eos_summary(
            basic_salary=Decimal("5000"),
            hire_date=date(2020, 1, 1),
            termination_date=date(2025, 1, 1),
        )

        scenarios = summary["scenarios"]
        assert "resignation" in scenarios
        assert "termination" in scenarios
        assert "retirement" in scenarios
        assert "end_of_contract" in scenarios

    def test_summary_scenario_structure(self, service):
        """Each scenario should have eligibility and amount"""
        summary = service.get_eos_summary(
            basic_salary=Decimal("5000"),
            hire_date=date(2020, 1, 1),
            termination_date=date(2025, 1, 1),
        )

        for scenario_type, scenario_data in summary["scenarios"].items():
            assert "eligibility_percentage" in scenario_data
            assert "eos_amount" in scenario_data


# ==================== Edge Cases ====================

class TestEdgeCases:
    """Tests for edge cases"""

    def test_very_long_service(self, service):
        """Should handle very long service period"""
        result = service.calculate(
            basic_salary=Decimal("5000"),
            hire_date=date(1990, 1, 1),
            termination_date=date(2025, 1, 1),
            termination_type=TerminationType.RETIREMENT,
        )

        assert result.years_of_service > Decimal("30")
        assert result.eos_payable_amount > Decimal("100000")

    def test_small_salary(self, service):
        """Should handle small salary amounts"""
        result = service.calculate(
            basic_salary=Decimal("1000"),
            hire_date=date(2020, 1, 1),
            termination_date=date(2025, 1, 1),
            termination_type=TerminationType.TERMINATION,
        )

        assert result.eos_payable_amount > Decimal("0")

    def test_large_salary(self, service):
        """Should handle large salary amounts"""
        result = service.calculate(
            basic_salary=Decimal("50000"),
            hire_date=date(2015, 1, 1),
            termination_date=date(2025, 1, 1),
            termination_type=TerminationType.TERMINATION,
        )

        assert result.eos_payable_amount > Decimal("0")

    def test_decimal_precision(self, service):
        """Should maintain decimal precision"""
        result = service.calculate(
            basic_salary=Decimal("5000.50"),
            hire_date=date(2020, 1, 1),
            termination_date=date(2025, 1, 1),
            termination_type=TerminationType.TERMINATION,
        )

        # Check that result is properly quantized
        assert str(result.eos_payable_amount).split('.')[-1].__len__() <= 2


# ==================== Singleton Tests ====================

class TestSingleton:
    """Tests for singleton instance"""

    def test_singleton_exists(self):
        """Should have a singleton instance"""
        assert eos_calculator_service is not None

    def test_singleton_is_instance(self):
        """Should be an EOSCalculatorService instance"""
        assert isinstance(eos_calculator_service, EOSCalculatorService)
