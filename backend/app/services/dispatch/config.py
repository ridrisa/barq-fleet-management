"""
Dispatch Configuration
"""

from dataclasses import dataclass, field


@dataclass
class PenaltyWeights:
    """Weights for scoring courier-order assignments"""
    distance: float = 1.0       # Weight for total distance
    sla: float = 5.0            # Weight for SLA slack (time buffer)
    fairness: float = 1.0       # Weight for load balancing
    overload: float = 4.0       # Penalty for exceeding target load


@dataclass
class DispatchConfig:
    """Configuration for the dispatch engine"""

    # Layer 1 - Haversine radius filter
    max_haversine_radius_km: float = 7.0

    # Layer 2 - Maximum ETA to pickup
    max_pickup_eta_minutes: float = 15.0

    # Speed assumptions
    average_speed_kmh: float = 25.0  # Average city driving speed

    # SLA settings
    sla_hours: float = 4.0           # Order deadline (hours from creation)
    sla_buffer_minutes: float = 15.0  # Internal safety buffer

    # Load balancing
    target_orders_per_courier_per_day: int = 15

    # Scoring penalties
    penalties: PenaltyWeights = field(default_factory=PenaltyWeights)

    # API timeouts
    routing_timeout_seconds: float = 30.0

    # Caching
    cache_ttl_minutes: int = 20


# Default configuration instance
DEFAULT_DISPATCH_CONFIG = DispatchConfig()
