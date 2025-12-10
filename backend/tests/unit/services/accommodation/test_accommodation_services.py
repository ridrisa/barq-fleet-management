"""
Unit Tests for Accommodation Services

Tests cover:
- Building Service
- Room Service
- Bed Service
- Allocation Service

Author: BARQ QA Team
Last Updated: 2025-12-10
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

from app.services.accommodation.building_service import BuildingService
from app.services.accommodation.room_service import RoomService
from app.services.accommodation.bed_service import BedService
from app.services.accommodation.allocation_service import AllocationService


# ==================== BUILDING SERVICE TESTS ====================

class TestBuildingService:
    """Test Building Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create BuildingService instance"""
        from app.models.accommodation.building import Building
        return BuildingService(Building)

    def test_create_building(self, service, db_session, test_organization):
        """Test creating a building"""
        from app.schemas.accommodation.building import BuildingCreate

        building_data = BuildingCreate(
            name="Building A",
            address="123 Main St, Riyadh",
            city="Riyadh",
            total_capacity=100,
            organization_id=test_organization.id
        )

        building = service.create(db_session, obj_in=building_data)

        assert building is not None
        assert building.name == "Building A"

    def test_get_building_by_id(self, service, db_session, test_organization):
        """Test getting building by ID"""
        from app.models.accommodation.building import Building

        building = Building(
            name="Test Building",
            address="456 Test St",
            city="Riyadh",
            organization_id=test_organization.id
        )
        db_session.add(building)
        db_session.commit()

        result = service.get(db_session, building.id)

        assert result is not None
        assert result.id == building.id

    def test_get_buildings_by_city(self, service, db_session, test_organization):
        """Test getting buildings by city"""
        from app.models.accommodation.building import Building

        building1 = Building(name="Riyadh B1", city="Riyadh", organization_id=test_organization.id)
        building2 = Building(name="Jeddah B1", city="Jeddah", organization_id=test_organization.id)
        db_session.add_all([building1, building2])
        db_session.commit()

        result = service.get_by_city(db_session, city="Riyadh")

        assert all(b.city == "Riyadh" for b in result)

    def test_get_buildings_with_availability(self, service, db_session, test_organization):
        """Test getting buildings with available space"""
        from app.models.accommodation.building import Building

        building = Building(
            name="Available Building",
            city="Riyadh",
            total_capacity=100,
            current_occupancy=50,
            organization_id=test_organization.id
        )
        db_session.add(building)
        db_session.commit()

        result = service.get_with_availability(db_session)

        assert len(result) >= 1

    def test_update_building_capacity(self, service, db_session, test_organization):
        """Test updating building capacity"""
        from app.models.accommodation.building import Building

        building = Building(
            name="Capacity Building",
            city="Riyadh",
            total_capacity=100,
            organization_id=test_organization.id
        )
        db_session.add(building)
        db_session.commit()

        result = service.update_capacity(db_session, building_id=building.id, new_capacity=150)

        assert result.total_capacity == 150

    def test_get_building_statistics(self, service, db_session, test_organization):
        """Test getting building statistics"""
        from app.models.accommodation.building import Building

        building = Building(
            name="Stats Building",
            city="Riyadh",
            total_capacity=100,
            current_occupancy=75,
            organization_id=test_organization.id
        )
        db_session.add(building)
        db_session.commit()

        stats = service.get_statistics(db_session)

        assert "total_buildings" in stats
        assert "total_capacity" in stats
        assert "total_occupancy" in stats


# ==================== ROOM SERVICE TESTS ====================

class TestRoomService:
    """Test Room Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create RoomService instance"""
        from app.models.accommodation.room import Room
        return RoomService(Room)

    @pytest.fixture
    def test_building(self, db_session, test_organization):
        """Create a test building"""
        from app.models.accommodation.building import Building
        building = Building(
            name="Test Building",
            city="Riyadh",
            organization_id=test_organization.id
        )
        db_session.add(building)
        db_session.commit()
        return building

    def test_create_room(self, service, db_session, test_building, test_organization):
        """Test creating a room"""
        from app.schemas.accommodation.room import RoomCreate

        room_data = RoomCreate(
            room_number="101",
            building_id=test_building.id,
            floor=1,
            capacity=4,
            organization_id=test_organization.id
        )

        room = service.create(db_session, obj_in=room_data)

        assert room is not None
        assert room.room_number == "101"

    def test_get_rooms_by_building(self, service, db_session, test_building, test_organization):
        """Test getting rooms by building"""
        from app.models.accommodation.room import Room

        room1 = Room(room_number="101", building_id=test_building.id, organization_id=test_organization.id)
        room2 = Room(room_number="102", building_id=test_building.id, organization_id=test_organization.id)
        db_session.add_all([room1, room2])
        db_session.commit()

        result = service.get_by_building(db_session, building_id=test_building.id)

        assert len(result) >= 2
        assert all(r.building_id == test_building.id for r in result)

    def test_get_available_rooms(self, service, db_session, test_building, test_organization):
        """Test getting available rooms"""
        from app.models.accommodation.room import Room

        available = Room(
            room_number="201",
            building_id=test_building.id,
            capacity=4,
            current_occupancy=2,
            organization_id=test_organization.id
        )
        full = Room(
            room_number="202",
            building_id=test_building.id,
            capacity=4,
            current_occupancy=4,
            organization_id=test_organization.id
        )
        db_session.add_all([available, full])
        db_session.commit()

        result = service.get_available_rooms(db_session)

        assert all(r.current_occupancy < r.capacity for r in result)

    def test_get_rooms_by_floor(self, service, db_session, test_building, test_organization):
        """Test getting rooms by floor"""
        from app.models.accommodation.room import Room

        floor1_room = Room(room_number="101", building_id=test_building.id, floor=1, organization_id=test_organization.id)
        floor2_room = Room(room_number="201", building_id=test_building.id, floor=2, organization_id=test_organization.id)
        db_session.add_all([floor1_room, floor2_room])
        db_session.commit()

        result = service.get_by_floor(db_session, building_id=test_building.id, floor=1)

        assert all(r.floor == 1 for r in result)

    def test_update_room_status(self, service, db_session, test_building, test_organization):
        """Test updating room status"""
        from app.models.accommodation.room import Room, RoomStatus

        room = Room(
            room_number="301",
            building_id=test_building.id,
            status=RoomStatus.AVAILABLE,
            organization_id=test_organization.id
        )
        db_session.add(room)
        db_session.commit()

        result = service.update_status(db_session, room_id=room.id, status=RoomStatus.MAINTENANCE)

        assert result.status == RoomStatus.MAINTENANCE


# ==================== BED SERVICE TESTS ====================

class TestBedService:
    """Test Bed Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create BedService instance"""
        from app.models.accommodation.bed import Bed
        return BedService(Bed)

    @pytest.fixture
    def test_room(self, db_session, test_organization):
        """Create a test room"""
        from app.models.accommodation.building import Building
        from app.models.accommodation.room import Room

        building = Building(name="Test Building", city="Riyadh", organization_id=test_organization.id)
        db_session.add(building)
        db_session.flush()

        room = Room(room_number="101", building_id=building.id, organization_id=test_organization.id)
        db_session.add(room)
        db_session.commit()
        return room

    def test_create_bed(self, service, db_session, test_room, test_organization):
        """Test creating a bed"""
        from app.schemas.accommodation.bed import BedCreate

        bed_data = BedCreate(
            bed_number="A",
            room_id=test_room.id,
            organization_id=test_organization.id
        )

        bed = service.create(db_session, obj_in=bed_data)

        assert bed is not None
        assert bed.bed_number == "A"

    def test_get_beds_by_room(self, service, db_session, test_room, test_organization):
        """Test getting beds by room"""
        from app.models.accommodation.bed import Bed

        bed1 = Bed(bed_number="A", room_id=test_room.id, organization_id=test_organization.id)
        bed2 = Bed(bed_number="B", room_id=test_room.id, organization_id=test_organization.id)
        db_session.add_all([bed1, bed2])
        db_session.commit()

        result = service.get_by_room(db_session, room_id=test_room.id)

        assert len(result) >= 2
        assert all(b.room_id == test_room.id for b in result)

    def test_get_available_beds(self, service, db_session, test_room, test_organization):
        """Test getting available beds"""
        from app.models.accommodation.bed import Bed, BedStatus

        available = Bed(bed_number="A", room_id=test_room.id, status=BedStatus.AVAILABLE, organization_id=test_organization.id)
        occupied = Bed(bed_number="B", room_id=test_room.id, status=BedStatus.OCCUPIED, organization_id=test_organization.id)
        db_session.add_all([available, occupied])
        db_session.commit()

        result = service.get_available_beds(db_session)

        assert all(b.status == BedStatus.AVAILABLE for b in result)

    def test_assign_bed_to_courier(self, service, db_session, test_room, courier_factory, test_organization):
        """Test assigning bed to courier"""
        from app.models.accommodation.bed import Bed, BedStatus

        bed = Bed(bed_number="A", room_id=test_room.id, status=BedStatus.AVAILABLE, organization_id=test_organization.id)
        db_session.add(bed)
        db_session.commit()

        courier = courier_factory()

        result = service.assign_to_courier(db_session, bed_id=bed.id, courier_id=courier.id)

        assert result.courier_id == courier.id
        assert result.status == BedStatus.OCCUPIED

    def test_release_bed(self, service, db_session, test_room, courier_factory, test_organization):
        """Test releasing a bed"""
        from app.models.accommodation.bed import Bed, BedStatus

        courier = courier_factory()
        bed = Bed(
            bed_number="A",
            room_id=test_room.id,
            status=BedStatus.OCCUPIED,
            courier_id=courier.id,
            organization_id=test_organization.id
        )
        db_session.add(bed)
        db_session.commit()

        result = service.release_bed(db_session, bed_id=bed.id)

        assert result.courier_id is None
        assert result.status == BedStatus.AVAILABLE


# ==================== ALLOCATION SERVICE TESTS ====================

class TestAllocationService:
    """Test Allocation Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create AllocationService instance"""
        from app.models.accommodation.allocation import Allocation
        return AllocationService(Allocation)

    @pytest.fixture
    def test_bed(self, db_session, test_organization):
        """Create a test bed"""
        from app.models.accommodation.building import Building
        from app.models.accommodation.room import Room
        from app.models.accommodation.bed import Bed, BedStatus

        building = Building(name="Test Building", city="Riyadh", organization_id=test_organization.id)
        db_session.add(building)
        db_session.flush()

        room = Room(room_number="101", building_id=building.id, organization_id=test_organization.id)
        db_session.add(room)
        db_session.flush()

        bed = Bed(bed_number="A", room_id=room.id, status=BedStatus.AVAILABLE, organization_id=test_organization.id)
        db_session.add(bed)
        db_session.commit()
        return bed

    def test_create_allocation(self, service, db_session, test_bed, courier_factory, test_organization):
        """Test creating an allocation"""
        from app.schemas.accommodation.allocation import AllocationCreate

        courier = courier_factory()
        allocation_data = AllocationCreate(
            courier_id=courier.id,
            bed_id=test_bed.id,
            start_date=date.today(),
            organization_id=test_organization.id
        )

        allocation = service.create(db_session, obj_in=allocation_data)

        assert allocation is not None
        assert allocation.courier_id == courier.id
        assert allocation.bed_id == test_bed.id

    def test_get_allocations_by_courier(self, service, db_session, test_bed, courier_factory, test_organization):
        """Test getting allocations by courier"""
        from app.models.accommodation.allocation import Allocation

        courier = courier_factory()
        allocation = Allocation(
            courier_id=courier.id,
            bed_id=test_bed.id,
            start_date=date.today(),
            organization_id=test_organization.id
        )
        db_session.add(allocation)
        db_session.commit()

        result = service.get_by_courier(db_session, courier_id=courier.id)

        assert len(result) >= 1
        assert all(a.courier_id == courier.id for a in result)

    def test_get_active_allocations(self, service, db_session, test_bed, courier_factory, test_organization):
        """Test getting active allocations"""
        from app.models.accommodation.allocation import Allocation

        courier = courier_factory()
        active = Allocation(
            courier_id=courier.id,
            bed_id=test_bed.id,
            start_date=date.today(),
            is_active=True,
            organization_id=test_organization.id
        )
        db_session.add(active)
        db_session.commit()

        result = service.get_active(db_session)

        assert all(a.is_active is True for a in result)

    def test_end_allocation(self, service, db_session, test_bed, courier_factory, test_organization):
        """Test ending an allocation"""
        from app.models.accommodation.allocation import Allocation

        courier = courier_factory()
        allocation = Allocation(
            courier_id=courier.id,
            bed_id=test_bed.id,
            start_date=date.today() - timedelta(days=30),
            is_active=True,
            organization_id=test_organization.id
        )
        db_session.add(allocation)
        db_session.commit()

        result = service.end_allocation(db_session, allocation_id=allocation.id, end_date=date.today())

        assert result.is_active is False
        assert result.end_date == date.today()

    def test_transfer_allocation(self, service, db_session, courier_factory, test_organization):
        """Test transferring courier to different bed"""
        from app.models.accommodation.building import Building
        from app.models.accommodation.room import Room
        from app.models.accommodation.bed import Bed, BedStatus
        from app.models.accommodation.allocation import Allocation

        building = Building(name="Transfer Building", city="Riyadh", organization_id=test_organization.id)
        db_session.add(building)
        db_session.flush()

        room = Room(room_number="101", building_id=building.id, organization_id=test_organization.id)
        db_session.add(room)
        db_session.flush()

        old_bed = Bed(bed_number="A", room_id=room.id, status=BedStatus.OCCUPIED, organization_id=test_organization.id)
        new_bed = Bed(bed_number="B", room_id=room.id, status=BedStatus.AVAILABLE, organization_id=test_organization.id)
        db_session.add_all([old_bed, new_bed])
        db_session.flush()

        courier = courier_factory()
        allocation = Allocation(
            courier_id=courier.id,
            bed_id=old_bed.id,
            start_date=date.today() - timedelta(days=30),
            is_active=True,
            organization_id=test_organization.id
        )
        db_session.add(allocation)
        db_session.commit()

        result = service.transfer(
            db_session,
            allocation_id=allocation.id,
            new_bed_id=new_bed.id
        )

        assert result.bed_id == new_bed.id

    def test_get_allocation_statistics(self, service, db_session, test_organization):
        """Test getting allocation statistics"""
        stats = service.get_statistics(db_session)

        assert "total_allocations" in stats
        assert "active_allocations" in stats
        assert "average_duration" in stats

    def test_get_allocations_by_date_range(self, service, db_session, test_bed, courier_factory, test_organization):
        """Test getting allocations by date range"""
        from app.models.accommodation.allocation import Allocation

        courier = courier_factory()
        allocation = Allocation(
            courier_id=courier.id,
            bed_id=test_bed.id,
            start_date=date.today() - timedelta(days=10),
            organization_id=test_organization.id
        )
        db_session.add(allocation)
        db_session.commit()

        result = service.get_by_date_range(
            db_session,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        assert len(result) >= 1
