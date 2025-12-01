from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from datetime import date, timedelta
from decimal import Decimal

from app.models.analytics import PerformanceData
from app.models.fleet import Courier
from app.schemas.analytics import (
    PerformanceCreate,
    PerformanceUpdate,
    PerformanceStats,
    TopPerformer,
    PerformanceTrend,
    CourierComparison,
)
from app.services.base import CRUDBase


class PerformanceService(CRUDBase[PerformanceData, PerformanceCreate, PerformanceUpdate]):
    """Service for Performance operations with analytics logic"""

    def get_by_courier(
        self,
        db: Session,
        courier_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "-date"
    ) -> List[PerformanceData]:
        """Get performance records for a specific courier"""
        return self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={"courier_id": courier_id},
            order_by=order_by
        )

    def get_by_date(
        self,
        db: Session,
        performance_date: date
    ) -> List[PerformanceData]:
        """Get all performance records for a specific date"""
        return db.query(PerformanceData).filter(
            PerformanceData.date == performance_date
        ).all()

    def get_by_date_range(
        self,
        db: Session,
        start_date: date,
        end_date: date,
        *,
        courier_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 1000
    ) -> List[PerformanceData]:
        """Get performance records within a date range"""
        query = db.query(PerformanceData).filter(
            and_(
                PerformanceData.date >= start_date,
                PerformanceData.date <= end_date
            )
        )

        if courier_id:
            query = query.filter(PerformanceData.courier_id == courier_id)

        return query.order_by(PerformanceData.date.desc()).offset(skip).limit(limit).all()

    def get_by_courier_and_date(
        self,
        db: Session,
        courier_id: int,
        performance_date: date
    ) -> Optional[PerformanceData]:
        """Get performance record for specific courier and date"""
        return db.query(PerformanceData).filter(
            and_(
                PerformanceData.courier_id == courier_id,
                PerformanceData.date == performance_date
            )
        ).first()

    def calculate_metrics(
        self,
        db: Session,
        courier_id: int,
        start_date: date,
        end_date: date
    ) -> PerformanceStats:
        """Calculate performance metrics for a courier within date range"""
        records = self.get_by_date_range(
            db,
            start_date=start_date,
            end_date=end_date,
            courier_id=courier_id
        )

        if not records:
            return PerformanceStats(
                courier_id=courier_id,
                period_start=start_date,
                period_end=end_date
            )

        # Aggregate metrics
        total_completed = sum(r.orders_completed for r in records)
        total_failed = sum(r.orders_failed for r in records)
        total_on_time = sum(r.on_time_deliveries for r in records)
        total_distance = sum(r.distance_covered_km for r in records)
        total_revenue = sum(r.revenue_generated for r in records)
        total_cod = sum(r.cod_collected for r in records)
        total_hours = sum(r.working_hours for r in records)

        # Calculate averages
        working_days = len(records)
        avg_rating = sum(r.average_rating for r in records) / working_days if working_days > 0 else Decimal("0.0")
        avg_efficiency = sum(r.efficiency_score for r in records) / working_days if working_days > 0 else Decimal("0.0")
        avg_orders_per_day = Decimal(str(total_completed)) / working_days if working_days > 0 else Decimal("0.0")

        # Calculate percentages
        on_time_percentage = (total_on_time / total_completed * 100) if total_completed > 0 else 0.0
        success_rate = (total_completed / (total_completed + total_failed) * 100) if (total_completed + total_failed) > 0 else 0.0

        return PerformanceStats(
            courier_id=courier_id,
            period_start=start_date,
            period_end=end_date,
            total_orders_completed=total_completed,
            total_orders_failed=total_failed,
            total_distance_km=Decimal(str(total_distance)),
            total_revenue=Decimal(str(total_revenue)),
            total_cod_collected=Decimal(str(total_cod)),
            average_rating=Decimal(str(avg_rating)),
            average_efficiency_score=Decimal(str(avg_efficiency)),
            average_orders_per_day=avg_orders_per_day,
            on_time_percentage=float(on_time_percentage),
            success_rate=float(success_rate),
            working_days=working_days,
            total_working_hours=Decimal(str(total_hours))
        )

    def get_top_performers(
        self,
        db: Session,
        start_date: date,
        end_date: date,
        *,
        limit: int = 10,
        metric: str = "orders"  # orders, revenue, efficiency, rating
    ) -> List[TopPerformer]:
        """Get top performing couriers for a date range"""

        # Aggregate performance data grouped by courier
        query = db.query(
            PerformanceData.courier_id,
            Courier.barq_id,
            Courier.full_name,
            func.sum(PerformanceData.orders_completed).label('total_orders'),
            func.sum(PerformanceData.revenue_generated).label('total_revenue'),
            func.avg(PerformanceData.average_rating).label('avg_rating'),
            func.avg(PerformanceData.efficiency_score).label('avg_efficiency'),
            func.sum(PerformanceData.on_time_deliveries).label('total_on_time'),
            func.sum(PerformanceData.orders_completed + PerformanceData.orders_failed).label('total_all_orders')
        ).join(
            Courier, PerformanceData.courier_id == Courier.id
        ).filter(
            and_(
                PerformanceData.date >= start_date,
                PerformanceData.date <= end_date
            )
        ).group_by(
            PerformanceData.courier_id,
            Courier.barq_id,
            Courier.full_name
        )

        # Order by selected metric
        if metric == "revenue":
            query = query.order_by(desc('total_revenue'))
        elif metric == "efficiency":
            query = query.order_by(desc('avg_efficiency'))
        elif metric == "rating":
            query = query.order_by(desc('avg_rating'))
        else:  # orders
            query = query.order_by(desc('total_orders'))

        results = query.limit(limit).all()

        # Build response
        performers = []
        for rank, result in enumerate(results, start=1):
            on_time_rate = (float(result.total_on_time) / float(result.total_orders) * 100) if result.total_orders > 0 else 0.0

            performers.append(TopPerformer(
                courier_id=result.courier_id,
                courier_barq_id=result.barq_id,
                courier_name=result.full_name,
                total_orders=result.total_orders or 0,
                total_revenue=Decimal(str(result.total_revenue or 0)),
                average_rating=Decimal(str(result.avg_rating or 0)),
                efficiency_score=Decimal(str(result.avg_efficiency or 0)),
                on_time_rate=on_time_rate,
                rank=rank
            ))

        return performers

    def get_performance_trends(
        self,
        db: Session,
        courier_id: int,
        start_date: date,
        end_date: date
    ) -> List[PerformanceTrend]:
        """Get performance trends over time for a courier"""
        records = self.get_by_date_range(
            db,
            start_date=start_date,
            end_date=end_date,
            courier_id=courier_id
        )

        trends = [
            PerformanceTrend(
                date=record.date,
                orders_completed=record.orders_completed,
                revenue_generated=record.revenue_generated,
                efficiency_score=record.efficiency_score,
                average_rating=record.average_rating
            )
            for record in sorted(records, key=lambda x: x.date)
        ]

        return trends

    def compare_couriers(
        self,
        db: Session,
        courier_ids: List[int],
        start_date: date,
        end_date: date
    ) -> List[CourierComparison]:
        """Compare performance metrics for multiple couriers"""
        comparisons = []

        for courier_id in courier_ids:
            courier = db.query(Courier).filter(Courier.id == courier_id).first()
            if not courier:
                continue

            records = self.get_by_date_range(
                db,
                start_date=start_date,
                end_date=end_date,
                courier_id=courier_id
            )

            if not records:
                continue

            total_completed = sum(r.orders_completed for r in records)
            total_failed = sum(r.orders_failed for r in records)
            total_on_time = sum(r.on_time_deliveries for r in records)
            total_revenue = sum(r.revenue_generated for r in records)
            total_distance = sum(r.distance_covered_km for r in records)
            avg_rating = sum(r.average_rating for r in records) / len(records)
            avg_efficiency = sum(r.efficiency_score for r in records) / len(records)

            success_rate = (total_completed / (total_completed + total_failed) * 100) if (total_completed + total_failed) > 0 else 0.0
            on_time_rate = (total_on_time / total_completed * 100) if total_completed > 0 else 0.0

            comparisons.append(CourierComparison(
                courier_id=courier_id,
                courier_barq_id=courier.barq_id,
                courier_name=courier.full_name,
                orders_completed=total_completed,
                orders_failed=total_failed,
                success_rate=float(success_rate),
                total_revenue=Decimal(str(total_revenue)),
                total_distance_km=Decimal(str(total_distance)),
                average_rating=Decimal(str(avg_rating)),
                efficiency_score=Decimal(str(avg_efficiency)),
                on_time_rate=float(on_time_rate)
            ))

        return comparisons

    def get_statistics(self, db: Session) -> Dict[str, Any]:
        """Get overall performance statistics"""
        total_records = db.query(func.count(PerformanceData.id)).scalar()

        total_orders = db.query(
            func.sum(PerformanceData.orders_completed)
        ).scalar() or 0

        total_revenue = db.query(
            func.sum(PerformanceData.revenue_generated)
        ).scalar() or Decimal("0.0")

        avg_efficiency = db.query(
            func.avg(PerformanceData.efficiency_score)
        ).scalar() or Decimal("0.0")

        avg_rating = db.query(
            func.avg(PerformanceData.average_rating)
        ).scalar() or Decimal("0.0")

        return {
            "total_records": total_records,
            "total_orders_completed": total_orders,
            "total_revenue_generated": float(total_revenue),
            "average_efficiency_score": float(avg_efficiency),
            "average_rating": float(avg_rating),
        }

    def upsert_performance(
        self,
        db: Session,
        courier_id: int,
        performance_date: date,
        data: PerformanceCreate
    ) -> PerformanceData:
        """Create or update performance record for courier and date"""
        existing = self.get_by_courier_and_date(db, courier_id, performance_date)

        if existing:
            return self.update(db, db_obj=existing, obj_in=data)
        else:
            return self.create(db, obj_in=data)


# Create instance
performance_service = PerformanceService(PerformanceData)
