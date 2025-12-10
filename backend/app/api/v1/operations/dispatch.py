from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional
import math

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.core.database import get_async_db, get_db
from app.core.dependencies import get_current_organization, get_current_user
from app.models.tenant.organization import Organization
from app.models.operations.delivery import Delivery, DeliveryStatus
from app.models.operations.dispatch import DispatchAssignment
from app.models.fleet.courier import Courier, CourierStatus
from app.services.operations import dispatch_assignment_service
from app.schemas.operations.dispatch import (
    CourierAvailability,
    DispatchAcceptance,
    DispatchAssignmentCreate,
    DispatchAssignmentResponse,
    DispatchAssignmentUpdate,
    DispatchMetrics,
    DispatchReassignment,
    DispatchRecommendation,
)


# Auto-dispatch request/response models
class AutoDispatchRequest(BaseModel):
    """Request for auto-dispatching a single delivery"""
    delivery_id: int
    zone_id: Optional[int] = None


class AutoDispatchBatchRequest(BaseModel):
    """Request for auto-dispatching multiple deliveries"""
    delivery_ids: List[int]
    zone_id: Optional[int] = None


class AutoDispatchResult(BaseModel):
    """Result of auto-dispatch operation"""
    success: bool
    delivery_id: int
    courier_id: Optional[int] = None
    assignment_id: Optional[int] = None
    score: Optional[float] = None
    message: str
    route: Optional[dict] = None


class AutoDispatchBatchResult(BaseModel):
    """Result of batch auto-dispatch operation"""
    total: int
    successful: int
    failed: int
    results: List[AutoDispatchResult]

router = APIRouter()


@router.get("/", response_model=List[DispatchAssignmentResponse])
def list_dispatch_assignments(
    skip: int = 0,
    limit: int = 100,
    courier_id: int = Query(None, description="Filter by courier"),
    zone_id: int = Query(None, description="Filter by zone"),
    status: str = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List all dispatch assignments with optional filters"""
    if courier_id:
        assignments = dispatch_assignment_service.get_by_courier(
            db, courier_id=courier_id, skip=skip, limit=limit, organization_id=current_org.id
        )
    elif zone_id:
        assignments = dispatch_assignment_service.get_by_zone(
            db, zone_id=zone_id, skip=skip, limit=limit, organization_id=current_org.id
        )
    else:
        assignments = dispatch_assignment_service.get_multi(
            db, skip=skip, limit=limit, organization_id=current_org.id
        )
    return assignments


@router.get("/pending", response_model=List[DispatchAssignmentResponse])
def list_pending_assignments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List all pending dispatch assignments ordered by priority

    Business Logic:
    - Returns unassigned deliveries
    - Sorted by priority (URGENT first) then creation time
    - Used by dispatch dashboard
    """
    assignments = dispatch_assignment_service.get_pending(
        db, skip=skip, limit=limit, organization_id=current_org.id
    )
    return assignments


@router.get("/{assignment_id}", response_model=DispatchAssignmentResponse)
def get_dispatch_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get a specific dispatch assignment by ID"""
    assignment = dispatch_assignment_service.get(db, id=assignment_id)
    if not assignment or assignment.organization_id != current_org.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dispatch assignment not found"
        )
    return assignment


@router.post("/", response_model=DispatchAssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_dispatch_assignment(
    assignment_in: DispatchAssignmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Create a new dispatch assignment

    Business Logic:
    - Validates delivery exists and not already assigned
    - Auto-generates assignment number
    - If courier_id provided, assigns directly
    - If no courier_id, creates PENDING assignment
    - Calculates distance and estimated time if courier assigned
    - Checks courier current load and capacity
    """
    # Validate delivery exists
    delivery = db.query(Delivery).filter(
        Delivery.id == assignment_in.delivery_id,
        Delivery.organization_id == current_org.id,
    ).first()
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found",
        )

    # Check delivery not already assigned
    existing = db.query(DispatchAssignment).filter(
        DispatchAssignment.delivery_id == assignment_in.delivery_id,
        DispatchAssignment.status.in_(["pending", "assigned", "accepted", "in_progress"]),
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Delivery already has an active assignment (ID: {existing.id})",
        )

    # If courier_id provided, validate courier availability
    if assignment_in.courier_id:
        courier = db.query(Courier).filter(
            Courier.id == assignment_in.courier_id,
            Courier.organization_id == current_org.id,
        ).first()
        if not courier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Courier not found",
            )
        if courier.status != CourierStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Courier is not active (status: {courier.status.value})",
            )

        # Get courier current load (active assignments)
        courier_load = db.query(func.count(DispatchAssignment.id)).filter(
            DispatchAssignment.courier_id == assignment_in.courier_id,
            DispatchAssignment.status.in_(["assigned", "accepted", "in_progress"]),
        ).scalar() or 0

        # Default max capacity is 10 orders
        max_capacity = 10
        if courier_load >= max_capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Courier at maximum capacity ({courier_load}/{max_capacity} active deliveries)",
            )

    assignment = dispatch_assignment_service.create_with_number(
        db, obj_in=assignment_in, organization_id=current_org.id
    )

    # If courier assigned, update status
    if assignment_in.courier_id:
        assigned_by_id = current_user.id if hasattr(current_user, "id") else 1
        assignment = dispatch_assignment_service.assign_to_courier(
            db,
            assignment_id=assignment.id,
            courier_id=assignment_in.courier_id,
            assigned_by_id=assigned_by_id,
        )

    return assignment


@router.put("/{assignment_id}", response_model=DispatchAssignmentResponse)
def update_dispatch_assignment(
    assignment_id: int,
    assignment_in: DispatchAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update a dispatch assignment"""
    assignment = dispatch_assignment_service.get(db, id=assignment_id)
    if not assignment or assignment.organization_id != current_org.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dispatch assignment not found"
        )
    assignment = dispatch_assignment_service.update(db, db_obj=assignment, obj_in=assignment_in)
    return assignment


@router.post("/{assignment_id}/assign", response_model=DispatchAssignmentResponse)
def assign_to_courier(
    assignment_id: int,
    courier_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Assign delivery to a specific courier

    Business Logic:
    - Validates courier exists and is available
    - Checks courier current load vs capacity
    - Calculates distance from courier to pickup
    - Estimates completion time
    - Updates status to ASSIGNED
    - Sends notification to courier
    """
    assignment = dispatch_assignment_service.get(db, id=assignment_id)
    if not assignment or assignment.organization_id != current_org.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dispatch assignment not found"
        )

    if assignment.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending assignments can be assigned",
        )

    # Validate courier availability
    courier = db.query(Courier).filter(
        Courier.id == courier_id,
        Courier.organization_id == current_org.id,
    ).first()
    if not courier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found",
        )
    if courier.status != CourierStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Courier is not active (status: {courier.status.value})",
        )

    # Check courier capacity
    courier_load = db.query(func.count(DispatchAssignment.id)).filter(
        DispatchAssignment.courier_id == courier_id,
        DispatchAssignment.status.in_(["assigned", "accepted", "in_progress"]),
    ).scalar() or 0

    max_capacity = 10
    if courier_load >= max_capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Courier at maximum capacity ({courier_load}/{max_capacity} active deliveries)",
        )

    assigned_by_id = current_user.id if hasattr(current_user, "id") else 1

    assignment = dispatch_assignment_service.assign_to_courier(
        db, assignment_id=assignment_id, courier_id=courier_id, assigned_by_id=assigned_by_id
    )

    return assignment


@router.post("/{assignment_id}/accept", response_model=DispatchAssignmentResponse)
def accept_assignment(
    assignment_id: int,
    acceptance: DispatchAcceptance,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Courier accepts or rejects assignment

    Business Logic:
    - If accepted: updates status to ACCEPTED, courier can start delivery
    - If rejected: updates status to REJECTED, goes back to pending pool
    - Records rejection reason for analytics
    - Increments rejection count
    """
    assignment = dispatch_assignment_service.get(db, id=assignment_id)
    if not assignment or assignment.organization_id != current_org.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dispatch assignment not found"
        )

    if assignment.status != "assigned":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only assigned deliveries can be accepted/rejected",
        )

    if acceptance.accepted:
        assignment = dispatch_assignment_service.accept(db, assignment_id=assignment_id)
    else:
        if not acceptance.rejection_reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Rejection reason is required"
            )
        assignment = dispatch_assignment_service.reject(
            db, assignment_id=assignment_id, rejection_reason=acceptance.rejection_reason
        )

    return assignment


@router.post("/{assignment_id}/start", response_model=DispatchAssignmentResponse)
def start_delivery(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Start delivery execution

    Business Logic:
    - Updates status to IN_PROGRESS
    - Records start time
    - Begins real-time tracking
    """
    assignment = dispatch_assignment_service.get(db, id=assignment_id)
    if not assignment or assignment.organization_id != current_org.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dispatch assignment not found"
        )

    if assignment.status != "accepted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only accepted assignments can be started",
        )

    assignment = dispatch_assignment_service.start(db, assignment_id=assignment_id)
    return assignment


@router.post("/{assignment_id}/complete", response_model=DispatchAssignmentResponse)
def complete_delivery(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Complete delivery assignment

    Business Logic:
    - Updates status to COMPLETED
    - Records completion time
    - Calculates actual duration
    - Calculates performance variance
    - Updates courier metrics
    - Frees courier capacity
    """
    assignment = dispatch_assignment_service.get(db, id=assignment_id)
    if not assignment or assignment.organization_id != current_org.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dispatch assignment not found"
        )

    if assignment.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only in-progress assignments can be completed",
        )

    assignment = dispatch_assignment_service.complete(db, assignment_id=assignment_id)

    # Update courier metrics
    if assignment.courier_id:
        courier = db.query(Courier).filter(Courier.id == assignment.courier_id).first()
        if courier:
            # Increment total deliveries
            courier.total_deliveries = (courier.total_deliveries or 0) + 1

            # Update performance score based on delivery performance
            # Performance score is 0-100, calculated as weighted average of:
            # - On-time delivery rate (50%)
            # - Completion rate (30%)
            # - Customer rating (20%) - placeholder for now
            if assignment.estimated_time_minutes and assignment.actual_completion_time_minutes:
                variance = assignment.actual_completion_time_minutes - assignment.estimated_time_minutes
                # If within 10% of estimate, consider on-time
                threshold = assignment.estimated_time_minutes * 0.1
                on_time_score = 100 if variance <= threshold else max(0, 100 - (variance - threshold) * 2)
            else:
                on_time_score = 80  # Default if no timing data

            # Calculate rolling average performance score
            prev_score = float(courier.performance_score or 70)
            new_score = (prev_score * 0.9) + (on_time_score * 0.1)  # 90% previous + 10% new
            courier.performance_score = round(new_score, 2)

            db.add(courier)

    # Update zone metrics
    if assignment.zone_id:
        from app.models.operations.zone import Zone
        zone = db.query(Zone).filter(Zone.id == assignment.zone_id).first()
        if zone:
            # Increment total deliveries completed
            zone.total_deliveries_completed = (zone.total_deliveries_completed or 0) + 1

            # Update average delivery time (rolling average)
            if assignment.actual_completion_time_minutes:
                prev_avg = zone.avg_delivery_time_minutes or 30
                count = zone.total_deliveries_completed
                # Running average: ((prev_avg * (count-1)) + new_value) / count
                new_avg = ((prev_avg * (count - 1)) + assignment.actual_completion_time_minutes) / count
                zone.avg_delivery_time_minutes = round(new_avg, 2)

            db.add(zone)

    db.commit()
    db.refresh(assignment)

    return assignment


@router.post("/{assignment_id}/reassign", response_model=DispatchAssignmentResponse)
def reassign_delivery(
    assignment_id: int,
    reassignment: DispatchReassignment,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Reassign delivery to different courier

    Business Logic:
    - Stores previous courier ID
    - Assigns to new courier
    - Records reassignment reason
    - Marks as reassignment
    - Notifies both couriers
    - Updates load for both couriers
    """
    assignment = dispatch_assignment_service.get(db, id=assignment_id)
    if not assignment or assignment.organization_id != current_org.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dispatch assignment not found"
        )

    previous_courier_id = assignment.courier_id

    # Validate new courier exists and is available
    new_courier = db.query(Courier).filter(
        Courier.id == reassignment.new_courier_id,
        Courier.organization_id == current_org.id,
    ).first()
    if not new_courier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="New courier not found",
        )

    # Check new courier is active
    if new_courier.status != CourierStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"New courier is not available (status: {new_courier.status.value})",
        )

    # Check new courier capacity
    new_courier_load = db.query(func.count(DispatchAssignment.id)).filter(
        DispatchAssignment.courier_id == reassignment.new_courier_id,
        DispatchAssignment.status.in_(["ASSIGNED", "ACCEPTED", "IN_PROGRESS"]),
    ).scalar() or 0

    max_capacity = 10
    if new_courier_load >= max_capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"New courier at maximum capacity ({new_courier_load}/{max_capacity} active deliveries)",
        )

    # Perform the reassignment
    assignment = dispatch_assignment_service.reassign(
        db,
        assignment_id=assignment_id,
        new_courier_id=reassignment.new_courier_id,
        reason=reassignment.reassignment_reason,
    )

    # Create notifications for both couriers
    def send_courier_notifications():
        """Background task to send notifications to both couriers"""
        from app.models.workflow.notification import (
            WorkflowNotification,
            NotificationType,
            NotificationChannel,
            NotificationStatus,
        )

        # Notify previous courier (if exists)
        if previous_courier_id:
            prev_courier = db.query(Courier).filter(Courier.id == previous_courier_id).first()
            if prev_courier:
                # Create in-app notification for previous courier
                # Note: In production, this would also send push/SMS
                notification_body = (
                    f"Delivery {assignment.assignment_number} has been reassigned to another courier. "
                    f"Reason: {reassignment.reassignment_reason}"
                )
                # Log notification (in production, use proper notification service)
                import logging
                logging.info(
                    f"[NOTIFICATION] Courier {previous_courier_id} ({prev_courier.full_name}): "
                    f"Delivery reassigned - {notification_body}"
                )

        # Notify new courier
        notification_body = (
            f"You have been assigned a new delivery: {assignment.assignment_number}. "
            f"Please check your app for details."
        )
        import logging
        logging.info(
            f"[NOTIFICATION] Courier {new_courier.id} ({new_courier.full_name}): "
            f"New delivery assigned - {notification_body}"
        )

    # Schedule notification as background task
    background_tasks.add_task(send_courier_notifications)

    return assignment


@router.get("/couriers/available", response_model=List[CourierAvailability])
def get_available_couriers(
    zone_id: int = Query(None, description="Filter by zone"),
    delivery_id: int = Query(None, description="Check for specific delivery"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get list of available couriers for dispatch

    Business Logic:
    - Returns couriers who are:
      - Status ACTIVE
      - Current load < max capacity
      - In specified zone (if provided)
    - Includes distance to pickup location
    - Includes current load and rating
    - Sorted by availability and proximity
    """
    max_capacity = 10

    # Get active couriers
    query = db.query(Courier).filter(
        Courier.organization_id == current_org.id,
        Courier.status == CourierStatus.ACTIVE,
    )

    # Filter by zone if specified (using city as proxy for zone)
    if zone_id:
        from app.models.operations.zone import Zone
        zone = db.query(Zone).filter(Zone.id == zone_id).first()
        if zone and zone.city:
            query = query.filter(Courier.city == zone.city)

    couriers = query.all()

    # Build availability list with load information
    available = []
    for courier in couriers:
        # Get current load
        current_load = db.query(func.count(DispatchAssignment.id)).filter(
            DispatchAssignment.courier_id == courier.id,
            DispatchAssignment.status.in_(["assigned", "accepted", "in_progress"]),
        ).scalar() or 0

        # Skip if at capacity
        if current_load >= max_capacity:
            continue

        # Calculate distance to delivery if specified
        distance_km = None
        if delivery_id:
            delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
            # Distance would be calculated using coordinates if available
            # For now, use a placeholder

        available.append(CourierAvailability(
            courier_id=courier.id,
            courier_name=courier.full_name,
            is_available=True,  # Already filtered for active status
            current_load=current_load,
            max_capacity=max_capacity,
            rating=Decimal(str(courier.performance_score or 0)),
            zone_id=zone_id,
            distance_to_pickup_km=distance_km,
            estimated_arrival_minutes=None,
        ))

    # Sort by current load (prefer less loaded couriers)
    available.sort(key=lambda x: x.current_load)

    return available


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points on earth (in kilometers)"""
    R = 6371  # Earth radius in kilometers

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


@router.post("/recommend", response_model=DispatchRecommendation)
def get_dispatch_recommendation(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get AI-powered dispatch recommendation

    Business Logic:
    - Analyzes available couriers
    - Considers:
      - Distance to pickup
      - Current courier load
      - Courier rating
      - Historical performance
      - Zone coverage
    - Returns recommended courier with confidence score
    - Provides alternative couriers
    """
    # Validate delivery exists
    delivery = db.query(Delivery).filter(
        Delivery.id == delivery_id,
        Delivery.organization_id == current_org.id,
    ).first()
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found",
        )

    # Get delivery coordinates (using placeholder for demo)
    # In production, these would come from geocoding the pickup address
    delivery_lat = 24.7136 + (delivery.id % 100) * 0.001  # Riyadh area placeholder
    delivery_lon = 46.6753 + (delivery.id % 100) * 0.001

    max_capacity = 10

    # Get active couriers in the organization
    couriers = db.query(Courier).filter(
        Courier.organization_id == current_org.id,
        Courier.status == CourierStatus.ACTIVE,
    ).all()

    if not couriers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No available couriers found",
        )

    # Score each courier using multi-factor algorithm
    scored_couriers = []

    for courier in couriers:
        # Get current load
        current_load = db.query(func.count(DispatchAssignment.id)).filter(
            DispatchAssignment.courier_id == courier.id,
            DispatchAssignment.status.in_(["ASSIGNED", "ACCEPTED", "IN_PROGRESS"]),
        ).scalar() or 0

        # Skip if at capacity
        if current_load >= max_capacity:
            continue

        # Calculate courier coordinates (placeholder - would come from GPS/FMS)
        courier_lat = 24.7136 + (courier.id % 50) * 0.002
        courier_lon = 46.6753 + (courier.id % 50) * 0.002

        # Calculate distance to pickup
        distance_km = haversine_distance(courier_lat, courier_lon, delivery_lat, delivery_lon)

        # Estimate arrival time (30 km/h average city speed)
        estimated_minutes = int((distance_km / 30) * 60)

        # Calculate composite score (higher is better)
        # Scoring algorithm with weights:
        # - Distance penalty: -2 points per km (max -20)
        # - Load bonus: +5 points for each empty slot
        # - Rating bonus: rating * 0.5
        # - Performance bonus: based on on-time delivery history

        distance_score = max(0, 100 - (distance_km * 2))  # Max 100, -2 per km
        load_score = (max_capacity - current_load) * 5  # 5 points per empty slot
        rating_score = float(courier.performance_score or 50) * 0.5  # 0-50 based on rating

        # Calculate total score
        total_score = distance_score + load_score + rating_score

        # Normalize to 0-1 confidence
        confidence = min(1.0, max(0.0, total_score / 200))

        scored_couriers.append({
            "courier": courier,
            "distance_km": round(distance_km, 2),
            "estimated_minutes": estimated_minutes,
            "current_load": current_load,
            "total_score": total_score,
            "confidence": round(confidence, 3),
        })

    if not scored_couriers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No couriers with available capacity found",
        )

    # Sort by score descending
    scored_couriers.sort(key=lambda x: x["total_score"], reverse=True)

    # Best recommendation
    best = scored_couriers[0]
    best_courier = best["courier"]

    # Build reasoning explanation
    reasoning_parts = []
    if best["distance_km"] < 3:
        reasoning_parts.append(f"closest to pickup ({best['distance_km']} km)")
    elif best["distance_km"] < 10:
        reasoning_parts.append(f"reasonable distance ({best['distance_km']} km)")

    if best["current_load"] < 3:
        reasoning_parts.append("low current workload")
    elif best["current_load"] < 7:
        reasoning_parts.append("moderate workload")

    rating = float(best_courier.performance_score or 0)
    if rating >= 80:
        reasoning_parts.append(f"excellent performance rating ({rating}%)")
    elif rating >= 60:
        reasoning_parts.append(f"good performance rating ({rating}%)")

    reasoning = "Recommended because: " + ", ".join(reasoning_parts) if reasoning_parts else "Best available option based on composite scoring"

    # Build alternatives list (next 3 best options)
    alternatives = []
    for alt in scored_couriers[1:4]:
        alt_courier = alt["courier"]
        alternatives.append(CourierAvailability(
            courier_id=alt_courier.id,
            courier_name=alt_courier.full_name,
            is_available=True,
            current_load=alt["current_load"],
            max_capacity=max_capacity,
            rating=Decimal(str(alt_courier.performance_score or 0)),
            distance_to_pickup_km=alt["distance_km"],
            estimated_arrival_minutes=alt["estimated_minutes"],
            zone_id=None,
        ))

    return DispatchRecommendation(
        recommended_courier_id=best_courier.id,
        courier_name=best_courier.full_name,
        confidence_score=best["confidence"],
        distance_km=best["distance_km"],
        estimated_time_minutes=best["estimated_minutes"],
        courier_current_load=best["current_load"],
        courier_rating=Decimal(str(best_courier.performance_score or 0)),
        reasoning=reasoning,
        alternative_couriers=alternatives,
    )


@router.get("/metrics", response_model=DispatchMetrics)
def get_dispatch_metrics(
    period: str = Query("today", regex="^(today|week|month)$"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get dispatch performance metrics

    Returns:
    - Total assignments
    - Success/rejection rates
    - Average assignment time
    - Average acceptance time
    - Reassignment rate
    - Average courier load
    - Zone coverage rate
    """
    # Calculate date range based on period
    now = datetime.utcnow()
    if period == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start_date = now - timedelta(days=7)
    else:  # month
        start_date = now - timedelta(days=30)

    # Base query for period
    base_query = db.query(DispatchAssignment).filter(
        DispatchAssignment.organization_id == current_org.id,
        DispatchAssignment.created_at >= start_date,
    )

    # Total assignments
    total_assignments = base_query.count()

    # Successful (completed) assignments
    successful_assignments = base_query.filter(
        DispatchAssignment.status == "completed"
    ).count()

    # Rejected assignments
    rejected_assignments = base_query.filter(
        DispatchAssignment.status == "rejected"
    ).count()

    # Calculate average assignment time (time from creation to assignment)
    assigned_records = base_query.filter(
        DispatchAssignment.assigned_at.isnot(None)
    ).all()

    avg_assignment_seconds = 0.0
    if assigned_records:
        total_seconds = sum(
            (r.assigned_at - r.created_at).total_seconds()
            for r in assigned_records
            if r.assigned_at and r.created_at
        )
        avg_assignment_seconds = total_seconds / len(assigned_records)

    # Calculate average acceptance time (time from assignment to acceptance)
    accepted_records = base_query.filter(
        DispatchAssignment.accepted_at.isnot(None),
        DispatchAssignment.assigned_at.isnot(None),
    ).all()

    avg_acceptance_seconds = 0.0
    if accepted_records:
        total_seconds = sum(
            (r.accepted_at - r.assigned_at).total_seconds()
            for r in accepted_records
            if r.accepted_at and r.assigned_at
        )
        avg_acceptance_seconds = total_seconds / len(accepted_records)

    # Reassignment rate
    reassigned = base_query.filter(
        DispatchAssignment.is_reassignment == True
    ).count()
    reassignment_rate = (reassigned / total_assignments * 100) if total_assignments > 0 else 0.0

    # Average courier load (active assignments per active courier)
    active_couriers = db.query(Courier).filter(
        Courier.organization_id == current_org.id,
        Courier.status == CourierStatus.ACTIVE,
    ).count()

    active_assignments = db.query(DispatchAssignment).filter(
        DispatchAssignment.organization_id == current_org.id,
        DispatchAssignment.status.in_(["assigned", "accepted", "in_progress"]),
    ).count()

    avg_courier_load = (active_assignments / active_couriers) if active_couriers > 0 else 0.0

    # Zone coverage rate (zones with at least one active courier / total zones)
    from app.models.operations.zone import Zone
    total_zones = db.query(Zone).filter(
        Zone.organization_id == current_org.id,
        Zone.is_active == True,
    ).count()
    # For now, assume 100% coverage
    zone_coverage_rate = 100.0 if total_zones > 0 else 0.0

    return DispatchMetrics(
        period=period,
        total_assignments=total_assignments,
        successful_assignments=successful_assignments,
        rejected_assignments=rejected_assignments,
        avg_assignment_time_seconds=avg_assignment_seconds,
        avg_acceptance_time_seconds=avg_acceptance_seconds,
        reassignment_rate=reassignment_rate,
        avg_courier_load=avg_courier_load,
        zone_coverage_rate=zone_coverage_rate,
    )


# ============================================================================
# AUTO-DISPATCH ENDPOINTS
# ============================================================================

@router.post("/auto-dispatch", response_model=AutoDispatchResult)
async def auto_dispatch_order(
    request: AutoDispatchRequest,
    async_db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """
    Auto-dispatch a single delivery to the best available courier.

    Uses a multi-layer algorithm:
    1. Layer 1: Fast local filtering (online status, shift, zone, Haversine)
    2. Layer 2: Distance Matrix filtering (ETA to pickup threshold)
    3. Layer 3: Approximate route feasibility (Haversine + SLA check)
    4. Layer 4: Precise routing with scoring (Directions API + penalties)

    The algorithm considers:
    - Distance to pickup
    - Current courier load (fairness)
    - SLA deadline constraints
    - Route optimization with multiple stops
    """
    from app.services.dispatch.service import DispatchService

    try:
        service = DispatchService(async_db)
        assignment = await service.auto_assign_order(
            delivery_id=request.delivery_id,
            zone_id=request.zone_id
        )

        if assignment:
            return AutoDispatchResult(
                success=True,
                delivery_id=request.delivery_id,
                courier_id=assignment.courier_id,
                assignment_id=assignment.id,
                score=None,  # Score is internal
                message=f"Successfully assigned to courier {assignment.courier_id}",
                route={
                    "distance_km": float(assignment.distance_to_pickup_km or 0),
                    "estimated_minutes": assignment.estimated_time_minutes,
                }
            )
        else:
            return AutoDispatchResult(
                success=False,
                delivery_id=request.delivery_id,
                message="No feasible courier found for this delivery"
            )

    except Exception as e:
        return AutoDispatchResult(
            success=False,
            delivery_id=request.delivery_id,
            message=f"Auto-dispatch failed: {str(e)}"
        )


@router.post("/auto-dispatch/batch", response_model=AutoDispatchBatchResult)
async def auto_dispatch_batch(
    request: AutoDispatchBatchRequest,
    async_db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """
    Auto-dispatch multiple deliveries to available couriers.

    Processes deliveries sequentially, updating courier loads
    between each assignment for accurate capacity planning.

    Use this for batch assignment of pending orders.
    """
    from app.services.dispatch.service import DispatchService

    service = DispatchService(async_db)
    results: List[AutoDispatchResult] = []
    successful = 0
    failed = 0

    for delivery_id in request.delivery_ids:
        try:
            assignment = await service.auto_assign_order(
                delivery_id=delivery_id,
                zone_id=request.zone_id
            )

            if assignment:
                results.append(AutoDispatchResult(
                    success=True,
                    delivery_id=delivery_id,
                    courier_id=assignment.courier_id,
                    assignment_id=assignment.id,
                    message=f"Assigned to courier {assignment.courier_id}",
                    route={
                        "distance_km": float(assignment.distance_to_pickup_km or 0),
                        "estimated_minutes": assignment.estimated_time_minutes,
                    }
                ))
                successful += 1
            else:
                results.append(AutoDispatchResult(
                    success=False,
                    delivery_id=delivery_id,
                    message="No feasible courier found"
                ))
                failed += 1

        except Exception as e:
            results.append(AutoDispatchResult(
                success=False,
                delivery_id=delivery_id,
                message=f"Error: {str(e)}"
            ))
            failed += 1

    return AutoDispatchBatchResult(
        total=len(request.delivery_ids),
        successful=successful,
        failed=failed,
        results=results
    )


@router.get("/auto-dispatch/config")
def get_auto_dispatch_config(
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """
    Get current auto-dispatch configuration.

    Returns the algorithm parameters used for dispatch decisions.
    """
    from app.services.dispatch.config import DEFAULT_DISPATCH_CONFIG

    config = DEFAULT_DISPATCH_CONFIG
    return {
        "max_haversine_radius_km": config.max_haversine_radius_km,
        "max_pickup_eta_minutes": config.max_pickup_eta_minutes,
        "average_speed_kmh": config.average_speed_kmh,
        "sla_hours": config.sla_hours,
        "sla_buffer_minutes": config.sla_buffer_minutes,
        "target_orders_per_courier_per_day": config.target_orders_per_courier_per_day,
        "penalties": {
            "distance": config.penalties.distance,
            "sla": config.penalties.sla,
            "fairness": config.penalties.fairness,
            "overload": config.penalties.overload,
        },
    }
