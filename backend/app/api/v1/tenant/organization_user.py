"""
Organization User API Endpoints

Manage organization memberships and user roles.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_active_user
from app.models.user import User
from app.models.tenant.organization_user import OrganizationRole
from app.schemas.tenant.organization_user import (
    OrganizationUserCreate,
    OrganizationUserUpdate,
    OrganizationUserResponse,
    OrganizationUserWithDetails,
)
from app.services.tenant.organization_user_service import organization_user_service
from app.services.tenant.organization_service import organization_service

router = APIRouter()


@router.get("/{organization_id}/members", response_model=List[OrganizationUserWithDetails])
def list_organization_members(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: bool = Query(None),
):
    """
    List all members of an organization.

    Requires membership in the organization or superuser.
    """
    # Check access
    if not current_user.is_superuser:
        if not organization_user_service.is_member(db, organization_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a member of this organization"
            )

    memberships = organization_user_service.get_by_organization(
        db, organization_id, skip=skip, limit=limit, is_active=is_active
    )

    # Enrich with user and organization details
    result = []
    for m in memberships:
        user = db.query(User).filter(User.id == m.user_id).first()
        org = organization_service.get(db, m.organization_id)

        result.append(OrganizationUserWithDetails(
            id=m.id,
            organization_id=m.organization_id,
            user_id=m.user_id,
            role=m.role,
            permissions=m.permissions,
            is_active=m.is_active,
            created_at=m.created_at,
            updated_at=m.updated_at,
            user_email=user.email if user else None,
            user_full_name=user.full_name if user else None,
            organization_name=org.name if org else None,
            organization_slug=org.slug if org else None,
        ))

    return result


@router.post("/{organization_id}/members", response_model=OrganizationUserResponse, status_code=status.HTTP_201_CREATED)
def add_organization_member(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int,
    member_in: OrganizationUserCreate,
):
    """
    Add a user to an organization.

    Requires OWNER or ADMIN role.
    """
    # Check access
    if not current_user.is_superuser:
        role = organization_user_service.get_user_role(db, organization_id, current_user.id)
        if role not in [OrganizationRole.OWNER, OrganizationRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owners and admins can add members"
            )

        # Admins cannot add owners
        if member_in.role == OrganizationRole.OWNER and role != OrganizationRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owners can add other owners"
            )

    return organization_user_service.add_user(db, organization_id=organization_id, obj_in=member_in)


@router.get("/{organization_id}/members/{user_id}", response_model=OrganizationUserWithDetails)
def get_organization_member(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int,
    user_id: int,
):
    """
    Get a specific member's details.

    Requires membership in the organization.
    """
    # Check access
    if not current_user.is_superuser:
        if not organization_user_service.is_member(db, organization_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a member of this organization"
            )

    # Get membership
    memberships = organization_user_service.get_by_organization(db, organization_id)
    membership = next((m for m in memberships if m.user_id == user_id), None)

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in this organization"
        )

    # Enrich with details
    user = db.query(User).filter(User.id == user_id).first()
    org = organization_service.get(db, organization_id)

    return OrganizationUserWithDetails(
        id=membership.id,
        organization_id=membership.organization_id,
        user_id=membership.user_id,
        role=membership.role,
        permissions=membership.permissions,
        is_active=membership.is_active,
        created_at=membership.created_at,
        updated_at=membership.updated_at,
        user_email=user.email if user else None,
        user_full_name=user.full_name if user else None,
        organization_name=org.name if org else None,
        organization_slug=org.slug if org else None,
    )


@router.put("/{organization_id}/members/{user_id}", response_model=OrganizationUserResponse)
def update_organization_member(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int,
    user_id: int,
    member_in: OrganizationUserUpdate,
):
    """
    Update a member's role or status.

    Requires OWNER or ADMIN role.
    """
    # Check access
    if not current_user.is_superuser:
        role = organization_user_service.get_user_role(db, organization_id, current_user.id)
        if role not in [OrganizationRole.OWNER, OrganizationRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owners and admins can update members"
            )

        # Cannot modify your own role
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify your own membership"
            )

        # Admins cannot promote to owner
        if member_in.role == OrganizationRole.OWNER and role != OrganizationRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owners can promote to owner role"
            )

    return organization_user_service.update_role(db, organization_id, user_id, member_in)


@router.delete("/{organization_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_organization_member(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int,
    user_id: int,
):
    """
    Remove a member from an organization.

    Requires OWNER or ADMIN role.
    Users can remove themselves (leave organization).
    """
    # Users can leave on their own
    if user_id == current_user.id:
        organization_user_service.remove_user(db, organization_id, user_id)
        return None

    # Check access for removing others
    if not current_user.is_superuser:
        role = organization_user_service.get_user_role(db, organization_id, current_user.id)
        if role not in [OrganizationRole.OWNER, OrganizationRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owners and admins can remove members"
            )

        # Admins cannot remove owners
        target_role = organization_user_service.get_user_role(db, organization_id, user_id)
        if target_role == OrganizationRole.OWNER and role != OrganizationRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owners can remove other owners"
            )

    organization_user_service.remove_user(db, organization_id, user_id)
    return None


@router.post("/{organization_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
def leave_organization(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int,
):
    """
    Leave an organization.

    Cannot leave if you're the last owner.
    """
    organization_user_service.remove_user(db, organization_id, current_user.id)
    return None
