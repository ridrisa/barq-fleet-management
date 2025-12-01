"""
Workflow Approval Service
Handles approval chains, approval requests, and approval processing
"""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.workflow.approval_chain import (
    ApprovalRequest,
    ApprovalStatus as ApprovalStatusEnum,
)
from app.models.workflow.instance import WorkflowStatus
from app.crud.workflow import approval_request, approval_chain, workflow_instance
from app.core.exceptions import AppException


class WorkflowApprovalService:
    """Service for managing workflow approvals"""

    def __init__(self, db: Session):
        self.db = db

    def create_approval_requests(
        self,
        workflow_instance_id: int,
        approval_chain_id: int,
    ) -> List[ApprovalRequest]:
        """
        Create approval requests for a workflow instance based on approval chain

        Args:
            workflow_instance_id: Workflow instance ID
            approval_chain_id: Approval chain ID

        Returns:
            List of created ApprovalRequest objects
        """
        chain = approval_chain.get(self.db, id=approval_chain_id)
        if not chain:
            raise AppException(
                status_code=404,
                detail="Approval chain not found",
                code="CHAIN_NOT_FOUND",
            )

        if not chain.approvers:
            raise AppException(
                status_code=400,
                detail="Approval chain has no approvers",
                code="NO_APPROVERS",
            )

        requests = []

        # Create requests based on chain type (sequential or parallel)
        for approver in sorted(chain.approvers, key=lambda x: (x.level, x.order)):
            # Calculate expiration time
            expires_at = None
            if chain.escalation_hours:
                expires_at = datetime.utcnow() + timedelta(hours=chain.escalation_hours)

            request = approval_request.create(
                self.db,
                obj_in={
                    "workflow_instance_id": workflow_instance_id,
                    "approval_chain_id": approval_chain_id,
                    "approver_id": approver.user_id,
                    "level": approver.level,
                    "status": ApprovalStatusEnum.PENDING,
                    "expires_at": expires_at,
                },
            )
            requests.append(request)

        return requests

    def approve_request(
        self,
        request_id: int,
        approver_id: int,
        comments: Optional[str] = None,
    ) -> ApprovalRequest:
        """
        Approve an approval request

        Args:
            request_id: Approval request ID
            approver_id: User ID of approver
            comments: Optional approval comments

        Returns:
            Updated ApprovalRequest
        """
        request = approval_request.get(self.db, id=request_id)
        if not request:
            raise AppException(
                status_code=404,
                detail="Approval request not found",
                code="REQUEST_NOT_FOUND",
            )

        if request.approver_id != approver_id:
            raise AppException(
                status_code=403,
                detail="You are not authorized to approve this request",
                code="UNAUTHORIZED_APPROVER",
            )

        if request.status != ApprovalStatusEnum.PENDING:
            raise AppException(
                status_code=400,
                detail=f"Request is already {request.status.value}",
                code="REQUEST_NOT_PENDING",
            )

        # Update request
        updated_request = approval_request.update(
            self.db,
            db_obj=request,
            obj_in={
                "status": ApprovalStatusEnum.APPROVED,
                "approved_at": datetime.utcnow(),
                "comments": comments,
            },
        )

        # Check if all approvals in chain are complete
        self._check_approval_chain_completion(request.workflow_instance_id)

        return updated_request

    def reject_request(
        self,
        request_id: int,
        approver_id: int,
        comments: Optional[str] = None,
    ) -> ApprovalRequest:
        """Reject an approval request"""
        request = approval_request.get(self.db, id=request_id)
        if not request:
            raise AppException(
                status_code=404,
                detail="Approval request not found",
                code="REQUEST_NOT_FOUND",
            )

        if request.approver_id != approver_id:
            raise AppException(
                status_code=403,
                detail="You are not authorized to reject this request",
                code="UNAUTHORIZED_APPROVER",
            )

        if request.status != ApprovalStatusEnum.PENDING:
            raise AppException(
                status_code=400,
                detail=f"Request is already {request.status.value}",
                code="REQUEST_NOT_PENDING",
            )

        # Update request
        updated_request = approval_request.update(
            self.db,
            db_obj=request,
            obj_in={
                "status": ApprovalStatusEnum.REJECTED,
                "rejected_at": datetime.utcnow(),
                "comments": comments,
            },
        )

        # Update workflow instance to rejected
        instance = workflow_instance.get(self.db, id=request.workflow_instance_id)
        if instance:
            workflow_instance.update(
                self.db,
                db_obj=instance,
                obj_in={"status": WorkflowStatus.REJECTED},
            )

        return updated_request

    def delegate_request(
        self,
        request_id: int,
        approver_id: int,
        delegate_to_id: int,
        comments: Optional[str] = None,
    ) -> ApprovalRequest:
        """Delegate an approval request to another user"""
        request = approval_request.get(self.db, id=request_id)
        if not request:
            raise AppException(
                status_code=404,
                detail="Approval request not found",
                code="REQUEST_NOT_FOUND",
            )

        if request.approver_id != approver_id:
            raise AppException(
                status_code=403,
                detail="You are not authorized to delegate this request",
                code="UNAUTHORIZED_APPROVER",
            )

        # Check if delegation is allowed
        chain = approval_chain.get(self.db, id=request.approval_chain_id)
        if chain and not chain.allow_delegation:
            raise AppException(
                status_code=400,
                detail="Delegation is not allowed for this approval chain",
                code="DELEGATION_NOT_ALLOWED",
            )

        # Update request
        updated_request = approval_request.update(
            self.db,
            db_obj=request,
            obj_in={
                "delegated_to_id": delegate_to_id,
                "delegated_at": datetime.utcnow(),
                "status": ApprovalStatusEnum.DELEGATED,
                "comments": comments,
            },
        )

        return updated_request

    def _check_approval_chain_completion(self, workflow_instance_id: int) -> None:
        """
        Check if approval chain is complete and update workflow status

        Args:
            workflow_instance_id: Workflow instance ID
        """
        instance = workflow_instance.get(self.db, id=workflow_instance_id)
        if not instance or not instance.approval_requests:
            return

        # Get all approval requests
        all_requests = instance.approval_requests

        # Check if all required approvals are complete
        all_approved = all(
            req.status == ApprovalStatusEnum.APPROVED
            for req in all_requests
            if req.status != ApprovalStatusEnum.DELEGATED
        )

        if all_approved:
            # Update workflow to approved status
            workflow_instance.update(
                self.db,
                db_obj=instance,
                obj_in={"status": WorkflowStatus.APPROVED},
            )
