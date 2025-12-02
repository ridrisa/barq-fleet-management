"""
Unit Tests for Vehicle Model

Tests vehicle model validation, relationships, and business logic.

Author: BARQ QA Team
Last Updated: 2025-12-02
"""

import pytest
from datetime import datetime, timedelta, date
from decimal import Decimal
from sqlalchemy.exc import IntegrityError

from app.models.fleet.vehicle import Vehicle, VehicleStatus, VehicleType, FuelType, OwnershipType
from tests.utils.factories import VehicleFactory


@pytest.mark.unit
@pytest.mark.fleet
class TestVehicleModel:
    """Test Vehicle model"""

    def test_create_vehicle_with_required_fields(self, db_session):
        """Test creating vehicle with minimum required fields"""
        vehicle = Vehicle(
            plate_number="ABC-123",
            vehicle_type=VehicleType.MOTORCYCLE,
            make="Honda",
            model="Wave 110",
            year=2023
        )

        db_session.add(vehicle)
        db_session.commit()
        db_session.refresh(vehicle)

        assert vehicle.id is not None
        assert vehicle.plate_number == "ABC-123"
        assert vehicle.vehicle_type == VehicleType.MOTORCYCLE
        assert vehicle.status == VehicleStatus.ACTIVE  # Default value
        assert vehicle.created_at is not None

    def test_create_vehicle_with_all_fields(self, db_session):
        """Test creating vehicle with all fields populated"""
        vehicle = Vehicle(
            plate_number="XYZ-999",
            vehicle_type=VehicleType.CAR,
            make="Toyota",
            model="Camry",
            year=2023,
            color="Silver",
            status=VehicleStatus.ACTIVE,
            ownership_type=OwnershipType.OWNED,
            registration_number="REG-12345",
            registration_expiry_date=date(2025, 12, 31),
            insurance_company="Tawuniya",
            insurance_policy_number="POL-98765",
            insurance_expiry_date=date(2025, 12, 31),
            vin_number="VIN1234567890",
            engine_number="ENG123456",
            engine_capacity="2.5L",
            transmission="Automatic",
            fuel_type=FuelType.GASOLINE,
            current_mileage=Decimal("5000.00"),
            fuel_capacity=Decimal("60.0"),
            purchase_price=Decimal("75000.00"),
            purchase_date=date(2023, 1, 15),
            city="Riyadh"
        )

        db_session.add(vehicle)
        db_session.commit()
        db_session.refresh(vehicle)

        assert vehicle.id is not None
        assert vehicle.plate_number == "XYZ-999"
        assert vehicle.engine_capacity == "2.5L"
        assert vehicle.current_mileage == Decimal("5000.00")
        assert vehicle.purchase_price == Decimal("75000.00")

    def test_unique_plate_number_constraint(self, db_session):
        """Test that plate number must be unique"""
        Vehicle(
            plate_number="ABC-100",
            vehicle_type=VehicleType.MOTORCYCLE,
            make="Honda",
            model="Wave",
            year=2023
        )
        db_session.commit()

        # Try to create another vehicle with same plate number
        vehicle2 = Vehicle(
            plate_number="ABC-100",
            vehicle_type=VehicleType.CAR,
            make="Toyota",
            model="Camry",
            year=2023
        )
        db_session.add(vehicle2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_vehicle_status_enum(self, db_session):
        """Test vehicle status enumeration"""
        vehicle = VehicleFactory.create(status=VehicleStatus.MAINTENANCE)
        assert vehicle.status == VehicleStatus.MAINTENANCE

        vehicle.status = VehicleStatus.REPAIR
        db_session.commit()
        db_session.refresh(vehicle)

        assert vehicle.status == VehicleStatus.REPAIR

    def test_vehicle_type_enum(self, db_session):
        """Test vehicle type enumeration"""
        statuses = [
            VehicleType.MOTORCYCLE,
            VehicleType.CAR,
            VehicleType.VAN,
            VehicleType.TRUCK,
            VehicleType.BICYCLE
        ]

        for vtype in statuses:
            vehicle = VehicleFactory.create(vehicle_type=vtype)
            assert vehicle.vehicle_type == vtype

    def test_fuel_type_enum(self, db_session):
        """Test fuel type enumeration"""
        fuel_types = [
            FuelType.GASOLINE,
            FuelType.DIESEL,
            FuelType.ELECTRIC,
            FuelType.HYBRID
        ]

        for ftype in fuel_types:
            vehicle = VehicleFactory.create(fuel_type=ftype)
            assert vehicle.fuel_type == ftype

    def test_ownership_type_enum(self, db_session):
        """Test ownership type enumeration"""
        ownership_types = [
            OwnershipType.OWNED,
            OwnershipType.LEASED,
            OwnershipType.RENTED
        ]

        for otype in ownership_types:
            vehicle = VehicleFactory.create(ownership_type=otype)
            assert vehicle.ownership_type == otype

    def test_decimal_fields_precision(self, db_session):
        """Test decimal fields store correct precision"""
        vehicle = VehicleFactory.create(
            current_mileage=Decimal("12345.67"),
            fuel_capacity=Decimal("55.75"),
            purchase_price=Decimal("80000.50")
        )

        db_session.refresh(vehicle)

        assert vehicle.current_mileage == Decimal("12345.67")
        assert vehicle.fuel_capacity == Decimal("55.75")
        assert vehicle.purchase_price == Decimal("80000.50")

    def test_vehicle_timestamps(self, db_session):
        """Test created_at and updated_at timestamps"""
        vehicle = VehicleFactory.create()

        created_at = vehicle.created_at
        assert created_at is not None

        # Update vehicle
        vehicle.current_mileage = Decimal("10000.00")
        db_session.commit()
        db_session.refresh(vehicle)

        # updated_at should be later than created_at
        assert vehicle.updated_at >= created_at

    def test_vehicle_city_indexing(self, db_session):
        """Test vehicles can be filtered by city"""
        VehicleFactory.create(city="Riyadh")
        VehicleFactory.create(city="Riyadh")
        VehicleFactory.create(city="Jeddah")

        riyadh_vehicles = db_session.query(Vehicle).filter_by(city="Riyadh").all()
        jeddah_vehicles = db_session.query(Vehicle).filter_by(city="Jeddah").all()

        assert len(riyadh_vehicles) == 2
        assert len(jeddah_vehicles) == 1

    def test_leased_vehicle_monthly_cost(self, db_session):
        """Test leased vehicle has monthly lease cost"""
        vehicle = VehicleFactory.create(
            ownership_type=OwnershipType.LEASED,
            monthly_lease_cost=Decimal("2000.00")
        )

        assert vehicle.ownership_type == OwnershipType.LEASED
        assert vehicle.monthly_lease_cost == Decimal("2000.00")

    def test_vehicle_insurance_expiry(self, db_session):
        """Test vehicle insurance expiry date"""
        expiry_date = date(2025, 12, 31)
        vehicle = VehicleFactory.create(
            insurance_expiry_date=expiry_date,
            insurance_company="Tawuniya",
            insurance_policy_number="POL-12345"
        )

        assert vehicle.insurance_expiry_date == expiry_date
        assert vehicle.insurance_company == "Tawuniya"

    def test_vehicle_registration_expiry(self, db_session):
        """Test vehicle registration expiry date"""
        expiry_date = date(2025, 6, 30)
        vehicle = VehicleFactory.create(
            registration_expiry_date=expiry_date,
            registration_number="REG-67890"
        )

        assert vehicle.registration_expiry_date == expiry_date
        assert vehicle.registration_number == "REG-67890"

    def test_vehicle_vin_uniqueness(self, db_session):
        """Test VIN number must be unique"""
        VehicleFactory.create(vin_number="VIN123456789")

        vehicle2 = Vehicle(
            plate_number="DEF-456",
            vehicle_type=VehicleType.CAR,
            make="Toyota",
            model="Camry",
            year=2023,
            vin_number="VIN123456789"
        )
        db_session.add(vehicle2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_retired_vehicle_status(self, db_session):
        """Test retiring a vehicle"""
        vehicle = VehicleFactory.create(status=VehicleStatus.ACTIVE)

        vehicle.status = VehicleStatus.RETIRED
        db_session.commit()
        db_session.refresh(vehicle)

        assert vehicle.status == VehicleStatus.RETIRED

    def test_electric_vehicle_no_fuel_capacity(self, db_session):
        """Test electric vehicle can have null fuel capacity"""
        vehicle = VehicleFactory.create(
            fuel_type=FuelType.ELECTRIC,
            fuel_capacity=None
        )

        assert vehicle.fuel_type == FuelType.ELECTRIC
        assert vehicle.fuel_capacity is None

    def test_vehicle_depreciation_rate(self, db_session):
        """Test vehicle depreciation rate"""
        vehicle = VehicleFactory.create(
            purchase_price=Decimal("100000.00"),
            depreciation_rate=Decimal("20.0")
        )

        assert vehicle.depreciation_rate == Decimal("20.0")

    def test_query_vehicles_by_status(self, db_session):
        """Test querying vehicles by status"""
        VehicleFactory.create(status=VehicleStatus.ACTIVE)
        VehicleFactory.create(status=VehicleStatus.ACTIVE)
        VehicleFactory.create(status=VehicleStatus.MAINTENANCE)
        VehicleFactory.create(status=VehicleStatus.REPAIR)

        active_vehicles = db_session.query(Vehicle).filter_by(
            status=VehicleStatus.ACTIVE
        ).all()

        assert len(active_vehicles) == 2

    def test_query_vehicles_by_type(self, db_session):
        """Test querying vehicles by type"""
        VehicleFactory.create(vehicle_type=VehicleType.MOTORCYCLE)
        VehicleFactory.create(vehicle_type=VehicleType.MOTORCYCLE)
        VehicleFactory.create(vehicle_type=VehicleType.CAR)

        motorcycles = db_session.query(Vehicle).filter_by(
            vehicle_type=VehicleType.MOTORCYCLE
        ).all()

        assert len(motorcycles) == 2

    def test_vehicle_soft_delete(self, db_session):
        """Test soft delete functionality if implemented"""
        vehicle = VehicleFactory.create()
        vehicle_id = vehicle.id

        # Vehicles might be soft-deleted by setting status to RETIRED
        vehicle.status = VehicleStatus.RETIRED
        db_session.commit()

        retired_vehicle = db_session.query(Vehicle).filter_by(id=vehicle_id).first()
        assert retired_vehicle.status == VehicleStatus.RETIRED
