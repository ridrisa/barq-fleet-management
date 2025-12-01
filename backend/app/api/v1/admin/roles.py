"""Admin Roles Management API"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_superuser
from app.models.user import User
from app.models.role import Role, Permission, role_permissions
from app.schemas.role import (
    RoleResponse,
    RoleCreate,
    RoleUpdate,
    PermissionResponse,
)

router = APIRouter()


@router.get("/", response_model=List[RoleResponse])
def list_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    List all roles with optional filtering.

    Requires superuser permission.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **is_active**: Filter by active status
    - **search**: Search in name and display_name
    """
    query = db.query(Role)

    # Apply filters
    if is_active is not None:
        query = query.filter(Role.is_active == is_active)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Role.name.ilike(search_pattern)) |
            (Role.display_name.ilike(search_pattern))
        )

    # Order by name and apply pagination
    roles = query.order_by(Role.name).offset(skip).limit(limit).all()
    return roles


@router.get("/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get a specific role by ID.

    Requires superuser permission.
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with id {role_id} not found"
        )
    return role


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    role_in: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Create a new role.

    Requires superuser permission.

    - **name**: Unique role identifier (lowercase, no spaces)
    - **display_name**: Human-readable role name
    - **description**: Optional role description
    - **permission_ids**: List of permission IDs to assign to this role
    """
    # Check if role with same name already exists
    existing_role = db.query(Role).filter(Role.name == role_in.name).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role with name '{role_in.name}' already exists"
        )

    # Validate permission IDs
    if role_in.permission_ids:
        permissions = db.query(Permission).filter(
            Permission.id.in_(role_in.permission_ids)
        ).all()
        if len(permissions) != len(role_in.permission_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more permission IDs are invalid"
            )

    # Create role
    role = Role(
        name=role_in.name,
        display_name=role_in.display_name,
        description=role_in.description,
        is_active=role_in.is_active,
        is_system_role=False,
    )

    # Assign permissions
    if role_in.permission_ids:
        permissions = db.query(Permission).filter(
            Permission.id.in_(role_in.permission_ids)
        ).all()
        role.permissions = permissions

    db.add(role)
    db.commit()
    db.refresh(role)

    return role


@router.patch("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    role_in: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Update an existing role.

    Requires superuser permission.
    System roles cannot be deactivated.
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with id {role_id} not found"
        )

    # Prevent deactivating system roles
    if role.is_system_role and role_in.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate system roles"
        )

    # Update fields
    update_data = role_in.model_dump(exclude_unset=True)

    # Handle permission_ids separately
    if "permission_ids" in update_data:
        permission_ids = update_data.pop("permission_ids")
        if permission_ids is not None:
            permissions = db.query(Permission).filter(
                Permission.id.in_(permission_ids)
            ).all()
            if len(permissions) != len(permission_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more permission IDs are invalid"
                )
            role.permissions = permissions

    # Apply other updates
    for field, value in update_data.items():
        setattr(role, field, value)

    db.commit()
    db.refresh(role)

    return role


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Delete a role.

    Requires superuser permission.
    System roles cannot be deleted.
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with id {role_id} not found"
        )

    # Prevent deleting system roles
    if role.is_system_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete system roles"
        )

    # Check if role is assigned to any users
    if role.users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete role. It is assigned to {len(role.users)} user(s)"
        )

    db.delete(role)
    db.commit()

    return None


@router.get("/{role_id}/permissions", response_model=List[PermissionResponse])
def get_role_permissions(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get all permissions assigned to a role.

    Requires superuser permission.
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with id {role_id} not found"
        )

    return role.permissions


@router.post("/{role_id}/permissions", response_model=RoleResponse)
def assign_permissions_to_role(
    role_id: int,
    permission_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Assign permissions to a role (replaces existing permissions).

    Requires superuser permission.

    - **permission_ids**: List of permission IDs to assign
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with id {role_id} not found"
        )

    # Validate permission IDs
    permissions = db.query(Permission).filter(
        Permission.id.in_(permission_ids)
    ).all()
    if len(permissions) != len(permission_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more permission IDs are invalid"
        )

    # Replace permissions
    role.permissions = permissions
    db.commit()
    db.refresh(role)

    return role
