"""Organization User service for managing user memberships"""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.tenant.organization_user import OrganizationRole, OrganizationUser
from app.models.user import User
from app.schemas.tenant.organization_user import (
    OrganizationUserCreate,
    OrganizationUserUpdate,
)
from app.services.base import CRUDBase
from app.services.tenant.organization_service import organization_service


class OrganizationUserService(
    CRUDBase[OrganizationUser, OrganizationUserCreate, OrganizationUserUpdate]
):
    """Service for managing organization user memberships"""

    def __init__(self):
        super().__init__(OrganizationUser)

    def add_user(
        self, db: Session, *, organization_id: int, obj_in: OrganizationUserCreate
    ) -> OrganizationUser:
        """
        Add a user to an organization
        Args:
            db: Database session
            organization_id: Organization ID
            obj_in: User membership data
        """
        # Check if organization exists
        org = organization_service.get(db, organization_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
            )

        # Check user limit
        if not organization_service.check_user_limit(db, organization_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization has reached maximum user limit",
            )

        # Check if user exists
        user = db.query(User).filter(User.id == obj_in.user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Check if user is already a member
        existing = (
            db.query(OrganizationUser)
            .filter(
                and_(
                    OrganizationUser.organization_id == organization_id,
                    OrganizationUser.user_id == obj_in.user_id,
                )
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this organization",
            )

        # Create membership
        user_data = obj_in.model_dump()
        user_data["organization_id"] = organization_id

        db_obj = OrganizationUser(**user_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj

    def remove_user(self, db: Session, organization_id: int, user_id: int) -> OrganizationUser:
        """
        Remove a user from an organization
        Args:
            db: Database session
            organization_id: Organization ID
            user_id: User ID
        """
        membership = (
            db.query(OrganizationUser)
            .filter(
                and_(
                    OrganizationUser.organization_id == organization_id,
                    OrganizationUser.user_id == user_id,
                )
            )
            .first()
        )

        if not membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User membership not found"
            )

        # Prevent removing the last owner
        if membership.role == OrganizationRole.OWNER:
            owner_count = (
                db.query(OrganizationUser)
                .filter(
                    and_(
                        OrganizationUser.organization_id == organization_id,
                        OrganizationUser.role == OrganizationRole.OWNER,
                        OrganizationUser.is_active == True,
                    )
                )
                .count()
            )

            if owner_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot remove the last owner from organization",
                )

        db.delete(membership)
        db.commit()
        return membership

    def update_role(
        self, db: Session, organization_id: int, user_id: int, obj_in: OrganizationUserUpdate
    ) -> OrganizationUser:
        """
        Update user role in organization
        Args:
            db: Database session
            organization_id: Organization ID
            user_id: User ID
            obj_in: Update data
        """
        membership = (
            db.query(OrganizationUser)
            .filter(
                and_(
                    OrganizationUser.organization_id == organization_id,
                    OrganizationUser.user_id == user_id,
                )
            )
            .first()
        )

        if not membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User membership not found"
            )

        # If changing from owner role, check if there are other owners
        if (
            membership.role == OrganizationRole.OWNER
            and obj_in.role
            and obj_in.role != OrganizationRole.OWNER
        ):
            owner_count = (
                db.query(OrganizationUser)
                .filter(
                    and_(
                        OrganizationUser.organization_id == organization_id,
                        OrganizationUser.role == OrganizationRole.OWNER,
                        OrganizationUser.is_active == True,
                    )
                )
                .count()
            )

            if owner_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot change role of the last owner",
                )

        # Update membership
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(membership, field, value)

        db.commit()
        db.refresh(membership)
        return membership

    def get_by_organization(
        self,
        db: Session,
        organization_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> List[OrganizationUser]:
        """
        Get all users in an organization
        Args:
            db: Database session
            organization_id: Organization ID
            skip: Number to skip for pagination
            limit: Maximum number to return
            is_active: Filter by active status
        """
        query = db.query(OrganizationUser).filter(
            OrganizationUser.organization_id == organization_id
        )

        if is_active is not None:
            query = query.filter(OrganizationUser.is_active == is_active)

        return query.offset(skip).limit(limit).all()

    def get_by_user(
        self,
        db: Session,
        user_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> List[OrganizationUser]:
        """
        Get all organizations a user belongs to
        Args:
            db: Database session
            user_id: User ID
            skip: Number to skip for pagination
            limit: Maximum number to return
            is_active: Filter by active status
        """
        query = db.query(OrganizationUser).filter(OrganizationUser.user_id == user_id)

        if is_active is not None:
            query = query.filter(OrganizationUser.is_active == is_active)

        return query.offset(skip).limit(limit).all()

    def get_user_role(
        self, db: Session, organization_id: int, user_id: int
    ) -> Optional[OrganizationRole]:
        """
        Get user's role in an organization
        Returns: OrganizationRole or None if not a member
        """
        membership = (
            db.query(OrganizationUser)
            .filter(
                and_(
                    OrganizationUser.organization_id == organization_id,
                    OrganizationUser.user_id == user_id,
                    OrganizationUser.is_active == True,
                )
            )
            .first()
        )

        return membership.role if membership else None

    def is_member(self, db: Session, organization_id: int, user_id: int) -> bool:
        """
        Check if user is a member of organization
        """
        return (
            db.query(OrganizationUser)
            .filter(
                and_(
                    OrganizationUser.organization_id == organization_id,
                    OrganizationUser.user_id == user_id,
                    OrganizationUser.is_active == True,
                )
            )
            .first()
            is not None
        )


# Create instance
organization_user_service = OrganizationUserService()
