from fastapi import APIRouter

from app.api.v1.analytics import (
    export,
    financial,
    fleet,
    forecasting,
    hr,
    kpi,
    operations,
    overview,
    performance,
    reports,
)

router = APIRouter()

# Performance Analytics
router.include_router(performance.router, prefix="/performance", tags=["analytics-performance"])

# Overview & Dashboard Analytics
router.include_router(overview.router, prefix="/overview", tags=["analytics-overview"])

# Fleet Analytics
router.include_router(fleet.router, prefix="/fleet", tags=["analytics-fleet"])

# HR Analytics
router.include_router(hr.router, prefix="/hr", tags=["analytics-hr"])

# Financial Analytics
router.include_router(financial.router, prefix="/financial", tags=["analytics-financial"])

# Operations Analytics
router.include_router(operations.router, prefix="/operations", tags=["analytics-operations"])

# Custom Reports
router.include_router(reports.router, prefix="/reports", tags=["analytics-reports"])

# KPI Dashboard
router.include_router(kpi.router, prefix="/kpi", tags=["analytics-kpi"])

# Forecasting
router.include_router(forecasting.router, prefix="/forecasting", tags=["analytics-forecasting"])

# Data Export
router.include_router(export.router, prefix="/export", tags=["analytics-export"])

__all__ = ["router"]
