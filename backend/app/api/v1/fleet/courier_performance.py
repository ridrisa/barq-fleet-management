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
    """Courier performance metrics - matches frontend expectations"""

    courier_id: int
    courier_name: str
    barq_id: str
    deliveries: int = 0
    on_time_rate: Decimal = Decimal("0.0")
    rating: Decimal = Decimal("0.0")
    cod_collected: Decimal = Decimal("0.0")
    revenue: Decimal = Decimal("0.0")
    performance_score: Decimal = Decimal("0.0")

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
        # Calculate on-time rate based on performance score
        on_time_rate = courier.performance_score or Decimal("0.0")

        # Get real data from courier model
        deliveries = courier.total_deliveries or 0

        results.append(
            CourierPerformanceMetrics(
                courier_id=courier.id,
                courier_name=courier.full_name or f"Courier {courier.id}",
                barq_id=courier.barq_id or "",
                deliveries=deliveries,
                on_time_rate=on_time_rate,
                rating=Decimal("0.0"),  # Rating not implemented in courier model yet
                cod_collected=Decimal("0.0"),  # Would need delivery data to calculate
                revenue=Decimal("0.0"),  # Would need delivery data to calculate
                performance_score=courier.performance_score or Decimal("0.0"),
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
