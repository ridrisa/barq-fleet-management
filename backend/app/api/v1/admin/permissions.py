"""Admin Permissions Management API"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_superuser
from app.models.user import User
from app.models.role import Permission
from app.schemas.role import (
    PermissionResponse,
    PermissionCreate,
    PermissionUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[PermissionResponse])
def list_permissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    resource: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    List all permissions with optional filtering.

    Requires superuser permission.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **resource**: Filter by resource type (e.g., "courier", "vehicle")
    - **action**: Filter by action type (e.g., "create", "read", "update")
    - **search**: Search in name and description
    """
    query = db.query(Permission)

    # Apply filters
    if resource:
        query = query.filter(Permission.resource == resource)

    if action:
        query = query.filter(Permission.action == action)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Permission.name.ilike(search_pattern)) |
            (Permission.description.ilike(search_pattern))
        )

    # Order by resource, then action, and apply pagination
    permissions = query.order_by(
        Permission.resource,
        Permission.action
    ).offset(skip).limit(limit).all()

    return permissions


@router.get("/{permission_id}", response_model=PermissionResponse)
def get_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get a specific permission by ID.

    Requires superuser permission.
    """
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission with id {permission_id} not found"
        )
    return permission


@router.post("/", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
def create_permission(
    permission_in: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Create a new permission.

    Requires superuser permission.

    Note: This endpoint is typically only used during initial system setup or
    when adding new resources/features. Most systems have predefined permissions.

    - **name**: Unique permission identifier (format: "resource:action")
    - **resource**: Resource type (e.g., "courier", "vehicle")
    - **action**: Action type (e.g., "create", "read", "update", "delete")
    - **description**: Optional human-readable description
    """
    # Check if permission with same name already exists
    existing_permission = db.query(Permission).filter(
        Permission.name == permission_in.name
    ).first()
    if existing_permission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Permission with name '{permission_in.name}' already exists"
        )

    # Validate name format (should be "resource:action")
    if ":" not in permission_in.name or permission_in.name.count(":") != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission name must follow format 'resource:action'"
        )

    # Create permission
    permission = Permission(
        name=permission_in.name,
        resource=permission_in.resource,
        action=permission_in.action,
        description=permission_in.description,
    )

    db.add(permission)
    db.commit()
    db.refresh(permission)

    return permission


@router.patch("/{permission_id}", response_model=PermissionResponse)
def update_permission(
    permission_id: int,
    permission_in: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Update a permission's description.

    Requires superuser permission.

    Note: Only the description can be updated. The name, resource, and action
    are immutable to maintain system integrity.
    """
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission with id {permission_id} not found"
        )

    # Update only the description
    update_data = permission_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(permission, field, value)

    db.commit()
    db.refresh(permission)

    return permission


@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Delete a permission.

    Requires superuser permission.

    Note: Use with extreme caution. Deleting permissions can break role
    assignments and affect system security. Only delete permissions that
    are no longer needed and not assigned to any roles.
    """
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission with id {permission_id} not found"
        )

    # Check if permission is assigned to any roles
    if permission.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete permission. It is assigned to {len(permission.roles)} role(s)"
        )

    db.delete(permission)
    db.commit()

    return None


@router.get("/resources/list", response_model=List[str])
def list_resources(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get a list of all unique resource types.

    Requires superuser permission.

    Useful for UI dropdowns and filtering.
    """
    resources = db.query(Permission.resource).distinct().order_by(Permission.resource).all()
    return [r[0] for r in resources]


@router.get("/actions/list", response_model=List[str])
def list_actions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get a list of all unique action types.

    Requires superuser permission.

    Useful for UI dropdowns and filtering.
    """
    actions = db.query(Permission.action).distinct().order_by(Permission.action).all()
    return [a[0] for a in actions]
