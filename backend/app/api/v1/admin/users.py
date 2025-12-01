"""Admin Users Management API"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.deps import get_db, get_current_superuser
from app.models.user import User
from app.models.role import Role, user_roles
from app.models.audit_log import AuditLog
from app.schemas.user import User as UserSchema, UserUpdate
from app.schemas.role import RoleResponse
from app.schemas.audit_log import AuditLogResponse

router = APIRouter()


@router.get("/", response_model=List[UserSchema])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    is_superuser: Optional[bool] = Query(None),
    role_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    List all users with optional filtering.

    Requires superuser permission.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **is_active**: Filter by active status
    - **is_superuser**: Filter by superuser status
    - **role_id**: Filter by assigned role
    - **search**: Search in email and full_name
    """
    query = db.query(User)

    # Apply filters
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    if is_superuser is not None:
        query = query.filter(User.is_superuser == is_superuser)

    if role_id is not None:
        query = query.join(User.roles).filter(Role.id == role_id)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (User.email.ilike(search_pattern)) |
            (User.full_name.ilike(search_pattern))
        )

    # Order by email and apply pagination
    users = query.order_by(User.email).offset(skip).limit(limit).all()

    return users


@router.get("/{user_id}", response_model=UserSchema)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get a specific user by ID.

    Requires superuser permission.

    Returns detailed user information including roles.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return user


@router.patch("/{user_id}", response_model=UserSchema)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Update a user.

    Requires superuser permission.

    Allows updating user's email, full_name, role, and status.
    Note: Password updates should use a separate endpoint for security.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    # Prevent user from deactivating themselves
    if user.id == current_user.id and hasattr(user_in, 'is_active') and user_in.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )

    # Update fields
    update_data = user_in.model_dump(exclude_unset=True, exclude={'password'})
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user


@router.post("/{user_id}/deactivate", response_model=UserSchema)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Deactivate a user account.

    Requires superuser permission.

    Deactivated users cannot log in but their data is preserved.
    This is preferred over deletion for audit trail purposes.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    # Prevent user from deactivating themselves
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )

    # Prevent deactivating the last superuser
    if user.is_superuser:
        active_superusers_count = db.query(User).filter(
            User.is_superuser == True,
            User.is_active == True
        ).count()
        if active_superusers_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate the last active superuser"
            )

    user.is_active = False
    db.commit()
    db.refresh(user)

    return user


@router.post("/{user_id}/activate", response_model=UserSchema)
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Activate a deactivated user account.

    Requires superuser permission.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    user.is_active = True
    db.commit()
    db.refresh(user)

    return user


@router.get("/{user_id}/roles", response_model=List[RoleResponse])
def get_user_roles(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get all roles assigned to a user.

    Requires superuser permission.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    return user.roles


@router.post("/{user_id}/roles", response_model=UserSchema)
def assign_roles_to_user(
    user_id: int,
    role_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Assign roles to a user (replaces existing role assignments).

    Requires superuser permission.

    - **role_ids**: List of role IDs to assign to the user
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    # Validate role IDs
    roles = db.query(Role).filter(
        Role.id.in_(role_ids),
        Role.is_active == True
    ).all()
    if len(roles) != len(role_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more role IDs are invalid or inactive"
        )

    # Replace roles
    user.roles = roles
    db.commit()
    db.refresh(user)

    return user


@router.get("/{user_id}/activity", response_model=List[AuditLogResponse])
def get_user_activity_logs(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get activity logs for a specific user.

    Requires superuser permission.

    Returns all audit logs for actions performed by this user,
    ordered by most recent first.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    logs = (
        db.query(AuditLog)
        .filter(AuditLog.user_id == user_id)
        .order_by(desc(AuditLog.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    return logs


@router.delete("/{user_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_role_from_user(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Remove a specific role from a user.

    Requires superuser permission.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with id {role_id} not found"
        )

    # Check if user has this role
    if role not in user.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have this role"
        )

    # Remove role
    user.roles.remove(role)
    db.commit()

    return None
