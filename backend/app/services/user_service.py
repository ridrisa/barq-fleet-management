"""User Service

Service layer for user management and authentication operations.
This is a critical service used by core/dependencies.py for authentication.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.base import CRUDBase


class UserService(CRUDBase[User, UserCreate, UserUpdate]):
    """
    Service for user management operations.

    This service handles:
    - User CRUD operations
    - Authentication (email/password and Google OAuth)
    - User status checks (is_active, is_superuser)
    """

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """
        Get a user by email address

        Args:
            db: Database session
            email: User's email address

        Returns:
            User object or None if not found
        """
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Create a new user with hashed password

        Args:
            db: Database session
            obj_in: User creation data

        Returns:
            Created user object
        """
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password) if obj_in.password else None,
            full_name=obj_in.full_name,
            role=obj_in.role,
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: UserUpdate | dict
    ) -> User:
        """
        Update a user, hashing password if provided

        Args:
            db: Database session
            db_obj: Existing user object
            obj_in: Update data

        Returns:
            Updated user object
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # Hash password if provided
        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = get_password_hash(update_data["password"])
            del update_data["password"]

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password

        Args:
            db: Database session
            email: User's email address
            password: User's password (plaintext)

        Returns:
            User object if authentication succeeds, None otherwise
        """
        user = self.get_by_email(db, email=email)
        if not user or not user.hashed_password:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        """
        Check if a user is active

        Args:
            user: User object

        Returns:
            True if user is active, False otherwise
        """
        return bool(user.is_active)

    def is_superuser(self, user: User) -> bool:
        """
        Check if a user is a superuser

        Args:
            user: User object

        Returns:
            True if user is a superuser, False otherwise
        """
        return bool(user.is_superuser)

    def get_by_google_id(self, db: Session, *, google_id: str) -> Optional[User]:
        """
        Get a user by Google ID

        Args:
            db: Database session
            google_id: Google OAuth ID

        Returns:
            User object or None if not found
        """
        return db.query(User).filter(User.google_id == google_id).first()

    def create_google_user(
        self,
        db: Session,
        *,
        email: str,
        google_id: str,
        full_name: str,
        picture: str,
    ) -> User:
        """
        Create a user from Google OAuth

        Args:
            db: Database session
            email: User's email from Google
            google_id: Google OAuth ID
            full_name: User's full name from Google
            picture: User's profile picture URL from Google

        Returns:
            Created user object
        """
        db_obj = User(
            email=email,
            google_id=google_id,
            full_name=full_name,
            picture=picture,
            is_active=True,
            is_superuser=False,
            role="user",
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_google_info(
        self,
        db: Session,
        *,
        user: User,
        google_id: str,
        picture: Optional[str] = None,
    ) -> User:
        """
        Update user's Google OAuth information

        Args:
            db: Database session
            user: Existing user object
            google_id: Google OAuth ID
            picture: Optional profile picture URL

        Returns:
            Updated user object
        """
        user.google_id = google_id
        if picture:
            user.picture = picture
        db.commit()
        db.refresh(user)
        return user

    def get_by_role(
        self,
        db: Session,
        *,
        role: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """
        Get all users with a specific role

        Args:
            db: Database session
            role: User role to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of users
        """
        return (
            db.query(User)
            .filter(User.role == role)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active_users(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """
        Get all active users

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of active users
        """
        return (
            db.query(User)
            .filter(User.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def deactivate(self, db: Session, *, user_id: int) -> Optional[User]:
        """
        Deactivate a user

        Args:
            db: Database session
            user_id: ID of the user to deactivate

        Returns:
            Updated user object or None if not found
        """
        user = self.get(db, user_id)
        if not user:
            return None
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user

    def activate(self, db: Session, *, user_id: int) -> Optional[User]:
        """
        Activate a user

        Args:
            db: Database session
            user_id: ID of the user to activate

        Returns:
            Updated user object or None if not found
        """
        user = self.get(db, user_id)
        if not user:
            return None
        user.is_active = True
        db.commit()
        db.refresh(user)
        return user

    def change_password(
        self,
        db: Session,
        *,
        user: User,
        new_password: str,
    ) -> User:
        """
        Change a user's password

        Args:
            db: Database session
            user: User object
            new_password: New password (plaintext)

        Returns:
            Updated user object
        """
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        db.refresh(user)
        return user


user_service = UserService(User)
