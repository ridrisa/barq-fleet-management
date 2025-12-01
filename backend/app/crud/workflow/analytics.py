from app.crud.base import CRUDBase
from app.models.workflow.analytics import (
    WorkflowMetrics,
    WorkflowStepMetrics,
    WorkflowPerformanceSnapshot,
    WorkflowUserMetrics,
)
from app.schemas.workflow.analytics import (
    WorkflowMetricsCreate,
    WorkflowMetricsUpdate,
    WorkflowStepMetricsCreate,
    WorkflowStepMetricsUpdate,
    WorkflowPerformanceSnapshotCreate,
    WorkflowUserMetricsCreate,
    WorkflowUserMetricsUpdate,
)

workflow_metrics = CRUDBase[
    WorkflowMetrics, WorkflowMetricsCreate, WorkflowMetricsUpdate
](WorkflowMetrics)
workflow_step_metrics = CRUDBase[
    WorkflowStepMetrics, WorkflowStepMetricsCreate, WorkflowStepMetricsUpdate
](WorkflowStepMetrics)
workflow_performance_snapshot = CRUDBase[
    WorkflowPerformanceSnapshot, WorkflowPerformanceSnapshotCreate, dict
](WorkflowPerformanceSnapshot)
workflow_user_metrics = CRUDBase[
    WorkflowUserMetrics, WorkflowUserMetricsCreate, WorkflowUserMetricsUpdate
](WorkflowUserMetrics)
