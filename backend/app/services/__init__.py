"""Services Package

This module exports all service instances for easy import.
"""

from app.services.user_service import UserService, user_service

__all__ = [
    "UserService",
    "user_service",
]
