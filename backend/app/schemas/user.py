from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr

UserRole = Literal[
    "user", "admin", "manager", "super_admin", "hr_manager", "fleet_manager", "viewer"
]


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = "user"
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDB(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    google_id: Optional[str] = None
    picture: Optional[str] = None

    model_config = {"from_attributes": True}


class User(UserInDB):
    pass
