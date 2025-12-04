import csv
import io
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.fleet.courier import Courier

router = APIRouter()


class CourierPerformanceMetrics(BaseModel):
    """Courier performance metrics"""

    courier_id: int
    barq_id: str
    full_name: str
    total_deliveries: int
    performance_score: Decimal
    avg_rating: Decimal = Decimal("0.0")
    completed_deliveries: int = 0
    failed_deliveries: int = 0
    success_rate: Decimal = Decimal("0.0")

    class Config:
        from_attributes = True


@router.get("/", response_model=List[CourierPerformanceMetrics])
def get_courier_performance(
    skip: int = 0,
    limit: int = 100,
    start_date: date = Query(default=None, description="Filter from this date"),
    end_date: date = Query(default=None, description="Filter until this date"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get courier performance metrics"""

    # If no date range provided, default to last 30 days
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # Query couriers with their basic performance metrics
    couriers = db.query(Courier).offset(skip).limit(limit).all()

    results = []
    for courier in couriers:
        # Calculate success rate
        success_rate = Decimal("0.0")
        if courier.total_deliveries > 0:
            success_rate = (
                Decimal(str(courier.total_deliveries - 0)) / Decimal(str(courier.total_deliveries))
            ) * Decimal("100")

        results.append(
            CourierPerformanceMetrics(
                courier_id=courier.id,
                barq_id=courier.barq_id,
                full_name=courier.full_name,
                total_deliveries=courier.total_deliveries or 0,
                performance_score=courier.performance_score or Decimal("0.0"),
                avg_rating=Decimal("0.0"),  # This would come from delivery ratings
                completed_deliveries=courier.total_deliveries or 0,
                failed_deliveries=0,
                success_rate=success_rate,
            )
        )

    return results


@router.get("/export")
def export_courier_performance(
    start_date: date = Query(default=None, description="Filter from this date"),
    end_date: date = Query(default=None, description="Filter until this date"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Export courier performance data to Excel (CSV format)"""

    # If no date range provided, default to last 30 days
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # Get all couriers
    couriers = db.query(Courier).all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(
        [
            "Courier ID",
            "BARQ ID",
            "Full Name",
            "Total Deliveries",
            "Performance Score",
            "Avg Rating",
            "Completed Deliveries",
            "Failed Deliveries",
            "Success Rate (%)",
        ]
    )

    # Write data
    for courier in couriers:
        success_rate = 0.0
        if courier.total_deliveries and courier.total_deliveries > 0:
            success_rate = ((courier.total_deliveries - 0) / courier.total_deliveries) * 100

        writer.writerow(
            [
                courier.id,
                courier.barq_id,
                courier.full_name,
                courier.total_deliveries or 0,
                float(courier.performance_score or 0),
                0.0,  # avg_rating placeholder
                courier.total_deliveries or 0,
                0,  # failed_deliveries placeholder
                f"{success_rate:.2f}",
            ]
        )

    # Prepare response
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=courier_performance_{start_date}_{end_date}.csv"
        },
    )
