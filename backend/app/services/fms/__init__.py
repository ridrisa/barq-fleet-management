"""
FMS (Fleet Management System) Integration
Provides integration with machinettalk FMS for GPS tracking and fleet monitoring.
"""

from app.services.fms.client import FMSClient, get_fms_client

__all__ = ["FMSClient", "get_fms_client"]
