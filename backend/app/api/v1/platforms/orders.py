"""
Platform Orders API
Endpoints for fetching and syncing orders from external platforms.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.platforms.base import PlatformOrder, PlatformType
from app.services.platforms.order_sync import order_sync_service

router = APIRouter(prefix="/platforms", tags=["Platform Orders"])


# ==================== Schemas ====================


class PlatformOrderResponse(BaseModel):
    """Response schema for platform orders"""
    platform: str
    platform_order_id: str
    platform_tracking_number: Optional[str] = None
    platform_driver_id: Optional[str] = None
    courier_barq_id: Optional[str] = None
    status: str
    order_type: Optional[str] = None
    pickup_address: str
    delivery_address: str
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    order_amount: float = 0
    cod_amount: float = 0
    delivery_fee: float = 0
    created_at: datetime
    assigned_at: Optional[datetime] = None
    picked_up_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    notes: Optional[str] = None
    items_count: int = 0

    class Config:
        from_attributes = True


class CourierOrdersResponse(BaseModel):
    """Response for fetching courier orders"""
    courier_id: int
    courier_barq_id: Optional[str] = None
    platforms: Dict[str, List[PlatformOrderResponse]]
    total_orders: int


class SyncRequest(BaseModel):
    """Request schema for sync operation"""
    courier_id: Optional[int] = None
    platforms: Optional[List[str]] = Field(None, description="Platforms to sync: barq, jahez, saned")
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None


class SyncResponse(BaseModel):
    """Response schema for sync operation"""
    total: Dict[str, int]
    by_courier: Dict[int, Dict[str, int]]
    couriers_processed: int


class PlatformHealthResponse(BaseModel):
    """Response schema for platform health check"""
    platform: str
    base_url: str
    authenticated: bool
    token_valid: bool
    request_count: int
    error_count: int
    last_request: Optional[str] = None


# ==================== Helper Functions ====================


def convert_platform_order(order: PlatformOrder) -> PlatformOrderResponse:
    """Convert PlatformOrder to response schema."""
    return PlatformOrderResponse(
        platform=order.platform if isinstance(order.platform, str) else order.platform.value,
        platform_order_id=order.platform_order_id,
        platform_tracking_number=order.platform_tracking_number,
        platform_driver_id=order.platform_driver_id,
        courier_barq_id=order.courier_barq_id,
        status=order.status if isinstance(order.status, str) else order.status.value,
        order_type=order.order_type,
        pickup_address=order.pickup_address,
        delivery_address=order.delivery_address,
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        order_amount=float(order.order_amount),
        cod_amount=float(order.cod_amount),
        delivery_fee=float(order.delivery_fee),
        created_at=order.created_at,
        assigned_at=order.assigned_at,
        picked_up_at=order.picked_up_at,
        delivered_at=order.delivered_at,
        notes=order.notes,
        items_count=order.items_count,
    )


def parse_platforms(platforms_str: Optional[str]) -> Optional[List[PlatformType]]:
    """Parse platform string to list of PlatformType."""
    if not platforms_str:
        return None
    platform_map = {
        "barq": PlatformType.BARQ,
        "jahez": PlatformType.JAHEZ,
        "saned": PlatformType.SANED,
    }
    platforms = []
    for p in platforms_str.split(","):
        p = p.strip().lower()
        if p in platform_map:
            platforms.append(platform_map[p])
    return platforms if platforms else None


# ==================== Endpoints ====================


@router.get("/health", response_model=Dict[str, PlatformHealthResponse])
async def get_platform_health(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get health status of all platform connections.

    Returns connection status, authentication state, and request statistics.
    """
    health = order_sync_service.get_platform_health()
    return health


@router.get("/orders/courier/{courier_id}", response_model=CourierOrdersResponse)
async def get_courier_orders(
    courier_id: int,
    platforms: Optional[str] = Query(None, description="Comma-separated platforms: barq,jahez,saned"),
    from_date: Optional[datetime] = Query(None, description="Start date filter"),
    to_date: Optional[datetime] = Query(None, description="End date filter"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CourierOrdersResponse:
    """
    Fetch orders for a specific courier from external platforms.

    This endpoint fetches real-time order data from configured platforms
    (BARQ, Jahez, Saned) for the specified courier.
    """
    # Parse platforms
    platform_list = parse_platforms(platforms)

    # Default date range: last 7 days
    if not from_date:
        from_date = datetime.utcnow() - timedelta(days=7)
    if not to_date:
        to_date = datetime.utcnow()

    # Fetch orders
    orders_by_platform = order_sync_service.fetch_orders_for_courier(
        db,
        courier_id=courier_id,
        platforms=platform_list,
        from_date=from_date,
        to_date=to_date,
    )

    # Convert to response format
    platforms_response = {}
    total_orders = 0
    courier_barq_id = None

    for platform, orders in orders_by_platform.items():
        platforms_response[platform] = [convert_platform_order(o) for o in orders]
        total_orders += len(orders)
        if orders and orders[0].courier_barq_id:
            courier_barq_id = orders[0].courier_barq_id

    return CourierOrdersResponse(
        courier_id=courier_id,
        courier_barq_id=courier_barq_id,
        platforms=platforms_response,
        total_orders=total_orders,
    )


@router.get("/orders", response_model=Dict[int, Dict[str, List[PlatformOrderResponse]]])
async def get_all_orders(
    platforms: Optional[str] = Query(None, description="Comma-separated platforms: barq,jahez,saned"),
    from_date: Optional[datetime] = Query(None, description="Start date filter"),
    to_date: Optional[datetime] = Query(None, description="End date filter"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[int, Dict[str, List[PlatformOrderResponse]]]:
    """
    Fetch orders for all active couriers from external platforms.

    Returns orders grouped by courier ID and platform.
    """
    # Get organization from current user
    organization_id = getattr(current_user, "organization_id", None)

    # Parse platforms
    platform_list = parse_platforms(platforms)

    # Default date range
    if not from_date:
        from_date = datetime.utcnow() - timedelta(days=7)
    if not to_date:
        to_date = datetime.utcnow()

    # Fetch all orders
    all_orders = order_sync_service.fetch_all_courier_orders(
        db,
        organization_id=organization_id,
        platforms=platform_list,
        from_date=from_date,
        to_date=to_date,
    )

    # Convert to response format
    result = {}
    for courier_id, platform_orders in all_orders.items():
        result[courier_id] = {}
        for platform, orders in platform_orders.items():
            result[courier_id][platform] = [convert_platform_order(o) for o in orders]

    return result


@router.post("/sync", response_model=SyncResponse)
async def sync_orders(
    request: SyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SyncResponse:
    """
    Sync orders from external platforms to the local database.

    This will fetch orders from configured platforms and create/update
    delivery records in the local database.
    """
    # Get organization from current user
    organization_id = getattr(current_user, "organization_id", None)

    # Parse platforms
    platform_list = None
    if request.platforms:
        platform_map = {
            "barq": PlatformType.BARQ,
            "jahez": PlatformType.JAHEZ,
            "saned": PlatformType.SANED,
        }
        platform_list = [platform_map[p.lower()] for p in request.platforms if p.lower() in platform_map]

    # Default date range
    from_date = request.from_date or (datetime.utcnow() - timedelta(days=7))
    to_date = request.to_date or datetime.utcnow()

    # Perform sync
    if request.courier_id:
        # Sync single courier
        orders_by_platform = order_sync_service.fetch_orders_for_courier(
            db,
            courier_id=request.courier_id,
            platforms=platform_list,
            from_date=from_date,
            to_date=to_date,
        )

        # Flatten orders
        all_orders = []
        for orders in orders_by_platform.values():
            all_orders.extend(orders)

        stats = order_sync_service.sync_orders_to_db(
            db,
            courier_id=request.courier_id,
            orders=all_orders,
            organization_id=organization_id,
        )

        return SyncResponse(
            total=stats,
            by_courier={request.courier_id: stats},
            couriers_processed=1,
        )
    else:
        # Full sync
        result = order_sync_service.full_sync(
            db,
            organization_id=organization_id,
            platforms=platform_list,
            from_date=from_date,
            to_date=to_date,
        )

        return SyncResponse(
            total=result["total"],
            by_courier=result["by_courier"],
            couriers_processed=result["couriers_processed"],
        )


@router.get("/couriers", response_model=List[Dict[str, Any]])
async def get_couriers_with_platform_ids(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """
    Get all active couriers with their platform IDs.

    Returns a list of couriers showing which platforms they are configured for.
    """
    organization_id = getattr(current_user, "organization_id", None)

    couriers = order_sync_service.get_courier_platform_ids(
        db,
        organization_id=organization_id,
    )

    # Add platform availability flags
    for courier in couriers:
        courier["platforms"] = {
            "barq": bool(courier.get("barq_id")),
            "jahez": bool(courier.get("jahez_driver_id")),
            "saned": bool(courier.get("jahez_driver_id")),  # Saned uses same ID
            "hunger": bool(courier.get("hunger_rider_id")),
            "mrsool": bool(courier.get("mrsool_courier_id")),
        }

    return couriers


@router.get("/orders/order/{platform}/{order_id}", response_model=PlatformOrderResponse)
async def get_order_details(
    platform: str,
    order_id: str,
    current_user: User = Depends(get_current_user),
) -> PlatformOrderResponse:
    """
    Get detailed information for a specific order from a platform.

    Args:
        platform: Platform name (barq, jahez, saned)
        order_id: Platform-specific order ID
    """
    platform = platform.lower()

    if platform == "barq":
        order = order_sync_service.barq_client.get_order_details(order_id)
    elif platform == "jahez":
        order = order_sync_service.jahez_client.get_order_details(order_id)
    elif platform == "saned":
        order = order_sync_service.saned_client.get_order_details(order_id)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown platform: {platform}")

    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found on {platform}")

    return convert_platform_order(order)
