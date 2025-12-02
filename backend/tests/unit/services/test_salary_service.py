"""
Unit Tests for Salary Service

Tests cover:
- Salary calculation logic
- GOSI calculations
- Deductions and bonuses
- Tax calculations
- Business rules

Author: BARQ QA Team
Last Updated: 2025-12-02
"""

import pytest
from decimal import Decimal
from datetime import datetime, date
from unittest.mock import Mock, patch

from app.services.hr.salary_service import SalaryService
from app.services.hr.gosi_calculator_service import GOSICalculatorService
from app.models.hr.salary import Salary
from app.models.fleet.courier import Courier, CourierStatus


class TestSalaryService:
    """Test Salary calculation service"""

    def test_calculate_gross_salary_basic(self, db_session):
        """Test basic gross salary calculation"""
        service = SalaryService(db_session)

        # Base salary only
        gross = service._calculate_gross_salary(
            base_salary=3000.00,
            allowances=0.00,
            bonuses=0.00
        )

        assert gross == 3000.00

    def test_calculate_gross_salary_with_allowances(self, db_session):
        """Test gross salary with allowances"""
        service = SalaryService(db_session)

        gross = service._calculate_gross_salary(
            base_salary=3000.00,
            allowances=500.00,  # Housing allowance
            bonuses=0.00
        )

        assert gross == 3500.00

    def test_calculate_gross_salary_with_bonuses(self, db_session):
        """Test gross salary with bonuses"""
        service = SalaryService(db_session)

        gross = service._calculate_gross_salary(
            base_salary=3000.00,
            allowances=500.00,
            bonuses=300.00  # Performance bonus
        )

        assert gross == 3800.00

    def test_calculate_gosi_deduction(self, db_session):
        """Test GOSI deduction calculation"""
        service = SalaryService(db_session)

        # Saudi national: 10% employee contribution
        gosi_saudi = service._calculate_gosi(
            base_salary=3000.00,
            is_saudi=True
        )
        assert gosi_saudi == 300.00  # 10% of 3000

        # Non-Saudi: 2% employee contribution
        gosi_non_saudi = service._calculate_gosi(
            base_salary=3000.00,
            is_saudi=False
        )
        assert gosi_non_saudi == 60.00  # 2% of 3000

    def test_calculate_loan_deduction(self, db_session, courier_factory):
        """Test loan installment deduction"""
        service = SalaryService(db_session)
        courier = courier_factory()

        # Create loan with installment
        from app.models.hr.loan import Loan, LoanStatus
        loan = Loan(
            courier_id=courier.id,
            amount=5000.00,
            installment_amount=500.00,
            remaining_amount=3000.00,
            status=LoanStatus.APPROVED
        )
        db_session.add(loan)
        db_session.commit()

        # Calculate deduction
        loan_deduction = service._calculate_loan_deduction(courier.id)
        assert loan_deduction == 500.00

    def test_calculate_total_deductions(self, db_session):
        """Test total deductions calculation"""
        service = SalaryService(db_session)

        deductions = service._calculate_total_deductions(
            gosi=300.00,
            loan=500.00,
            penalties=100.00,
            other=50.00
        )

        assert deductions == 950.00

    def test_calculate_net_salary(self, db_session):
        """Test net salary calculation"""
        service = SalaryService(db_session)

        net = service._calculate_net_salary(
            gross_salary=5000.00,
            total_deductions=1200.00
        )

        assert net == 3800.00

    def test_calculate_net_salary_minimum_threshold(self, db_session):
        """Test net salary doesn't go below minimum"""
        service = SalaryService(db_session)

        # If deductions exceed gross, net should be 0
        net = service._calculate_net_salary(
            gross_salary=3000.00,
            total_deductions=3500.00
        )

        assert net == 0.00

    @patch('app.services.hr.salary_service.SalaryService._get_courier_bonuses')
    @patch('app.services.hr.salary_service.SalaryService._get_courier_penalties')
    def test_calculate_monthly_salary_complete(
        self,
        mock_penalties,
        mock_bonuses,
        db_session,
        courier_factory
    ):
        """Test complete monthly salary calculation"""
        mock_bonuses.return_value = 500.00
        mock_penalties.return_value = 200.00

        service = SalaryService(db_session)
        courier = courier_factory(
            nationality="Saudi Arabia"
        )

        salary = service.calculate_monthly_salary(
            courier_id=courier.id,
            month=1,
            year=2025,
            base_salary=4000.00,
            housing_allowance=800.00,
            transport_allowance=300.00
        )

        # Gross: 4000 + 800 + 300 + 500 (bonus) = 5600
        # GOSI: 10% of 4000 = 400
        # Penalties: 200
        # Net: 5600 - 400 - 200 = 5000

        assert salary.base_salary == 4000.00
        assert salary.housing_allowance == 800.00
        assert salary.transport_allowance == 300.00
        assert salary.bonuses == 500.00
        assert salary.penalties == 200.00
        assert salary.gosi_deduction == 400.00
        assert salary.net_salary == 5000.00

    def test_salary_calculation_for_new_employee(self, db_session, courier_factory):
        """Test pro-rated salary for new employee"""
        service = SalaryService(db_session)

        # Employee joined on 15th of the month (worked 15 days out of 30)
        courier = courier_factory(
            joining_date=date(2025, 1, 15)
        )

        salary = service.calculate_prorated_salary(
            courier_id=courier.id,
            month=1,
            year=2025,
            base_salary=3000.00,
            days_worked=15,
            total_days=30
        )

        # Pro-rated base: 3000 * (15/30) = 1500
        assert salary.base_salary == 1500.00

    def test_salary_calculation_with_unpaid_leave(self, db_session, courier_factory):
        """Test salary with unpaid leave deduction"""
        service = SalaryService(db_session)
        courier = courier_factory()

        # 5 days unpaid leave in 30-day month
        salary = service.calculate_salary_with_leaves(
            courier_id=courier.id,
            month=1,
            year=2025,
            base_salary=3000.00,
            unpaid_leave_days=5,
            total_days=30
        )

        # Deduction: 3000 * (5/30) = 500
        # Actual salary: 3000 - 500 = 2500
        assert salary.base_salary == 2500.00

    def test_overtime_calculation(self, db_session):
        """Test overtime payment calculation"""
        service = SalaryService(db_session)

        # Saudi labor law: overtime = 1.5x hourly rate
        # Base salary 3000, work 8 hours/day, 30 days = 240 hours/month
        # Hourly rate = 3000/240 = 12.5
        # Overtime for 10 hours = 10 * 12.5 * 1.5 = 187.5

        overtime = service.calculate_overtime_pay(
            base_salary=3000.00,
            overtime_hours=10,
            standard_hours_per_month=240
        )

        assert overtime == 187.50

    def test_end_of_service_benefit_calculation(self, db_session, courier_factory):
        """Test end-of-service benefit calculation (Saudi labor law)"""
        service = SalaryService(db_session)

        # Less than 5 years: half month salary per year
        # 5+ years: full month salary per year
        # Example: 3 years service, 4000 salary
        # Benefit: 3 * (4000 / 2) = 6000

        eos = service.calculate_end_of_service_benefit(
            base_salary=4000.00,
            service_years=3,
            service_months=0
        )

        assert eos == 6000.00

        # 6 years service: first 5 years at half, remaining at full
        # (5 * 4000/2) + (1 * 4000) = 10000 + 4000 = 14000
        eos_long = service.calculate_end_of_service_benefit(
            base_salary=4000.00,
            service_years=6,
            service_months=0
        )

        assert eos_long == 14000.00

    def test_salary_validation_negative_values(self, db_session):
        """Test that negative salary values are rejected"""
        service = SalaryService(db_session)

        with pytest.raises(ValueError, match="cannot be negative"):
            service._calculate_gross_salary(
                base_salary=-1000.00,
                allowances=500.00,
                bonuses=0.00
            )

    def test_salary_validation_excessive_deductions(self, db_session):
        """Test warning for excessive deductions"""
        service = SalaryService(db_session)

        # Deductions > 50% of gross should log warning
        with patch('app.services.hr.salary_service.logger.warning') as mock_warning:
            service._validate_deductions(
                gross_salary=3000.00,
                total_deductions=2000.00  # 66% of gross
            )
            mock_warning.assert_called_once()

    def test_batch_salary_generation(self, db_session, courier_factory):
        """Test generating salaries for multiple couriers"""
        service = SalaryService(db_session)

        # Create multiple active couriers
        couriers = [
            courier_factory(status=CourierStatus.ACTIVE)
            for _ in range(5)
        ]

        salaries = service.generate_monthly_salaries_batch(
            month=1,
            year=2025,
            courier_ids=[c.id for c in couriers]
        )

        assert len(salaries) == 5
        for salary in salaries:
            assert salary.month == 1
            assert salary.year == 2025
            assert salary.net_salary > 0

    def test_salary_slip_generation(self, db_session, courier_factory):
        """Test generating salary slip PDF"""
        service = SalaryService(db_session)
        courier = courier_factory()

        # Create salary record
        salary = Salary(
            courier_id=courier.id,
            month=1,
            year=2025,
            base_salary=4000.00,
            net_salary=3500.00
        )
        db_session.add(salary)
        db_session.commit()

        # Generate slip (would return PDF bytes in real implementation)
        slip = service.generate_salary_slip(salary.id)

        assert slip is not None
        # In real test, would verify PDF content

    def test_salary_comparison_month_over_month(self, db_session, courier_factory):
        """Test comparing salary across months"""
        service = SalaryService(db_session)
        courier = courier_factory()

        # Create salaries for 2 months
        salary_jan = Salary(
            courier_id=courier.id,
            month=1,
            year=2025,
            base_salary=4000.00,
            bonuses=500.00,
            net_salary=4200.00
        )
        salary_feb = Salary(
            courier_id=courier.id,
            month=2,
            year=2025,
            base_salary=4000.00,
            bonuses=700.00,  # Higher bonus
            net_salary=4400.00
        )
        db_session.add_all([salary_jan, salary_feb])
        db_session.commit()

        comparison = service.compare_salaries(salary_jan.id, salary_feb.id)

        assert comparison["bonus_change"] == 200.00
        assert comparison["net_change"] == 200.00
        assert comparison["percentage_change"] > 0
