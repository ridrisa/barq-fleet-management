"""
BigQuery Integration API - Courier Data Migration and Performance Analytics

Provides endpoints for:
- Syncing courier data from SANED BigQuery to local database
- Querying courier performance metrics from BigQuery
- Health check for BigQuery connection
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.services.integrations.bigquery_client import bigquery_client
from app.services.integrations.bigquery_sync import bigquery_sync_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ============ Pydantic Schemas ============

class SyncStats(BaseModel):
    """Statistics from a sync operation"""
    created: int = Field(description="Number of new couriers created")
    updated: int = Field(description="Number of existing couriers updated")
    skipped: int = Field(description="Number of couriers skipped")
    errors: int = Field(description="Number of errors encountered")
    total: int = Field(description="Total records processed")


class SyncRequest(BaseModel):
    """Request body for sync operation"""
    organization_id: int = Field(description="Organization ID to assign couriers to")
    update_existing: bool = Field(default=True, description="Whether to update existing couriers")
    batch_size: int = Field(default=100, ge=10, le=500, description="Batch size for processing")
    status_filter: Optional[str] = Field(
        default=None,
        description="Filter by status (e.g., 'Active', 'Inactive')"
    )


class SyncResponse(BaseModel):
    """Response from a sync operation"""
    success: bool
    message: str
    stats: SyncStats


class SingleSyncRequest(BaseModel):
    """Request body for single courier sync"""
    barq_id: int = Field(description="BARQ_ID of the courier to sync")
    organization_id: int = Field(description="Organization ID to assign courier to")


class SingleSyncResponse(BaseModel):
    """Response from single courier sync"""
    success: bool
    message: str
    action: str = Field(description="Action taken: created, updated, skipped, not_found")
    courier_id: Optional[int] = Field(default=None, description="Local courier ID if found/created")


class HealthCheckResponse(BaseModel):
    """BigQuery health check response"""
    status: str
    project: str
    dataset: str
    table: str
    row_count: Optional[int] = None
    error: Optional[str] = None


class CourierPerformanceItem(BaseModel):
    """Single courier performance data"""
    barq_id: int
    name: Optional[str]
    status: Optional[str]
    city: Optional[str]
    vehicle: Optional[str]
    plate: Optional[str]
    total_orders: Optional[int]
    total_revenue: Optional[float]
    fuel_cost: Optional[float]


class PerformanceResponse(BaseModel):
    """Response with courier performance data"""
    success: bool
    couriers: List[Dict[str, Any]]
    total: int


class PerformanceSummaryResponse(BaseModel):
    """Aggregate performance summary"""
    success: bool
    summary: Dict[str, Any]


class CityBreakdownItem(BaseModel):
    """City performance breakdown"""
    city: str
    courier_count: int
    active_count: int
    total_orders: int
    total_revenue: float
    avg_orders: float
    avg_revenue: float


class CityBreakdownResponse(BaseModel):
    """Response with city breakdown data"""
    success: bool
    cities: List[Dict[str, Any]]


class PlatformBreakdownItem(BaseModel):
    """Platform performance breakdown"""
    platform: str
    total_orders: int
    total_revenue: float


class PlatformBreakdownResponse(BaseModel):
    """Response with platform breakdown data"""
    success: bool
    platforms: List[Dict[str, Any]]


class SearchResponse(BaseModel):
    """Search results response"""
    success: bool
    results: List[Dict[str, Any]]
    count: int


# ============ Endpoints ============

@router.get("/health", response_model=HealthCheckResponse, summary="BigQuery Health Check")
async def bigquery_health_check(
    current_user: User = Depends(get_current_active_user),
):
    """
    Check BigQuery connection health.

    Returns status of connection to SANED BigQuery data.
    """
    try:
        health = bigquery_client.health_check()
        return HealthCheckResponse(**health)
    except Exception as e:
        logger.error(f"BigQuery health check failed: {e}")
        return HealthCheckResponse(
            status="unhealthy",
            project="looker-barqdata-2030",
            dataset="master_saned",
            table="ultimate",
            error=str(e)
        )


@router.post("/sync", response_model=SyncResponse, summary="Sync All Couriers from BigQuery")
async def sync_couriers_from_bigquery(
    request: SyncRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Sync all couriers from SANED BigQuery to local database.

    This is a potentially long-running operation that processes ~300k records.
    Consider running in background for large datasets.

    - **organization_id**: Organization to assign couriers to
    - **update_existing**: Whether to update existing couriers (default: True)
    - **batch_size**: Records per batch (10-500, default: 100)
    - **status_filter**: Optional status filter (e.g., "Active")
    """
    try:
        logger.info(f"Starting BigQuery sync for org {request.organization_id}")

        stats = bigquery_sync_service.sync_all_couriers(
            db=db,
            organization_id=request.organization_id,
            update_existing=request.update_existing,
            batch_size=request.batch_size,
            status_filter=request.status_filter,
        )

        return SyncResponse(
            success=True,
            message=f"Sync completed: {stats['created']} created, {stats['updated']} updated, {stats['errors']} errors",
            stats=SyncStats(**stats)
        )
    except Exception as e:
        logger.error(f"BigQuery sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.post("/sync/single", response_model=SingleSyncResponse, summary="Sync Single Courier by BARQ ID")
async def sync_single_courier(
    request: SingleSyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Sync a single courier by BARQ_ID from BigQuery.

    - **barq_id**: BARQ_ID of the courier in BigQuery
    - **organization_id**: Organization to assign courier to
    """
    try:
        courier, action = bigquery_sync_service.sync_single_by_barq_id(
            db=db,
            barq_id=request.barq_id,
            organization_id=request.organization_id,
        )

        if action == "not_found":
            return SingleSyncResponse(
                success=False,
                message=f"Courier with BARQ_ID {request.barq_id} not found in BigQuery",
                action=action,
            )

        return SingleSyncResponse(
            success=True,
            message=f"Courier {action} successfully",
            action=action,
            courier_id=courier.id if courier else None,
        )
    except Exception as e:
        logger.error(f"Single courier sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.get("/performance", response_model=PerformanceResponse, summary="Get Courier Performance Metrics")
async def get_performance_metrics(
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    status: str = Query("Active", description="Filter by status"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get courier performance metrics directly from BigQuery.

    Returns performance data including orders and revenue by platform.
    """
    try:
        couriers = bigquery_client.get_performance_metrics(
            skip=skip,
            limit=limit,
            status=status,
        )
        return PerformanceResponse(
            success=True,
            couriers=couriers,
            total=len(couriers)
        )
    except Exception as e:
        logger.error(f"Failed to fetch performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/summary", response_model=PerformanceSummaryResponse, summary="Get Performance Summary")
async def get_performance_summary(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get aggregate performance summary for all couriers.

    Returns totals and averages across all couriers.
    """
    try:
        summary = bigquery_client.get_performance_summary()
        return PerformanceSummaryResponse(
            success=True,
            summary=summary
        )
    except Exception as e:
        logger.error(f"Failed to fetch performance summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/by-city", response_model=CityBreakdownResponse, summary="Get Performance by City")
async def get_performance_by_city(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get performance breakdown by city.

    Returns courier counts, orders, and revenue grouped by city.
    """
    try:
        cities = bigquery_client.get_city_breakdown()
        return CityBreakdownResponse(
            success=True,
            cities=cities
        )
    except Exception as e:
        logger.error(f"Failed to fetch city breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/by-platform", response_model=PlatformBreakdownResponse, summary="Get Performance by Platform")
async def get_performance_by_platform(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get order and revenue breakdown by delivery platform.

    Returns totals for each platform (Jahez, Barq, Mrsool, etc.).
    """
    try:
        platforms = bigquery_client.get_platform_breakdown()
        return PlatformBreakdownResponse(
            success=True,
            platforms=platforms
        )
    except Exception as e:
        logger.error(f"Failed to fetch platform breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=SearchResponse, summary="Search Couriers in BigQuery")
async def search_couriers(
    q: str = Query(..., min_length=1, description="Search term (name, BARQ_ID, or mobile)"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Search couriers in BigQuery by name, BARQ_ID, or mobile number.

    Returns matching couriers with basic info and performance data.
    """
    try:
        results = bigquery_client.search_couriers(search_term=q, limit=limit)
        return SearchResponse(
            success=True,
            results=results,
            count=len(results)
        )
    except Exception as e:
        logger.error(f"Courier search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/courier/{barq_id}", summary="Get Single Courier from BigQuery")
async def get_courier_by_barq_id(
    barq_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a single courier's data from BigQuery by BARQ_ID.
    """
    try:
        courier = bigquery_client.get_courier_by_barq_id(barq_id)
        if not courier:
            raise HTTPException(status_code=404, detail=f"Courier with BARQ_ID {barq_id} not found")
        return {
            "success": True,
            "courier": courier
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch courier {barq_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
