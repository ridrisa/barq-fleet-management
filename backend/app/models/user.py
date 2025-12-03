from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Nullable for Google OAuth users
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(String, default="user")  # user, admin, manager

    # Google OAuth fields
    google_id = Column(String, unique=True, index=True, nullable=True)
    picture = Column(String, nullable=True)  # Google profile picture URL

    # Relationships - RBAC (uncommented to fix bidirectional relationship)
    roles = relationship("Role", secondary="user_roles", back_populates="users")

    # Password reset tokens relationship
    password_reset_tokens = relationship(
        "PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
