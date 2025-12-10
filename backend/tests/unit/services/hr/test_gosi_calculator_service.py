"""
Unit Tests for GOSI Calculator Service

Tests GOSI (General Organization for Social Insurance) calculations:
- Monthly contribution calculations
- Annual contribution calculations
- Contribution validation
"""

import pytest
from decimal import Decimal

from app.services.hr.gosi_calculator_service import (
    GOSICalculatorService,
    GOSICalculationResult,
    gosi_calculator_service,
)


# ==================== Fixtures ====================

@pytest.fixture
def service():
    """Create GOSICalculatorService instance"""
    return GOSICalculatorService()


# ==================== Rate Constants Tests ====================

class TestRateConstants:
    """Tests for GOSI rate constants"""

    def test_employee_rate(self, service):
        """Employee rate should be 9%"""
        assert service.EMPLOYEE_RATE == Decimal("0.09")

    def test_employer_rate(self, service):
        """Employer rate should be 12%"""
        assert service.EMPLOYER_RATE == Decimal("0.12")


# ==================== Monthly Calculation Tests ====================

class TestMonthlyCalculation:
    """Tests for calculate method"""

    def test_basic_calculation(self, service):
        """Should calculate GOSI contributions correctly"""
        result = service.calculate(Decimal("5000"))

        # Employee: 5000 * 0.09 = 450
        assert result.employee_contribution == Decimal("450.00")
        # Employer: 5000 * 0.12 = 600
        assert result.employer_contribution == Decimal("600.00")
        # Total: 450 + 600 = 1050
        assert result.total_contribution == Decimal("1050.00")

    def test_small_salary(self, service):
        """Should handle small salary correctly"""
        result = service.calculate(Decimal("1000"))

        assert result.employee_contribution == Decimal("90.00")
        assert result.employer_contribution == Decimal("120.00")
        assert result.total_contribution == Decimal("210.00")

    def test_large_salary(self, service):
        """Should handle large salary correctly"""
        result = service.calculate(Decimal("50000"))

        assert result.employee_contribution == Decimal("4500.00")
        assert result.employer_contribution == Decimal("6000.00")
        assert result.total_contribution == Decimal("10500.00")

    def test_decimal_salary(self, service):
        """Should handle decimal salary values"""
        result = service.calculate(Decimal("5555.55"))

        # 5555.55 * 0.09 = 500.00 (rounded)
        expected_employee = (Decimal("5555.55") * Decimal("0.09")).quantize(Decimal("0.01"))
        assert result.employee_contribution == expected_employee

    def test_zero_salary_raises_error(self, service):
        """Should raise error for zero salary"""
        with pytest.raises(ValueError, match="Basic salary must be greater than zero"):
            service.calculate(Decimal("0"))

    def test_negative_salary_raises_error(self, service):
        """Should raise error for negative salary"""
        with pytest.raises(ValueError, match="Basic salary must be greater than zero"):
            service.calculate(Decimal("-5000"))

    def test_result_type(self, service):
        """Should return GOSICalculationResult"""
        result = service.calculate(Decimal("5000"))
        assert isinstance(result, GOSICalculationResult)

    def test_result_contains_rates(self, service):
        """Result should contain the rates used"""
        result = service.calculate(Decimal("5000"))

        assert result.employee_rate == Decimal("0.09")
        assert result.employer_rate == Decimal("0.12")

    def test_result_contains_basic_salary(self, service):
        """Result should contain the input salary"""
        result = service.calculate(Decimal("5000"))
        assert result.basic_salary == Decimal("5000")


# ==================== Annual Calculation Tests ====================

class TestAnnualCalculation:
    """Tests for calculate_annual method"""

    def test_annual_calculation_12_months(self, service):
        """Should calculate annual contributions for 12 months"""
        result = service.calculate_annual(Decimal("5000"))

        assert result["months"] == 12
        assert result["monthly_basic_salary"] == 5000.0
        assert result["annual_basic_salary"] == 60000.0
        assert result["monthly_employee_contribution"] == 450.0
        assert result["monthly_employer_contribution"] == 600.0
        assert result["annual_employee_contribution"] == 5400.0
        assert result["annual_employer_contribution"] == 7200.0
        assert result["annual_total_contribution"] == 12600.0

    def test_annual_calculation_partial_year(self, service):
        """Should calculate for partial year"""
        result = service.calculate_annual(Decimal("5000"), months=6)

        assert result["months"] == 6
        assert result["annual_basic_salary"] == 30000.0
        assert result["annual_employee_contribution"] == 2700.0
        assert result["annual_employer_contribution"] == 3600.0

    def test_annual_calculation_single_month(self, service):
        """Should handle single month"""
        result = service.calculate_annual(Decimal("5000"), months=1)

        assert result["months"] == 1
        assert result["annual_employee_contribution"] == 450.0
        assert result["annual_employer_contribution"] == 600.0


# ==================== Validation Tests ====================

class TestValidateContribution:
    """Tests for validate_contribution method"""

    def test_valid_contributions(self, service):
        """Should validate correct contributions"""
        result = service.validate_contribution(
            basic_salary=Decimal("5000"),
            employee_contribution=Decimal("450.00"),
            employer_contribution=Decimal("600.00"),
        )

        assert result["is_valid"] is True
        assert result["employee_contribution_valid"] is True
        assert result["employer_contribution_valid"] is True

    def test_invalid_employee_contribution(self, service):
        """Should detect incorrect employee contribution"""
        result = service.validate_contribution(
            basic_salary=Decimal("5000"),
            employee_contribution=Decimal("400.00"),  # Wrong
            employer_contribution=Decimal("600.00"),
        )

        assert result["is_valid"] is False
        assert result["employee_contribution_valid"] is False
        assert result["employer_contribution_valid"] is True
        assert result["employee_difference"] == 50.0

    def test_invalid_employer_contribution(self, service):
        """Should detect incorrect employer contribution"""
        result = service.validate_contribution(
            basic_salary=Decimal("5000"),
            employee_contribution=Decimal("450.00"),
            employer_contribution=Decimal("500.00"),  # Wrong
        )

        assert result["is_valid"] is False
        assert result["employee_contribution_valid"] is True
        assert result["employer_contribution_valid"] is False
        assert result["employer_difference"] == 100.0

    def test_both_invalid(self, service):
        """Should detect both contributions incorrect"""
        result = service.validate_contribution(
            basic_salary=Decimal("5000"),
            employee_contribution=Decimal("400.00"),
            employer_contribution=Decimal("500.00"),
        )

        assert result["is_valid"] is False
        assert result["employee_contribution_valid"] is False
        assert result["employer_contribution_valid"] is False

    def test_validation_result_structure(self, service):
        """Should return complete validation structure"""
        result = service.validate_contribution(
            basic_salary=Decimal("5000"),
            employee_contribution=Decimal("450.00"),
            employer_contribution=Decimal("600.00"),
        )

        assert "is_valid" in result
        assert "employee_contribution_valid" in result
        assert "employer_contribution_valid" in result
        assert "expected_employee_contribution" in result
        assert "expected_employer_contribution" in result
        assert "provided_employee_contribution" in result
        assert "provided_employer_contribution" in result
        assert "employee_difference" in result
        assert "employer_difference" in result


# ==================== Edge Cases ====================

class TestEdgeCases:
    """Tests for edge cases"""

    def test_very_small_salary(self, service):
        """Should handle very small salary"""
        result = service.calculate(Decimal("100"))

        assert result.employee_contribution == Decimal("9.00")
        assert result.employer_contribution == Decimal("12.00")

    def test_very_large_salary(self, service):
        """Should handle very large salary"""
        result = service.calculate(Decimal("1000000"))

        assert result.employee_contribution == Decimal("90000.00")
        assert result.employer_contribution == Decimal("120000.00")

    def test_precision_with_decimals(self, service):
        """Should maintain precision with decimal salaries"""
        result = service.calculate(Decimal("3333.33"))

        # Verify proper rounding
        assert str(result.employee_contribution).split('.')[-1].__len__() <= 2
        assert str(result.employer_contribution).split('.')[-1].__len__() <= 2

    def test_rounding_consistency(self, service):
        """Rounding should be consistent"""
        result1 = service.calculate(Decimal("1111.11"))
        result2 = service.calculate(Decimal("1111.11"))

        assert result1.employee_contribution == result2.employee_contribution
        assert result1.employer_contribution == result2.employer_contribution


# ==================== Integration Tests ====================

class TestIntegration:
    """Integration tests for the service"""

    def test_calculate_then_validate(self, service):
        """Should be able to calculate and validate"""
        calc_result = service.calculate(Decimal("5000"))
        validation = service.validate_contribution(
            basic_salary=Decimal("5000"),
            employee_contribution=calc_result.employee_contribution,
            employer_contribution=calc_result.employer_contribution,
        )

        assert validation["is_valid"] is True

    def test_annual_matches_monthly_times_12(self, service):
        """Annual calculation should equal monthly * 12"""
        salary = Decimal("5000")
        monthly = service.calculate(salary)
        annual = service.calculate_annual(salary)

        assert annual["annual_employee_contribution"] == float(monthly.employee_contribution * 12)
        assert annual["annual_employer_contribution"] == float(monthly.employer_contribution * 12)


# ==================== Singleton Tests ====================

class TestSingleton:
    """Tests for singleton instance"""

    def test_singleton_exists(self):
        """Should have a singleton instance"""
        assert gosi_calculator_service is not None

    def test_singleton_is_instance(self):
        """Should be a GOSICalculatorService instance"""
        assert isinstance(gosi_calculator_service, GOSICalculatorService)

    def test_singleton_calculation(self):
        """Singleton should work correctly"""
        result = gosi_calculator_service.calculate(Decimal("5000"))
        assert result.employee_contribution == Decimal("450.00")
