"""
Organization API Endpoints

CRUD operations for multi-tenant organization management.
Requires appropriate roles for modifications.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_active_user,
    get_current_organization,
    get_db,
)
from app.models.tenant.organization import Organization
from app.models.tenant.organization_user import OrganizationRole
from app.models.user import User
from app.schemas.tenant.organization import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
    OrganizationWithStats,
    SubscriptionUpgrade,
)
from app.services.tenant.organization_service import organization_service
from app.services.tenant.organization_user_service import organization_user_service

router = APIRouter()


@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    org_in: OrganizationCreate,
):
    """
    Create a new organization.

    The current user will be assigned as OWNER of the new organization.
    """
    # Only superusers can create new organizations (or first organization for new users)
    if not current_user.is_superuser:
        # Check if user already has organizations
        existing_orgs = organization_user_service.get_by_user(db, current_user.id)
        if existing_orgs:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can create additional organizations",
            )

    # Create organization
    org = organization_service.create_organization(db, obj_in=org_in)

    # Add current user as owner
    from app.schemas.tenant.organization_user import OrganizationUserCreate

    org_user_in = OrganizationUserCreate(
        user_id=current_user.id,
        role=OrganizationRole.OWNER,
    )
    organization_user_service.add_user(db, organization_id=org.id, obj_in=org_user_in)

    return org


@router.get("/", response_model=List[OrganizationResponse])
def list_organizations(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """
    List organizations the current user belongs to.

    Superusers see all organizations.
    """
    if current_user.is_superuser:
        # Superusers can see all organizations
        return organization_service.get_multi(db, skip=skip, limit=limit)

    # Regular users only see their organizations
    memberships = organization_user_service.get_by_user(
        db, current_user.id, is_active=True, skip=skip, limit=limit
    )
    return [m.organization for m in memberships if m.organization]


@router.get("/current", response_model=OrganizationWithStats)
def get_current_organization_details(
    *,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
):
    """
    Get current organization details with statistics.
    """
    stats = organization_service.get_statistics(db, current_org.id)

    return OrganizationWithStats(
        id=current_org.id,
        name=current_org.name,
        slug=current_org.slug,
        is_active=current_org.is_active,
        subscription_plan=current_org.subscription_plan,
        subscription_status=current_org.subscription_status,
        max_users=current_org.max_users,
        max_couriers=current_org.max_couriers,
        max_vehicles=current_org.max_vehicles,
        trial_ends_at=current_org.trial_ends_at,
        settings=current_org.settings,
        created_at=current_org.created_at,
        updated_at=current_org.updated_at,
        user_count=stats["user_count"],
        courier_count=stats["courier_count"],
        vehicle_count=stats["vehicle_count"],
    )


@router.get("/{organization_id}", response_model=OrganizationWithStats)
def get_organization(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int,
):
    """
    Get organization by ID.

    User must be a member or superuser.
    """
    org = organization_service.get(db, organization_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    # Check access
    if not current_user.is_superuser:
        if not organization_user_service.is_member(db, organization_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this organization"
            )

    stats = organization_service.get_statistics(db, organization_id)

    return OrganizationWithStats(
        id=org.id,
        name=org.name,
        slug=org.slug,
        is_active=org.is_active,
        subscription_plan=org.subscription_plan,
        subscription_status=org.subscription_status,
        max_users=org.max_users,
        max_couriers=org.max_couriers,
        max_vehicles=org.max_vehicles,
        trial_ends_at=org.trial_ends_at,
        settings=org.settings,
        created_at=org.created_at,
        updated_at=org.updated_at,
        user_count=stats["user_count"],
        courier_count=stats["courier_count"],
        vehicle_count=stats["vehicle_count"],
    )


@router.put("/{organization_id}", response_model=OrganizationResponse)
def update_organization(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int,
    org_in: OrganizationUpdate,
):
    """
    Update organization.

    Requires OWNER or ADMIN role, or superuser.
    """
    org = organization_service.get(db, organization_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    # Check access
    if not current_user.is_superuser:
        role = organization_user_service.get_user_role(db, organization_id, current_user.id)
        if role not in [OrganizationRole.OWNER, OrganizationRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owners and admins can update organization",
            )

    return organization_service.update(db, db_obj=org, obj_in=org_in)


@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int,
):
    """
    Delete organization.

    Requires OWNER role or superuser.
    WARNING: This will delete all organization data!
    """
    org = organization_service.get(db, organization_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    # Check access - only owners or superusers
    if not current_user.is_superuser:
        role = organization_user_service.get_user_role(db, organization_id, current_user.id)
        if role != OrganizationRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can delete organization"
            )

    organization_service.remove(db, id=organization_id)
    return None


@router.post("/{organization_id}/activate", response_model=OrganizationResponse)
def activate_organization(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int,
):
    """
    Activate a suspended organization.

    Requires superuser.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can activate organizations",
        )

    return organization_service.activate_organization(db, organization_id)


@router.post("/{organization_id}/suspend", response_model=OrganizationResponse)
def suspend_organization(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int,
):
    """
    Suspend an organization.

    Requires superuser.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can suspend organizations",
        )

    return organization_service.suspend_organization(db, organization_id)


@router.post("/{organization_id}/upgrade", response_model=OrganizationResponse)
def upgrade_subscription(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int,
    upgrade_data: SubscriptionUpgrade,
):
    """
    Upgrade organization subscription plan.

    Requires OWNER role or superuser.
    """
    # Check access
    if not current_user.is_superuser:
        role = organization_user_service.get_user_role(db, organization_id, current_user.id)
        if role != OrganizationRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can upgrade subscription"
            )

    return organization_service.upgrade_plan(db, organization_id, upgrade_data)


@router.get("/{organization_id}/statistics")
def get_organization_statistics(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int,
):
    """
    Get organization statistics.

    Requires membership in the organization.
    """
    if not current_user.is_superuser:
        if not organization_user_service.is_member(db, organization_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this organization"
            )

    return organization_service.get_statistics(db, organization_id)
