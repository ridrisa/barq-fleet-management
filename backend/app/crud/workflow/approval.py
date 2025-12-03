from app.crud.base import CRUDBase
from app.models.workflow.approval_chain import (
    ApprovalChain,
    ApprovalChainApprover,
    ApprovalRequest,
)
from app.schemas.workflow.approval import (
    ApprovalChainApproverCreate,
    ApprovalChainApproverUpdate,
    ApprovalChainCreate,
    ApprovalChainUpdate,
    ApprovalRequestCreate,
    ApprovalRequestUpdate,
)

approval_chain = CRUDBase[ApprovalChain, ApprovalChainCreate, ApprovalChainUpdate](ApprovalChain)
approval_chain_approver = CRUDBase[
    ApprovalChainApprover, ApprovalChainApproverCreate, ApprovalChainApproverUpdate
](ApprovalChainApprover)
approval_request = CRUDBase[ApprovalRequest, ApprovalRequestCreate, ApprovalRequestUpdate](
    ApprovalRequest
)
