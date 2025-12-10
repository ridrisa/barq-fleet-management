"""
Unit Tests for Analytics Services

Tests cover:
- Performance Analytics Service
- HR Analytics Service
- Fleet Analytics Service

Author: BARQ QA Team
Last Updated: 2025-12-10
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

from app.services.analytics.performance_service import PerformanceAnalyticsService
from app.services.analytics.hr_analytics_service import HRAnalyticsService
from app.services.analytics.fleet_analytics_service import FleetAnalyticsService


# ==================== PERFORMANCE ANALYTICS SERVICE TESTS ====================

class TestPerformanceAnalyticsService:
    """Test Performance Analytics Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create PerformanceAnalyticsService instance"""
        return PerformanceAnalyticsService(db_session)

    def test_get_daily_performance(self, service, db_session, courier_factory, delivery_factory):
        """Test getting daily performance metrics"""
        courier = courier_factory()
        delivery_factory(courier, status="delivered")

        result = service.get_daily_performance(date=date.today())

        assert "total_deliveries" in result
        assert "success_rate" in result
        assert "average_delivery_time" in result

    def test_get_weekly_performance(self, service, db_session, courier_factory):
        """Test getting weekly performance metrics"""
        courier = courier_factory()

        result = service.get_weekly_performance(
            start_date=date.today() - timedelta(days=7),
            end_date=date.today()
        )

        assert "total_deliveries" in result
        assert "daily_breakdown" in result

    def test_get_monthly_performance(self, service, db_session):
        """Test getting monthly performance metrics"""
        result = service.get_monthly_performance(
            month=date.today().month,
            year=date.today().year
        )

        assert "total_deliveries" in result
        assert "comparison_with_previous" in result

    def test_get_courier_performance(self, service, db_session, courier_factory, delivery_factory):
        """Test getting individual courier performance"""
        courier = courier_factory()
        for _ in range(5):
            delivery_factory(courier)

        result = service.get_courier_performance(
            courier_id=courier.id,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        assert "courier_id" in result
        assert "total_deliveries" in result
        assert "success_rate" in result
        assert "average_rating" in result

    def test_get_top_performers(self, service, db_session, courier_factory, delivery_factory):
        """Test getting top performing couriers"""
        for _ in range(5):
            courier = courier_factory()
            for _ in range(3):
                delivery_factory(courier, status="delivered")

        result = service.get_top_performers(limit=3)

        assert len(result) <= 3
        assert all("courier_id" in r for r in result)

    def test_get_performance_trends(self, service, db_session):
        """Test getting performance trends over time"""
        result = service.get_trends(
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        assert "trend_data" in result
        assert "trend_direction" in result

    def test_get_kpi_summary(self, service, db_session):
        """Test getting KPI summary"""
        result = service.get_kpi_summary(
            start_date=date.today() - timedelta(days=7),
            end_date=date.today()
        )

        assert "deliveries_completed" in result
        assert "on_time_rate" in result
        assert "customer_satisfaction" in result


# ==================== HR ANALYTICS SERVICE TESTS ====================

class TestHRAnalyticsService:
    """Test HR Analytics Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create HRAnalyticsService instance"""
        return HRAnalyticsService(db_session)

    def test_get_headcount_summary(self, service, db_session, courier_factory):
        """Test getting headcount summary"""
        for _ in range(5):
            courier_factory(status="active")
        for _ in range(2):
            courier_factory(status="on_leave")

        result = service.get_headcount_summary()

        assert "total_employees" in result
        assert "active_count" in result
        assert "on_leave_count" in result

    def test_get_attendance_analytics(self, service, db_session, courier_factory):
        """Test getting attendance analytics"""
        courier = courier_factory()

        result = service.get_attendance_analytics(
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        assert "average_attendance_rate" in result
        assert "late_arrivals" in result
        assert "absences" in result

    def test_get_leave_analytics(self, service, db_session, courier_factory, leave_factory):
        """Test getting leave analytics"""
        courier = courier_factory()
        for _ in range(3):
            leave_factory(courier)

        result = service.get_leave_analytics(
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        assert "total_leave_days" in result
        assert "leave_by_type" in result
        assert "pending_approvals" in result

    def test_get_salary_analytics(self, service, db_session, courier_factory):
        """Test getting salary analytics"""
        for _ in range(5):
            courier_factory()

        result = service.get_salary_analytics(
            month=date.today().month,
            year=date.today().year
        )

        assert "total_payroll" in result
        assert "average_salary" in result
        assert "salary_distribution" in result

    def test_get_turnover_analytics(self, service, db_session, courier_factory):
        """Test getting turnover analytics"""
        result = service.get_turnover_analytics(
            start_date=date.today() - timedelta(days=365),
            end_date=date.today()
        )

        assert "turnover_rate" in result
        assert "new_hires" in result
        assert "terminations" in result

    def test_get_loan_analytics(self, service, db_session, courier_factory, loan_factory):
        """Test getting loan analytics"""
        courier = courier_factory()
        loan_factory(courier, amount=Decimal("5000.00"))

        result = service.get_loan_analytics()

        assert "total_loans_disbursed" in result
        assert "total_outstanding" in result
        assert "average_loan_amount" in result

    def test_get_employee_demographics(self, service, db_session, courier_factory):
        """Test getting employee demographics"""
        courier_factory(nationality="Saudi Arabia", city="Riyadh")
        courier_factory(nationality="Egypt", city="Jeddah")

        result = service.get_demographics()

        assert "nationality_breakdown" in result
        assert "city_breakdown" in result
        assert "sponsorship_breakdown" in result


# ==================== FLEET ANALYTICS SERVICE TESTS ====================

class TestFleetAnalyticsService:
    """Test Fleet Analytics Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create FleetAnalyticsService instance"""
        return FleetAnalyticsService(db_session)

    def test_get_vehicle_utilization(self, service, db_session, vehicle_factory, courier_factory):
        """Test getting vehicle utilization metrics"""
        vehicle = vehicle_factory()
        courier = courier_factory(current_vehicle_id=vehicle.id)

        result = service.get_vehicle_utilization()

        assert "total_vehicles" in result
        assert "assigned_vehicles" in result
        assert "utilization_rate" in result

    def test_get_maintenance_analytics(self, service, db_session, vehicle_factory):
        """Test getting maintenance analytics"""
        vehicle = vehicle_factory()

        result = service.get_maintenance_analytics(
            start_date=date.today() - timedelta(days=90),
            end_date=date.today()
        )

        assert "total_maintenance_cost" in result
        assert "maintenance_count" in result
        assert "average_cost_per_vehicle" in result

    def test_get_fuel_analytics(self, service, db_session, vehicle_factory):
        """Test getting fuel consumption analytics"""
        vehicle = vehicle_factory()

        result = service.get_fuel_analytics(
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        assert "total_fuel_cost" in result
        assert "total_liters" in result
        assert "average_per_vehicle" in result

    def test_get_vehicle_status_summary(self, service, db_session, vehicle_factory):
        """Test getting vehicle status summary"""
        vehicle_factory(status="active")
        vehicle_factory(status="active")
        vehicle_factory(status="maintenance")

        result = service.get_status_summary()

        assert "active_count" in result
        assert "maintenance_count" in result
        assert "retired_count" in result

    def test_get_fleet_efficiency(self, service, db_session, vehicle_factory, delivery_factory, courier_factory):
        """Test getting fleet efficiency metrics"""
        vehicle = vehicle_factory()
        courier = courier_factory(current_vehicle_id=vehicle.id)
        for _ in range(5):
            delivery_factory(courier)

        result = service.get_fleet_efficiency(
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        assert "deliveries_per_vehicle" in result
        assert "cost_per_delivery" in result
        assert "efficiency_score" in result

    def test_get_vehicle_age_analysis(self, service, db_session, vehicle_factory):
        """Test getting vehicle age analysis"""
        vehicle_factory(year=2020)
        vehicle_factory(year=2022)
        vehicle_factory(year=2024)

        result = service.get_age_analysis()

        assert "average_age" in result
        assert "age_distribution" in result
        assert "replacement_due" in result

    def test_get_courier_fleet_assignment(self, service, db_session, courier_factory, vehicle_factory):
        """Test getting courier fleet assignment analytics"""
        vehicle = vehicle_factory()
        courier_factory(current_vehicle_id=vehicle.id)
        courier_factory(current_vehicle_id=None)

        result = service.get_assignment_analytics()

        assert "assigned_couriers" in result
        assert "unassigned_couriers" in result
        assert "assignment_rate" in result

    def test_get_document_expiry_analytics(self, service, db_session, vehicle_factory):
        """Test getting document expiry analytics"""
        vehicle_factory(
            registration_expiry_date=date.today() + timedelta(days=15)
        )

        result = service.get_document_expiry_analytics()

        assert "expiring_soon" in result
        assert "already_expired" in result
        assert "valid_documents" in result

    def test_get_fleet_cost_breakdown(self, service, db_session, vehicle_factory):
        """Test getting fleet cost breakdown"""
        vehicle = vehicle_factory()

        result = service.get_cost_breakdown(
            start_date=date.today() - timedelta(days=90),
            end_date=date.today()
        )

        assert "fuel_costs" in result
        assert "maintenance_costs" in result
        assert "insurance_costs" in result
        assert "total_costs" in result

    def test_get_fleet_performance_comparison(self, service, db_session, vehicle_factory):
        """Test comparing fleet performance across periods"""
        result = service.get_performance_comparison(
            current_start=date.today() - timedelta(days=30),
            current_end=date.today(),
            previous_start=date.today() - timedelta(days=60),
            previous_end=date.today() - timedelta(days=30)
        )

        assert "current_period" in result
        assert "previous_period" in result
        assert "change_percentage" in result
