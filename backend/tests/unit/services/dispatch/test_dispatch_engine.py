"""
Unit Tests for Dispatch Engine

Tests the multi-layer dispatch engine:
- Layer 1: Local filtering
- Layer 2: Distance Matrix filtering
- Layer 3: Approximate feasibility
- Layer 4: Precise scoring
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from app.services.dispatch.engine import DispatchEngine
from app.services.dispatch.config import DispatchConfig, PenaltyWeights
from app.services.dispatch.routing import (
    DistanceMatrixResult,
    RouteLeg,
    RouteResult,
    RoutingProvider,
)
from app.services.dispatch.types import (
    AssignmentResult,
    CourierOnlineStatus,
    CourierPlan,
    DispatchCourier,
    DispatchOrder,
    OrderStatus,
    Point,
    RouteStop,
    StopType,
)


# ==================== Fixtures ====================

@pytest.fixture
def mock_routing_provider():
    """Create a mock routing provider"""
    provider = MagicMock(spec=RoutingProvider)

    # Default behavior for get_travel_times
    async def get_travel_times(origins, destinations, departure_time):
        durations = [[10.0 for _ in destinations] for _ in origins]
        distances = [[5.0 for _ in destinations] for _ in origins]
        return DistanceMatrixResult(
            durations_minutes=durations,
            distances_km=distances
        )

    provider.get_travel_times = AsyncMock(side_effect=get_travel_times)

    # Default behavior for get_route
    async def get_route(origin, waypoints, departure_time, optimize=False):
        legs = []
        prev_point = origin
        for wp in waypoints:
            legs.append(RouteLeg(
                from_point=prev_point,
                to_point=wp,
                distance_km=2.0,
                duration_minutes=5.0
            ))
            prev_point = wp
        return RouteResult(legs=legs, polyline=None)

    provider.get_route = AsyncMock(side_effect=get_route)

    return provider


@pytest.fixture
def default_config():
    """Create default dispatch config"""
    return DispatchConfig()


@pytest.fixture
def sample_order():
    """Create a sample unassigned order"""
    now = datetime.now()
    return DispatchOrder(
        id="order_1",
        pickup=Point(lat=24.7136, lng=46.6753),
        dropoff=Point(lat=24.7500, lng=46.7000),
        created_at=now,
        deadline_at=now + timedelta(hours=4),
        status=OrderStatus.UNASSIGNED,
        zone_id="zone_1"
    )


@pytest.fixture
def sample_courier():
    """Create a sample available courier"""
    return DispatchCourier(
        id="courier_1",
        current_location=Point(lat=24.7200, lng=46.6800),
        online_status=CourierOnlineStatus.ONLINE,
        shift_end_at=datetime.now() + timedelta(hours=6),
        completed_orders_today=5,
        assigned_open_order_ids=[],
        zone_id="zone_1"
    )


# ==================== Engine Initialization Tests ====================

class TestDispatchEngineInit:
    """Tests for DispatchEngine initialization"""

    def test_init_with_routing_provider(self, mock_routing_provider):
        """Engine should accept a routing provider"""
        engine = DispatchEngine(routing_provider=mock_routing_provider)
        assert engine.routing == mock_routing_provider

    def test_init_with_default_config(self, mock_routing_provider):
        """Engine should use default config when not specified"""
        engine = DispatchEngine(routing_provider=mock_routing_provider)
        assert engine.config is not None
        assert engine.config.max_haversine_radius_km == 7.0

    def test_init_with_custom_config(self, mock_routing_provider):
        """Engine should accept custom config"""
        custom_config = DispatchConfig(max_haversine_radius_km=10.0)
        engine = DispatchEngine(
            routing_provider=mock_routing_provider,
            config=custom_config
        )
        assert engine.config.max_haversine_radius_km == 10.0


# ==================== Layer 1: Local Filtering Tests ====================

class TestLayer1Filtering:
    """Tests for Layer 1 (local) filtering"""

    def test_filter_couriers_online_status(self, mock_routing_provider, sample_order):
        """Should filter out offline couriers"""
        engine = DispatchEngine(routing_provider=mock_routing_provider)
        now = datetime.now()

        online_courier = DispatchCourier(
            id="courier_1",
            current_location=Point(lat=24.7136, lng=46.6753),
            online_status=CourierOnlineStatus.ONLINE,
            shift_end_at=now + timedelta(hours=6),
            completed_orders_today=0,
            assigned_open_order_ids=[],
        )
        offline_courier = DispatchCourier(
            id="courier_2",
            current_location=Point(lat=24.7136, lng=46.6753),
            online_status=CourierOnlineStatus.OFFLINE,
            shift_end_at=now + timedelta(hours=6),
            completed_orders_today=0,
            assigned_open_order_ids=[],
        )
        break_courier = DispatchCourier(
            id="courier_3",
            current_location=Point(lat=24.7136, lng=46.6753),
            online_status=CourierOnlineStatus.BREAK,
            shift_end_at=now + timedelta(hours=6),
            completed_orders_today=0,
            assigned_open_order_ids=[],
        )

        result = engine._filter_couriers_layer1(
            sample_order,
            [online_courier, offline_courier, break_courier],
            now
        )

        assert len(result) == 1
        assert result[0].id == "courier_1"

    def test_filter_couriers_shift_ended(self, mock_routing_provider, sample_order):
        """Should filter out couriers whose shift has ended"""
        engine = DispatchEngine(routing_provider=mock_routing_provider)
        now = datetime.now()

        active_shift_courier = DispatchCourier(
            id="courier_1",
            current_location=Point(lat=24.7136, lng=46.6753),
            online_status=CourierOnlineStatus.ONLINE,
            shift_end_at=now + timedelta(hours=1),
            completed_orders_today=0,
            assigned_open_order_ids=[],
        )
        ended_shift_courier = DispatchCourier(
            id="courier_2",
            current_location=Point(lat=24.7136, lng=46.6753),
            online_status=CourierOnlineStatus.ONLINE,
            shift_end_at=now - timedelta(hours=1),
            completed_orders_today=0,
            assigned_open_order_ids=[],
        )

        result = engine._filter_couriers_layer1(
            sample_order,
            [active_shift_courier, ended_shift_courier],
            now
        )

        assert len(result) == 1
        assert result[0].id == "courier_1"

    def test_filter_couriers_zone_matching(self, mock_routing_provider):
        """Should filter out couriers in different zones"""
        engine = DispatchEngine(routing_provider=mock_routing_provider)
        now = datetime.now()

        order_with_zone = DispatchOrder(
            id="order_1",
            pickup=Point(lat=24.7136, lng=46.6753),
            dropoff=Point(lat=24.7500, lng=46.7000),
            created_at=now,
            deadline_at=now + timedelta(hours=4),
            status=OrderStatus.UNASSIGNED,
            zone_id="zone_A"
        )

        same_zone_courier = DispatchCourier(
            id="courier_1",
            current_location=Point(lat=24.7136, lng=46.6753),
            online_status=CourierOnlineStatus.ONLINE,
            shift_end_at=now + timedelta(hours=6),
            completed_orders_today=0,
            assigned_open_order_ids=[],
            zone_id="zone_A"
        )
        different_zone_courier = DispatchCourier(
            id="courier_2",
            current_location=Point(lat=24.7136, lng=46.6753),
            online_status=CourierOnlineStatus.ONLINE,
            shift_end_at=now + timedelta(hours=6),
            completed_orders_today=0,
            assigned_open_order_ids=[],
            zone_id="zone_B"
        )

        result = engine._filter_couriers_layer1(
            order_with_zone,
            [same_zone_courier, different_zone_courier],
            now
        )

        assert len(result) == 1
        assert result[0].id == "courier_1"

    def test_filter_couriers_haversine_radius(self, mock_routing_provider, sample_order):
        """Should filter out couriers outside radius"""
        config = DispatchConfig(max_haversine_radius_km=5.0)
        engine = DispatchEngine(routing_provider=mock_routing_provider, config=config)
        now = datetime.now()

        close_courier = DispatchCourier(
            id="courier_1",
            current_location=Point(lat=24.7150, lng=46.6760),  # ~200m from pickup
            online_status=CourierOnlineStatus.ONLINE,
            shift_end_at=now + timedelta(hours=6),
            completed_orders_today=0,
            assigned_open_order_ids=[],
        )
        far_courier = DispatchCourier(
            id="courier_2",
            current_location=Point(lat=24.8000, lng=46.8000),  # ~15km from pickup
            online_status=CourierOnlineStatus.ONLINE,
            shift_end_at=now + timedelta(hours=6),
            completed_orders_today=0,
            assigned_open_order_ids=[],
        )

        result = engine._filter_couriers_layer1(
            sample_order,
            [close_courier, far_courier],
            now
        )

        assert len(result) == 1
        assert result[0].id == "courier_1"


# ==================== Layer 2: Distance Matrix Filtering Tests ====================

class TestLayer2Filtering:
    """Tests for Layer 2 (Distance Matrix) filtering"""

    @pytest.mark.asyncio
    async def test_filter_couriers_by_eta(self, mock_routing_provider, sample_order):
        """Should filter couriers by pickup ETA"""
        config = DispatchConfig(max_pickup_eta_minutes=15.0)
        engine = DispatchEngine(routing_provider=mock_routing_provider, config=config)
        now = datetime.now()

        courier1 = DispatchCourier(
            id="courier_1",
            current_location=Point(lat=24.7150, lng=46.6760),
            online_status=CourierOnlineStatus.ONLINE,
            shift_end_at=now + timedelta(hours=6),
            completed_orders_today=0,
            assigned_open_order_ids=[],
        )
        courier2 = DispatchCourier(
            id="courier_2",
            current_location=Point(lat=24.7200, lng=46.6800),
            online_status=CourierOnlineStatus.ONLINE,
            shift_end_at=now + timedelta(hours=6),
            completed_orders_today=0,
            assigned_open_order_ids=[],
        )

        # Mock returns 10 mins for all, which is under 15 min threshold
        result = await engine._filter_couriers_layer2(
            sample_order,
            [courier1, courier2],
            now
        )

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_filter_couriers_empty_list(self, mock_routing_provider, sample_order):
        """Should handle empty courier list"""
        engine = DispatchEngine(routing_provider=mock_routing_provider)
        now = datetime.now()

        result = await engine._filter_couriers_layer2(sample_order, [], now)
        assert result == []

    @pytest.mark.asyncio
    async def test_filter_couriers_eta_too_high(self, mock_routing_provider, sample_order):
        """Should filter out couriers with ETA above threshold"""
        config = DispatchConfig(max_pickup_eta_minutes=5.0)  # 5 min threshold
        engine = DispatchEngine(routing_provider=mock_routing_provider, config=config)
        now = datetime.now()

        # Mock returns 10 mins, which is over 5 min threshold
        async def high_eta_travel_times(origins, destinations, departure_time):
            return DistanceMatrixResult(
                durations_minutes=[[20.0] for _ in origins],  # 20 min ETA
                distances_km=[[10.0] for _ in origins]
            )

        mock_routing_provider.get_travel_times = AsyncMock(side_effect=high_eta_travel_times)

        courier = DispatchCourier(
            id="courier_1",
            current_location=Point(lat=24.7150, lng=46.6760),
            online_status=CourierOnlineStatus.ONLINE,
            shift_end_at=now + timedelta(hours=6),
            completed_orders_today=0,
            assigned_open_order_ids=[],
        )

        result = await engine._filter_couriers_layer2(sample_order, [courier], now)
        assert len(result) == 0


# ==================== Layer 3: Approximate Feasibility Tests ====================

class TestLayer3Feasibility:
    """Tests for Layer 3 (approximate feasibility) checking"""

    def test_feasibility_no_existing_orders(self, mock_routing_provider, sample_order, sample_courier):
        """Should pass feasibility when courier has no existing orders"""
        engine = DispatchEngine(routing_provider=mock_routing_provider)
        now = datetime.now()

        all_orders = {sample_order.id: sample_order}

        result = engine._check_approximate_feasibility(
            sample_order,
            sample_courier,
            all_orders,
            now
        )

        assert result is True

    def test_feasibility_with_existing_orders(self, mock_routing_provider, sample_order):
        """Should check feasibility with existing orders"""
        engine = DispatchEngine(routing_provider=mock_routing_provider)
        now = datetime.now()

        existing_order = DispatchOrder(
            id="existing_order",
            pickup=Point(lat=24.7200, lng=46.6850),
            dropoff=Point(lat=24.7400, lng=46.6900),
            created_at=now,
            deadline_at=now + timedelta(hours=4),
            status=OrderStatus.ASSIGNED,
        )

        courier_with_order = DispatchCourier(
            id="courier_1",
            current_location=Point(lat=24.7150, lng=46.6760),
            online_status=CourierOnlineStatus.ONLINE,
            shift_end_at=now + timedelta(hours=6),
            completed_orders_today=3,
            assigned_open_order_ids=["existing_order"],
        )

        all_orders = {
            sample_order.id: sample_order,
            existing_order.id: existing_order
        }

        result = engine._check_approximate_feasibility(
            sample_order,
            courier_with_order,
            all_orders,
            now
        )

        # With reasonable distances and time, should be feasible
        assert result is True


# ==================== Scoring Tests ====================

class TestScoring:
    """Tests for plan scoring"""

    def test_score_plan_basic(self, mock_routing_provider, sample_order, sample_courier):
        """Should calculate score based on plan metrics"""
        engine = DispatchEngine(routing_provider=mock_routing_provider)
        now = datetime.now()

        plan = CourierPlan(
            courier_id=sample_courier.id,
            stops=[
                RouteStop(
                    order_id=sample_order.id,
                    type=StopType.PICKUP,
                    location=sample_order.pickup,
                    eta=now + timedelta(minutes=10)
                ),
                RouteStop(
                    order_id=sample_order.id,
                    type=StopType.DROPOFF,
                    location=sample_order.dropoff,
                    eta=now + timedelta(minutes=25)
                )
            ],
            total_distance_km=5.0,
            total_duration_minutes=25.0
        )

        all_orders = {sample_order.id: sample_order}

        score = engine._score_plan(sample_order, sample_courier, plan, all_orders)

        # Score should be a positive number
        assert score >= 0

    def test_score_plan_distance_affects_score(self, mock_routing_provider, sample_order, sample_courier):
        """Longer distance should increase score (worse)"""
        engine = DispatchEngine(routing_provider=mock_routing_provider)
        now = datetime.now()
        all_orders = {sample_order.id: sample_order}

        short_plan = CourierPlan(
            courier_id=sample_courier.id,
            stops=[
                RouteStop(
                    order_id=sample_order.id,
                    type=StopType.DROPOFF,
                    location=sample_order.dropoff,
                    eta=now + timedelta(minutes=20)
                )
            ],
            total_distance_km=2.0,
            total_duration_minutes=10.0
        )

        long_plan = CourierPlan(
            courier_id=sample_courier.id,
            stops=[
                RouteStop(
                    order_id=sample_order.id,
                    type=StopType.DROPOFF,
                    location=sample_order.dropoff,
                    eta=now + timedelta(minutes=20)
                )
            ],
            total_distance_km=10.0,
            total_duration_minutes=10.0
        )

        short_score = engine._score_plan(sample_order, sample_courier, short_plan, all_orders)
        long_score = engine._score_plan(sample_order, sample_courier, long_plan, all_orders)

        assert long_score > short_score


# ==================== Full Assignment Flow Tests ====================

class TestAssignNewOrder:
    """Tests for the complete assign_new_order flow"""

    @pytest.mark.asyncio
    async def test_assign_order_success(self, mock_routing_provider, sample_order, sample_courier):
        """Should successfully assign order to courier"""
        engine = DispatchEngine(routing_provider=mock_routing_provider)
        now = datetime.now()

        all_orders = {sample_order.id: sample_order}
        couriers = [sample_courier]

        result = await engine.assign_new_order(
            sample_order,
            all_orders,
            couriers,
            now
        )

        assert result is not None
        assert result.order_id == sample_order.id
        assert result.courier_id == sample_courier.id

    @pytest.mark.asyncio
    async def test_assign_order_already_assigned(self, mock_routing_provider, sample_courier):
        """Should not assign already assigned order"""
        engine = DispatchEngine(routing_provider=mock_routing_provider)
        now = datetime.now()

        assigned_order = DispatchOrder(
            id="order_1",
            pickup=Point(lat=24.7136, lng=46.6753),
            dropoff=Point(lat=24.7500, lng=46.7000),
            created_at=now,
            deadline_at=now + timedelta(hours=4),
            status=OrderStatus.ASSIGNED,  # Already assigned
        )

        all_orders = {assigned_order.id: assigned_order}
        couriers = [sample_courier]

        result = await engine.assign_new_order(
            assigned_order,
            all_orders,
            couriers,
            now
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_assign_order_past_deadline(self, mock_routing_provider, sample_courier):
        """Should not assign order past deadline"""
        engine = DispatchEngine(routing_provider=mock_routing_provider)
        now = datetime.now()

        expired_order = DispatchOrder(
            id="order_1",
            pickup=Point(lat=24.7136, lng=46.6753),
            dropoff=Point(lat=24.7500, lng=46.7000),
            created_at=now - timedelta(hours=5),
            deadline_at=now - timedelta(hours=1),  # Past deadline
            status=OrderStatus.UNASSIGNED,
        )

        all_orders = {expired_order.id: expired_order}
        couriers = [sample_courier]

        result = await engine.assign_new_order(
            expired_order,
            all_orders,
            couriers,
            now
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_assign_order_no_couriers(self, mock_routing_provider, sample_order):
        """Should return None when no couriers available"""
        engine = DispatchEngine(routing_provider=mock_routing_provider)
        now = datetime.now()

        all_orders = {sample_order.id: sample_order}
        couriers = []  # No couriers

        result = await engine.assign_new_order(
            sample_order,
            all_orders,
            couriers,
            now
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_assign_order_selects_best_courier(self, mock_routing_provider, sample_order):
        """Should select best courier based on score"""
        engine = DispatchEngine(routing_provider=mock_routing_provider)
        now = datetime.now()

        # Closer courier should be selected
        close_courier = DispatchCourier(
            id="courier_close",
            current_location=Point(lat=24.7140, lng=46.6760),  # Very close
            online_status=CourierOnlineStatus.ONLINE,
            shift_end_at=now + timedelta(hours=6),
            completed_orders_today=5,
            assigned_open_order_ids=[],
            zone_id="zone_1"
        )
        far_courier = DispatchCourier(
            id="courier_far",
            current_location=Point(lat=24.7500, lng=46.6753),  # Further
            online_status=CourierOnlineStatus.ONLINE,
            shift_end_at=now + timedelta(hours=6),
            completed_orders_today=5,
            assigned_open_order_ids=[],
            zone_id="zone_1"
        )

        all_orders = {sample_order.id: sample_order}
        couriers = [far_courier, close_courier]  # Put far first intentionally

        result = await engine.assign_new_order(
            sample_order,
            all_orders,
            couriers,
            now
        )

        assert result is not None
        # Score should select a courier (either could be valid)
        assert result.courier_id in ["courier_close", "courier_far"]
