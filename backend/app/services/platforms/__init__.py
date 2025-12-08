"""
Platform Integration Services
Handles order fetching from external delivery platforms (BARQ, Jahez, Saned)
"""

from app.services.platforms.base import BasePlatformClient, PlatformOrder, PlatformType
from app.services.platforms.barq_client import BarqClient, get_barq_client
from app.services.platforms.jahez_client import JahezClient, get_jahez_client
from app.services.platforms.order_sync import OrderSyncService, order_sync_service

__all__ = [
    "BasePlatformClient",
    "PlatformOrder",
    "PlatformType",
    "BarqClient",
    "get_barq_client",
    "JahezClient",
    "get_jahez_client",
    "OrderSyncService",
    "order_sync_service",
]
