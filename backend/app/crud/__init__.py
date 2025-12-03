"""
CRUD Module - Database Operations

This module provides CRUD (Create, Read, Update, Delete) operations for all models.

Base Classes:
    - CRUDBase: Standard CRUD operations without tenant isolation
    - TenantAwareCRUD: CRUD operations with automatic organization filtering

Usage:
    from app.crud import CRUDBase, TenantAwareCRUD

    # Standard CRUD (for global tables like users, roles)
    class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
        pass

    # Tenant-aware CRUD (for organization-scoped tables)
    class CRUDCourier(TenantAwareCRUD[Courier, CourierCreate, CourierUpdate]):
        pass
"""
from app.crud.base import CRUDBase
from app.crud.tenant_crud import TenantAwareCRUD, TenantCRUD
from app.crud.user import crud_user

__all__ = [
    "CRUDBase",
    "TenantAwareCRUD",
    "TenantCRUD",
    "crud_user",
]
