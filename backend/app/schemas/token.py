from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenWithOrganization(BaseModel):
    """Token response with organization context"""
    access_token: str
    token_type: str = "bearer"
    organization_id: Optional[int] = None
    organization_name: Optional[str] = None
    organization_role: Optional[str] = None


class TokenPayload(BaseModel):
    sub: int | None = None
    org_id: int | None = None
    org_role: str | None = None
