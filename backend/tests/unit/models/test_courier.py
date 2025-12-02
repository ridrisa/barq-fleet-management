"""
Unit Tests for Courier Model

Tests cover:
- Model creation and validation
- Enum values
- Computed properties
- Relationships
- Business logic methods

Author: BARQ QA Team
Last Updated: 2025-12-02
"""

import pytest
from datetime import datetime, timedelta, date
from sqlalchemy.exc import IntegrityError

from app.models.fleet.courier import Courier, CourierStatus, SponsorshipStatus, ProjectType
from tests.utils.test_helpers import DataGenerator


class TestCourierModel:
    """Test Courier model"""

    def test_create_courier_with_required_fields(self, db_session):
        """Test creating courier with minimum required fields"""
        courier = Courier(
            barq_id=DataGenerator.random_barq_id(),
            full_name="Ahmad Hassan",
            mobile_number="+966501234567"
        )
        db_session.add(courier)
        db_session.commit()
        db_session.refresh(courier)

        assert courier.id is not None
        assert courier.full_name == "Ahmad Hassan"
        assert courier.status == CourierStatus.ONBOARDING
        assert courier.created_at is not None
        assert courier.updated_at is None

    def test_create_courier_with_all_fields(self, db_session):
        """Test creating courier with all fields"""
        joining_date = date(2025, 1, 1)
        dob = date(1995, 5, 15)

        courier = Courier(
            barq_id="BRQ-12345",
            full_name="Mohammad Ali",
            email="mohammad.ali@test.com",
            mobile_number="+966501234567",
            employee_id="EMP-001",
            status=CourierStatus.ACTIVE,
            sponsorship_status=SponsorshipStatus.INHOUSE,
            project_type=ProjectType.BARQ,
            position="Senior Courier",
            city="Riyadh",
            joining_date=joining_date,
            date_of_birth=dob,
            national_id="1234567890",
            nationality="Saudi Arabia",
        )
        db_session.add(courier)
        db_session.commit()
        db_session.refresh(courier)

        assert courier.barq_id == "BRQ-12345"
        assert courier.employee_id == "EMP-001"
        assert courier.status == CourierStatus.ACTIVE
        assert courier.sponsorship_status == SponsorshipStatus.INHOUSE
        assert courier.project_type == ProjectType.BARQ
        assert courier.joining_date == joining_date
        assert courier.date_of_birth == dob

    def test_unique_barq_id_constraint(self, db_session):
        """Test that barq_id must be unique"""
        barq_id = DataGenerator.random_barq_id()

        courier1 = Courier(
            barq_id=barq_id,
            full_name="Courier 1",
            mobile_number="+966501111111"
        )
        db_session.add(courier1)
        db_session.commit()

        courier2 = Courier(
            barq_id=barq_id,  # Duplicate BARQ ID
            full_name="Courier 2",
            mobile_number="+966502222222"
        )
        db_session.add(courier2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_unique_email_constraint(self, db_session):
        """Test that email must be unique"""
        email = DataGenerator.random_email()

        courier1 = Courier(
            barq_id=DataGenerator.random_barq_id(),
            full_name="Courier 1",
            email=email,
            mobile_number="+966501111111"
        )
        db_session.add(courier1)
        db_session.commit()

        courier2 = Courier(
            barq_id=DataGenerator.random_barq_id(),
            full_name="Courier 2",
            email=email,  # Duplicate email
            mobile_number="+966502222222"
        )
        db_session.add(courier2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_courier_status_enum(self, db_session):
        """Test all courier status values"""
        statuses = [
            CourierStatus.ACTIVE,
            CourierStatus.INACTIVE,
            CourierStatus.ON_LEAVE,
            CourierStatus.TERMINATED,
            CourierStatus.ONBOARDING,
            CourierStatus.SUSPENDED,
        ]

        for status in statuses:
            courier = Courier(
                barq_id=DataGenerator.random_barq_id(),
                full_name=f"Courier {status.value}",
                mobile_number=DataGenerator.random_phone(),
                status=status
            )
            db_session.add(courier)
            db_session.commit()
            db_session.refresh(courier)

            assert courier.status == status
            db_session.rollback()

    def test_sponsorship_status_enum(self, db_session):
        """Test all sponsorship status values"""
        statuses = [
            SponsorshipStatus.AJEER,
            SponsorshipStatus.INHOUSE,
            SponsorshipStatus.TRIAL,
            SponsorshipStatus.FREELANCER,
        ]

        for status in statuses:
            courier = Courier(
                barq_id=DataGenerator.random_barq_id(),
                full_name=f"Courier {status.value}",
                mobile_number=DataGenerator.random_phone(),
                sponsorship_status=status
            )
            db_session.add(courier)
            db_session.commit()
            db_session.refresh(courier)

            assert courier.sponsorship_status == status
            db_session.rollback()

    def test_is_active_property(self, db_session):
        """Test is_active computed property"""
        # Active courier
        active_courier = Courier(
            barq_id=DataGenerator.random_barq_id(),
            full_name="Active Courier",
            mobile_number=DataGenerator.random_phone(),
            status=CourierStatus.ACTIVE
        )
        assert active_courier.is_active is True

        # Inactive courier
        inactive_courier = Courier(
            barq_id=DataGenerator.random_barq_id(),
            full_name="Inactive Courier",
            mobile_number=DataGenerator.random_phone(),
            status=CourierStatus.INACTIVE
        )
        assert inactive_courier.is_active is False

        # Terminated courier
        terminated_courier = Courier(
            barq_id=DataGenerator.random_barq_id(),
            full_name="Terminated Courier",
            mobile_number=DataGenerator.random_phone(),
            status=CourierStatus.TERMINATED
        )
        assert terminated_courier.is_active is False

    def test_has_vehicle_property(self, db_session):
        """Test has_vehicle computed property"""
        # Courier without vehicle
        courier_no_vehicle = Courier(
            barq_id=DataGenerator.random_barq_id(),
            full_name="No Vehicle Courier",
            mobile_number=DataGenerator.random_phone()
        )
        assert courier_no_vehicle.has_vehicle is False

        # Courier with vehicle (would need vehicle fixture in real test)
        courier_with_vehicle = Courier(
            barq_id=DataGenerator.random_barq_id(),
            full_name="With Vehicle Courier",
            mobile_number=DataGenerator.random_phone(),
            current_vehicle_id=1
        )
        assert courier_with_vehicle.has_vehicle is True

    def test_is_document_expired_property(self, db_session):
        """Test is_document_expired computed property"""
        today = date.today()

        # All documents valid
        valid_courier = Courier(
            barq_id=DataGenerator.random_barq_id(),
            full_name="Valid Documents",
            mobile_number=DataGenerator.random_phone(),
            iqama_expiry_date=today + timedelta(days=30),
            passport_expiry_date=today + timedelta(days=60),
            license_expiry_date=today + timedelta(days=90)
        )
        assert valid_courier.is_document_expired is False

        # Expired iqama
        expired_iqama = Courier(
            barq_id=DataGenerator.random_barq_id(),
            full_name="Expired Iqama",
            mobile_number=DataGenerator.random_phone(),
            iqama_expiry_date=today - timedelta(days=1),
            passport_expiry_date=today + timedelta(days=60),
            license_expiry_date=today + timedelta(days=90)
        )
        assert expired_iqama.is_document_expired is True

        # Expired passport
        expired_passport = Courier(
            barq_id=DataGenerator.random_barq_id(),
            full_name="Expired Passport",
            mobile_number=DataGenerator.random_phone(),
            passport_expiry_date=today - timedelta(days=1)
        )
        assert expired_passport.is_document_expired is True

        # Expired license
        expired_license = Courier(
            barq_id=DataGenerator.random_barq_id(),
            full_name="Expired License",
            mobile_number=DataGenerator.random_phone(),
            license_expiry_date=today - timedelta(days=1)
        )
        assert expired_license.is_document_expired is True

    def test_courier_repr(self, db_session):
        """Test string representation"""
        courier = Courier(
            barq_id="BRQ-12345",
            full_name="Test Courier",
            mobile_number="+966501234567",
            status=CourierStatus.ACTIVE
        )

        repr_str = repr(courier)
        assert "BRQ-12345" in repr_str
        assert "Test Courier" in repr_str
        assert "active" in repr_str

    def test_performance_metrics_defaults(self, db_session):
        """Test default values for performance metrics"""
        courier = Courier(
            barq_id=DataGenerator.random_barq_id(),
            full_name="Test Courier",
            mobile_number=DataGenerator.random_phone()
        )
        db_session.add(courier)
        db_session.commit()
        db_session.refresh(courier)

        assert courier.performance_score == 0.0
        assert courier.total_deliveries == 0

    def test_nullable_fields(self, db_session):
        """Test that optional fields can be null"""
        courier = Courier(
            barq_id=DataGenerator.random_barq_id(),
            full_name="Minimal Courier",
            mobile_number=DataGenerator.random_phone()
        )
        db_session.add(courier)
        db_session.commit()
        db_session.refresh(courier)

        assert courier.email is None
        assert courier.employee_id is None
        assert courier.joining_date is None
        assert courier.last_working_day is None
        assert courier.national_id is None
        assert courier.notes is None
