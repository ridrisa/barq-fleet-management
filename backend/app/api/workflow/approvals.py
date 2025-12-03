from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.crud.workflow import approval_chain, approval_request
from app.schemas.workflow import (
    ApprovalChainCreate,
    ApprovalChainUpdate,
    ApprovalChainResponse,
    ApprovalRequestResponse,
    ApprovalActionRequest,
)
from app.services.workflow.approval_service import WorkflowApprovalService

router = APIRouter()


# Approval Chains
@router.get("/chains", response_model=List[ApprovalChainResponse])
def list_approval_chains(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all approval chains"""
    chains = approval_chain.get_multi(db, skip=skip, limit=limit)
    return chains


@router.post("/chains", response_model=ApprovalChainResponse, status_code=201)
def create_approval_chain(
    chain_in: ApprovalChainCreate,
    db: Session = Depends(get_db),
):
    """Create a new approval chain"""
    chain = approval_chain.create(db, obj_in=chain_in)
    return chain


@router.get("/chains/{chain_id}", response_model=ApprovalChainResponse)
def get_approval_chain(
    chain_id: int,
    db: Session = Depends(get_db),
):
    """Get an approval chain by ID"""
    chain = approval_chain.get(db, id=chain_id)
    if not chain:
        raise HTTPException(status_code=404, detail="Approval chain not found")
    return chain


@router.put("/chains/{chain_id}", response_model=ApprovalChainResponse)
def update_approval_chain(
    chain_id: int,
    chain_in: ApprovalChainUpdate,
    db: Session = Depends(get_db),
):
    """Update an approval chain"""
    chain = approval_chain.get(db, id=chain_id)
    if not chain:
        raise HTTPException(status_code=404, detail="Approval chain not found")

    chain = approval_chain.update(db, db_obj=chain, obj_in=chain_in)
    return chain


@router.delete("/chains/{chain_id}", status_code=204)
def delete_approval_chain(
    chain_id: int,
    db: Session = Depends(get_db),
):
    """Delete an approval chain"""
    chain = approval_chain.get(db, id=chain_id)
    if not chain:
        raise HTTPException(status_code=404, detail="Approval chain not found")

    approval_chain.remove(db, id=chain_id)
    return None


# Approval Requests
@router.get("/requests", response_model=List[ApprovalRequestResponse])
def list_approval_requests(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all approval requests"""
    requests = approval_request.get_multi(db, skip=skip, limit=limit)
    return requests


@router.get("/requests/{request_id}", response_model=ApprovalRequestResponse)
def get_approval_request(
    request_id: int,
    db: Session = Depends(get_db),
):
    """Get an approval request by ID"""
    request = approval_request.get(db, id=request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Approval request not found")
    return request


@router.post("/requests/{request_id}/action", response_model=ApprovalRequestResponse)
def process_approval_action(
    request_id: int,
    action: ApprovalActionRequest,
    approver_id: int = Body(...),
    db: Session = Depends(get_db),
):
    """Process an approval action (approve, reject, delegate)"""
    approval_service = WorkflowApprovalService(db)

    if action.action == "approve":
        request = approval_service.approve_request(
            request_id=request_id,
            approver_id=approver_id,
            comments=action.comments,
        )
    elif action.action == "reject":
        request = approval_service.reject_request(
            request_id=request_id,
            approver_id=approver_id,
            comments=action.comments,
        )
    elif action.action == "delegate":
        if not action.delegate_to_id:
            raise HTTPException(
                status_code=400, detail="delegate_to_id required for delegation"
            )
        request = approval_service.delegate_request(
            request_id=request_id,
            approver_id=approver_id,
            delegate_to_id=action.delegate_to_id,
            comments=action.comments,
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    return request
