from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.analytics import PerformanceData
from app.models.user import User
from app.schemas.analytics import (
    CourierComparison,
    PerformanceBulkCreate,
    PerformanceCreate,
    PerformanceList,
    PerformanceResponse,
    PerformanceStats,
    PerformanceTrend,
    PerformanceUpdate,
    TopPerformer,
)
from app.services.analytics import performance_service

router = APIRouter()


@router.get("/", response_model=List[PerformanceList])
def get_performance_records(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    courier_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
):
    """Get performance records with optional filtering"""
    if start_date and end_date:
        return performance_service.get_by_date_range(
            db,
            start_date=start_date,
            end_date=end_date,
            courier_id=courier_id,
            skip=skip,
            limit=limit,
        )
    elif courier_id:
        return performance_service.get_by_courier(db, courier_id=courier_id, skip=skip, limit=limit)
    else:
        filters = {}
        if courier_id:
            filters["courier_id"] = courier_id
        return performance_service.get_multi(db, skip=skip, limit=limit, filters=filters)


@router.get("/courier/{courier_id}", response_model=List[PerformanceList])
def get_courier_performance(
    courier_id: int,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get all performance records for a specific courier"""
    return performance_service.get_by_courier(db, courier_id=courier_id, skip=skip, limit=limit)


@router.get("/date/{performance_date}", response_model=List[PerformanceList])
def get_performance_by_date(
    performance_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all performance records for a specific date"""
    return performance_service.get_by_date(db, performance_date=performance_date)


@router.get("/statistics", response_model=dict)
def get_performance_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get overall performance statistics"""
    return performance_service.get_statistics(db)


@router.get("/courier/{courier_id}/metrics", response_model=PerformanceStats)
def get_courier_metrics(
    courier_id: int,
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Calculate performance metrics for a courier within date range"""
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="end_date must be after start_date")

    return performance_service.calculate_metrics(
        db, courier_id=courier_id, start_date=start_date, end_date=end_date
    )


@router.get("/top-performers", response_model=List[TopPerformer])
def get_top_performers(
    db: Session = Depends(get_db),
    start_date: date = Query(default=None, description="Start date (defaults to 30 days ago)"),
    end_date: date = Query(default=None, description="End date (defaults to today)"),
    limit: int = Query(10, ge=1, le=100, description="Number of top performers"),
    metric: str = Query(
        "orders", regex="^(orders|revenue|efficiency|rating)$", description="Metric to rank by"
    ),
    current_user: User = Depends(get_current_user),
):
    """Get top performing couriers for a date range"""
    # Default to last 30 days if dates not provided
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    if end_date < start_date:
        raise HTTPException(status_code=400, detail="end_date must be after start_date")

    return performance_service.get_top_performers(
        db, start_date=start_date, end_date=end_date, limit=limit, metric=metric
    )


@router.get("/courier/{courier_id}/trends", response_model=List[PerformanceTrend])
def get_performance_trends(
    courier_id: int,
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get performance trends over time for a courier"""
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="end_date must be after start_date")

    return performance_service.get_performance_trends(
        db, courier_id=courier_id, start_date=start_date, end_date=end_date
    )


@router.post("/compare", response_model=List[CourierComparison])
def compare_couriers(
    courier_ids: List[int] = Query(
        ..., min_items=2, max_items=10, description="Courier IDs to compare"
    ),
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Compare performance metrics for multiple couriers"""
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="end_date must be after start_date")

    return performance_service.compare_couriers(
        db, courier_ids=courier_ids, start_date=start_date, end_date=end_date
    )


@router.get("/{performance_id}", response_model=PerformanceResponse)
def get_performance_record(
    performance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get performance record by ID"""
    performance = performance_service.get(db, id=performance_id)
    if not performance:
        raise HTTPException(status_code=404, detail="Performance record not found")
    return performance


@router.post("/", response_model=PerformanceResponse, status_code=status.HTTP_201_CREATED)
def create_performance_record(
    performance_in: PerformanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new performance record"""
    # Check if record already exists for this courier and date
    existing = performance_service.get_by_courier_and_date(
        db, courier_id=performance_in.courier_id, performance_date=performance_in.date
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Performance record already exists for courier {performance_in.courier_id} on {performance_in.date}",
        )

    return performance_service.create(db, obj_in=performance_in)


@router.post("/bulk", response_model=dict, status_code=status.HTTP_201_CREATED)
def bulk_create_performance_records(
    bulk_data: PerformanceBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Bulk create performance records"""
    created = performance_service.bulk_create(db, obj_list=bulk_data.records)
    return {"message": f"Created {len(created)} performance records", "count": len(created)}


@router.post("/upsert", response_model=PerformanceResponse)
def upsert_performance_record(
    performance_in: PerformanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create or update performance record (upsert)"""
    return performance_service.upsert_performance(
        db,
        courier_id=performance_in.courier_id,
        performance_date=performance_in.date,
        data=performance_in,
    )


@router.put("/{performance_id}", response_model=PerformanceResponse)
def update_performance_record(
    performance_id: int,
    performance_in: PerformanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update performance record"""
    performance = performance_service.get(db, id=performance_id)
    if not performance:
        raise HTTPException(status_code=404, detail="Performance record not found")

    return performance_service.update(db, db_obj=performance, obj_in=performance_in)


@router.delete("/{performance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_performance_record(
    performance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete performance record"""
    performance = performance_service.get(db, id=performance_id)
    if not performance:
        raise HTTPException(status_code=404, detail="Performance record not found")

    performance_service.delete(db, id=performance_id)
    return None


@router.delete(
    "/courier/{courier_id}/date/{performance_date}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_performance_by_courier_date(
    courier_id: int,
    performance_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete performance record by courier and date"""
    performance = performance_service.get_by_courier_and_date(
        db, courier_id=courier_id, performance_date=performance_date
    )

    if not performance:
        raise HTTPException(
            status_code=404,
            detail=f"Performance record not found for courier {courier_id} on {performance_date}",
        )

    performance_service.delete(db, id=performance.id)
    return None
