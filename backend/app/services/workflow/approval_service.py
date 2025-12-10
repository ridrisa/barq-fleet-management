"""
Workflow Approval Service
Handles approval chains, approval requests, and approval processing
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models.workflow.approval_chain import (
    ApprovalChain,
    ApprovalChainApprover,
    ApprovalRequest,
)
from app.models.workflow.approval_chain import ApprovalStatus as ApprovalStatusEnum
from app.models.workflow.instance import WorkflowInstance, WorkflowStatus
from app.schemas.workflow.approval import (
    ApprovalChainApproverCreate,
    ApprovalChainApproverUpdate,
    ApprovalChainCreate,
    ApprovalChainUpdate,
    ApprovalRequestCreate,
    ApprovalRequestUpdate,
)


class WorkflowApprovalService:
    """Service for managing workflow approvals"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== ApprovalChain CRUD ====================

    def get_approval_chain(self, id: Any) -> Optional[ApprovalChain]:
        """Get an approval chain by ID"""
        return self.db.get(ApprovalChain, id)

    def get_approval_chains(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[ApprovalChain]:
        """Get multiple approval chains with optional filters"""
        query = self.db.query(ApprovalChain)
        if filters:
            for key, value in filters.items():
                if hasattr(ApprovalChain, key):
                    query = query.filter(getattr(ApprovalChain, key) == value)
        return query.offset(skip).limit(limit).all()

    def create_approval_chain(
        self, *, obj_in: Union[ApprovalChainCreate, Dict[str, Any]]
    ) -> ApprovalChain:
        """Create a new approval chain"""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = ApprovalChain(**obj_in_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update_approval_chain(
        self,
        *,
        db_obj: ApprovalChain,
        obj_in: Union[ApprovalChainUpdate, Dict[str, Any]],
    ) -> ApprovalChain:
        """Update an approval chain"""
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete_approval_chain(self, *, id: int) -> Optional[ApprovalChain]:
        """Delete an approval chain"""
        obj = self.db.get(ApprovalChain, id)
        if not obj:
            return None
        self.db.delete(obj)
        self.db.commit()
        return obj

    # ==================== ApprovalChainApprover CRUD ====================

    def get_approval_chain_approver(self, id: Any) -> Optional[ApprovalChainApprover]:
        """Get an approval chain approver by ID"""
        return self.db.get(ApprovalChainApprover, id)

    def get_approval_chain_approvers(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[ApprovalChainApprover]:
        """Get multiple approval chain approvers with optional filters"""
        query = self.db.query(ApprovalChainApprover)
        if filters:
            for key, value in filters.items():
                if hasattr(ApprovalChainApprover, key):
                    query = query.filter(getattr(ApprovalChainApprover, key) == value)
        return query.offset(skip).limit(limit).all()

    def create_approval_chain_approver(
        self, *, obj_in: Union[ApprovalChainApproverCreate, Dict[str, Any]]
    ) -> ApprovalChainApprover:
        """Create a new approval chain approver"""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = ApprovalChainApprover(**obj_in_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update_approval_chain_approver(
        self,
        *,
        db_obj: ApprovalChainApprover,
        obj_in: Union[ApprovalChainApproverUpdate, Dict[str, Any]],
    ) -> ApprovalChainApprover:
        """Update an approval chain approver"""
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete_approval_chain_approver(self, *, id: int) -> Optional[ApprovalChainApprover]:
        """Delete an approval chain approver"""
        obj = self.db.get(ApprovalChainApprover, id)
        if not obj:
            return None
        self.db.delete(obj)
        self.db.commit()
        return obj

    # ==================== ApprovalRequest CRUD ====================

    def get_approval_request(self, id: Any) -> Optional[ApprovalRequest]:
        """Get an approval request by ID"""
        return self.db.get(ApprovalRequest, id)

    def get_approval_requests(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[ApprovalRequest]:
        """Get multiple approval requests with optional filters"""
        query = self.db.query(ApprovalRequest)
        if filters:
            for key, value in filters.items():
                if hasattr(ApprovalRequest, key):
                    query = query.filter(getattr(ApprovalRequest, key) == value)
        return query.offset(skip).limit(limit).all()

    def create_approval_request_record(
        self, *, obj_in: Union[ApprovalRequestCreate, Dict[str, Any]]
    ) -> ApprovalRequest:
        """Create a new approval request record"""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = ApprovalRequest(**obj_in_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update_approval_request_record(
        self,
        *,
        db_obj: ApprovalRequest,
        obj_in: Union[ApprovalRequestUpdate, Dict[str, Any]],
    ) -> ApprovalRequest:
        """Update an approval request record"""
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete_approval_request(self, *, id: int) -> Optional[ApprovalRequest]:
        """Delete an approval request"""
        obj = self.db.get(ApprovalRequest, id)
        if not obj:
            return None
        self.db.delete(obj)
        self.db.commit()
        return obj

    # ==================== WorkflowInstance CRUD (for approval operations) ====================

    def _get_workflow_instance(self, id: Any) -> Optional[WorkflowInstance]:
        """Get a workflow instance by ID (internal helper)"""
        return self.db.get(WorkflowInstance, id)

    def _update_workflow_instance(
        self,
        *,
        db_obj: WorkflowInstance,
        obj_in: Dict[str, Any],
    ) -> WorkflowInstance:
        """Update a workflow instance (internal helper)"""
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    # ==================== Business Logic Methods ====================

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
        chain = self.get_approval_chain(approval_chain_id)
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

            request = self.create_approval_request_record(
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
        request = self.get_approval_request(request_id)
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
        updated_request = self.update_approval_request_record(
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
        request = self.get_approval_request(request_id)
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
        updated_request = self.update_approval_request_record(
            db_obj=request,
            obj_in={
                "status": ApprovalStatusEnum.REJECTED,
                "rejected_at": datetime.utcnow(),
                "comments": comments,
            },
        )

        # Update workflow instance to rejected
        instance = self._get_workflow_instance(request.workflow_instance_id)
        if instance:
            self._update_workflow_instance(
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
        request = self.get_approval_request(request_id)
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
        chain = self.get_approval_chain(request.approval_chain_id)
        if chain and not chain.allow_delegation:
            raise AppException(
                status_code=400,
                detail="Delegation is not allowed for this approval chain",
                code="DELEGATION_NOT_ALLOWED",
            )

        # Update request
        updated_request = self.update_approval_request_record(
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
        instance = self._get_workflow_instance(workflow_instance_id)
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
            self._update_workflow_instance(
                db_obj=instance,
                obj_in={"status": WorkflowStatus.APPROVED},
            )
