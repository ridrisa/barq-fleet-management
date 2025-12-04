"""
Approval Chains API Routes
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_organization, get_current_user
from app.models.tenant.organization import Organization
from app.models.workflow.approval_chain import ApprovalChain

router = APIRouter()


class ApprovalChainBase(BaseModel):
    name: str
    description: Optional[str] = None
    workflow_template_id: Optional[int] = None
    levels: int = 1
    is_sequential: bool = True
    allow_delegation: bool = False
    auto_escalate: bool = True
    escalation_hours: int = 24
    is_active: bool = True


class ApprovalChainCreate(ApprovalChainBase):
    pass


class ApprovalChainUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    levels: Optional[int] = None
    is_sequential: Optional[bool] = None
    allow_delegation: Optional[bool] = None
    auto_escalate: Optional[bool] = None
    escalation_hours: Optional[int] = None
    is_active: Optional[bool] = None


class ApprovalChainResponse(ApprovalChainBase):
    id: int
    organization_id: int

    class Config:
        from_attributes = True


@router.get("/", response_model=List[ApprovalChainResponse])
def list_approval_chains(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List all approval chains for the organization"""
    query = db.query(ApprovalChain).filter(ApprovalChain.organization_id == current_org.id)

    if is_active is not None:
        query = query.filter(ApprovalChain.is_active == is_active)

    chains = query.offset(skip).limit(limit).all()
    return chains


@router.get("/{chain_id}", response_model=ApprovalChainResponse)
def get_approval_chain(
    chain_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get a specific approval chain by ID"""
    chain = db.query(ApprovalChain).filter(
        ApprovalChain.id == chain_id,
        ApprovalChain.organization_id == current_org.id
    ).first()

    if not chain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval chain not found"
        )
    return chain


@router.post("/", response_model=ApprovalChainResponse, status_code=status.HTTP_201_CREATED)
def create_approval_chain(
    chain_in: ApprovalChainCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Create a new approval chain"""
    chain = ApprovalChain(
        **chain_in.model_dump(),
        organization_id=current_org.id
    )
    db.add(chain)
    db.commit()
    db.refresh(chain)
    return chain


@router.put("/{chain_id}", response_model=ApprovalChainResponse)
def update_approval_chain(
    chain_id: int,
    chain_in: ApprovalChainUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update an existing approval chain"""
    chain = db.query(ApprovalChain).filter(
        ApprovalChain.id == chain_id,
        ApprovalChain.organization_id == current_org.id
    ).first()

    if not chain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval chain not found"
        )

    update_data = chain_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(chain, field, value)

    db.commit()
    db.refresh(chain)
    return chain


@router.delete("/{chain_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_approval_chain(
    chain_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Delete an approval chain"""
    chain = db.query(ApprovalChain).filter(
        ApprovalChain.id == chain_id,
        ApprovalChain.organization_id == current_org.id
    ).first()

    if not chain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval chain not found"
        )

    db.delete(chain)
    db.commit()
    return None
