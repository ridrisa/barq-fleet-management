"""Organization service for multi-tenant operations"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.tenant.organization import Organization, SubscriptionPlan, SubscriptionStatus
from app.models.tenant.organization_user import OrganizationUser
from app.schemas.tenant.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    SubscriptionUpgrade,
)
from app.services.base import CRUDBase


class OrganizationService(CRUDBase[Organization, OrganizationCreate, OrganizationUpdate]):
    """Service for managing organizations"""

    def __init__(self):
        super().__init__(Organization)

    def create_organization(
        self,
        db: Session,
        *,
        obj_in: OrganizationCreate,
        trial_days: int = 14
    ) -> Organization:
        """
        Create a new organization with default trial period
        Args:
            db: Database session
            obj_in: Organization creation data
            trial_days: Number of days for trial period (default: 14)
        """
        # Check if organization name or slug already exists
        existing = db.query(Organization).filter(
            (Organization.name == obj_in.name) | (Organization.slug == obj_in.slug)
        ).first()

        if existing:
            if existing.name == obj_in.name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Organization with this name already exists"
                )
            if existing.slug == obj_in.slug:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Organization with this slug already exists"
                )

        # Set trial end date
        trial_ends_at = datetime.utcnow() + timedelta(days=trial_days)

        # Create organization
        org_data = obj_in.model_dump()
        org_data["trial_ends_at"] = trial_ends_at
        org_data["subscription_status"] = SubscriptionStatus.TRIAL

        db_obj = Organization(**org_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj

    def get_by_slug(self, db: Session, slug: str) -> Optional[Organization]:
        """Get organization by slug"""
        return db.query(Organization).filter(Organization.slug == slug).first()

    def activate_organization(self, db: Session, organization_id: int) -> Organization:
        """Activate an organization"""
        org = self.get(db, organization_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

        org.is_active = True
        org.subscription_status = SubscriptionStatus.ACTIVE
        db.commit()
        db.refresh(org)
        return org

    def suspend_organization(self, db: Session, organization_id: int) -> Organization:
        """Suspend an organization"""
        org = self.get(db, organization_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

        org.is_active = False
        org.subscription_status = SubscriptionStatus.SUSPENDED
        db.commit()
        db.refresh(org)
        return org

    def upgrade_plan(
        self,
        db: Session,
        organization_id: int,
        upgrade_data: SubscriptionUpgrade
    ) -> Organization:
        """
        Upgrade organization subscription plan
        Args:
            db: Database session
            organization_id: Organization ID
            upgrade_data: Upgrade details
        """
        org = self.get(db, organization_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

        # Update subscription plan
        org.subscription_plan = upgrade_data.subscription_plan
        org.subscription_status = SubscriptionStatus.ACTIVE

        # Update limits if provided
        if upgrade_data.max_users is not None:
            org.max_users = upgrade_data.max_users
        if upgrade_data.max_couriers is not None:
            org.max_couriers = upgrade_data.max_couriers
        if upgrade_data.max_vehicles is not None:
            org.max_vehicles = upgrade_data.max_vehicles

        # Clear trial end date for paid plans
        if upgrade_data.subscription_plan != SubscriptionPlan.FREE:
            org.trial_ends_at = None

        db.commit()
        db.refresh(org)
        return org

    def check_user_limit(self, db: Session, organization_id: int) -> bool:
        """
        Check if organization has reached user limit
        Returns: True if under limit, False if limit reached
        """
        org = self.get(db, organization_id)
        if not org:
            return False

        current_user_count = db.query(func.count(OrganizationUser.id)).filter(
            OrganizationUser.organization_id == organization_id,
            OrganizationUser.is_active == True
        ).scalar()

        return current_user_count < org.max_users

    def check_courier_limit(self, db: Session, organization_id: int) -> bool:
        """
        Check if organization has reached courier limit
        Returns: True if under limit, False if limit reached
        """
        org = self.get(db, organization_id)
        if not org:
            return False

        # This would check against actual courier count
        # For now, returning True as courier module will implement the actual check
        return True

    def check_vehicle_limit(self, db: Session, organization_id: int) -> bool:
        """
        Check if organization has reached vehicle limit
        Returns: True if under limit, False if limit reached
        """
        org = self.get(db, organization_id)
        if not org:
            return False

        # This would check against actual vehicle count
        # For now, returning True as fleet module will implement the actual check
        return True

    def get_statistics(self, db: Session, organization_id: int) -> Dict[str, Any]:
        """
        Get organization statistics
        Returns: Dictionary with user_count, courier_count, vehicle_count, etc.
        """
        org = self.get(db, organization_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

        user_count = db.query(func.count(OrganizationUser.id)).filter(
            OrganizationUser.organization_id == organization_id,
            OrganizationUser.is_active == True
        ).scalar()

        # These would be populated by actual counts from other modules
        courier_count = 0
        vehicle_count = 0

        return {
            "user_count": user_count,
            "courier_count": courier_count,
            "vehicle_count": vehicle_count,
            "max_users": org.max_users,
            "max_couriers": org.max_couriers,
            "max_vehicles": org.max_vehicles,
            "subscription_plan": org.subscription_plan.value,
            "subscription_status": org.subscription_status.value,
            "trial_ends_at": org.trial_ends_at.isoformat() if org.trial_ends_at else None,
        }

    def update_settings(
        self,
        db: Session,
        organization_id: int,
        settings: Dict[str, Any]
    ) -> Organization:
        """Update organization settings"""
        org = self.get(db, organization_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

        # Merge with existing settings
        current_settings = org.settings or {}
        current_settings.update(settings)
        org.settings = current_settings

        db.commit()
        db.refresh(org)
        return org


# Create instance
organization_service = OrganizationService()
