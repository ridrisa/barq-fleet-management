import logging
from datetime import date, datetime, timedelta
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_organization, get_current_user
from app.models.fleet.courier import Courier
from app.models.fleet.vehicle import Vehicle
from app.models.operations.incident import Incident, IncidentStatus, IncidentType
from app.models.tenant.organization import Organization
from app.services.operations import incident_service
from app.services.sms_notification_service import sms_notification_service
from app.schemas.operations.incident import IncidentCreate, IncidentResponse, IncidentUpdate

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[IncidentResponse])
def list_incidents(
    skip: int = 0,
    limit: int = 100,
    courier_id: int = Query(None, description="Filter by courier"),
    vehicle_id: int = Query(None, description="Filter by vehicle"),
    incident_type: str = Query(None, description="Filter by type"),
    status: str = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List all incidents with optional filters"""
    incidents = incident_service.get_multi(db, skip=skip, limit=limit, filters={"organization_id": current_org.id})
    return incidents


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get a specific incident by ID"""
    incident = incident_service.get(db, id=incident_id)
    if not incident or incident.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return incident


@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
def create_incident(
    incident_in: IncidentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Report a new incident

    Business Logic:
    - Creates incident record
    - Sets status to REPORTED
    - Validates courier and vehicle exist
    - Auto-categorizes incident severity
    - Triggers notifications to supervisors
    """
    # Validate courier exists
    courier = None
    if incident_in.courier_id:
        courier = db.query(Courier).filter(
            Courier.id == incident_in.courier_id,
            Courier.organization_id == current_org.id
        ).first()
        if not courier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Courier with ID {incident_in.courier_id} not found",
            )

    # Validate vehicle exists
    if incident_in.vehicle_id:
        vehicle = db.query(Vehicle).filter(
            Vehicle.id == incident_in.vehicle_id,
            Vehicle.organization_id == current_org.id
        ).first()
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vehicle with ID {incident_in.vehicle_id} not found",
            )

    # Auto-categorize severity based on incident type if not provided
    incident_data = incident_in.model_dump()
    if not incident_data.get("severity"):
        severity_mapping = {
            IncidentType.ACCIDENT: "critical",
            IncidentType.THEFT: "critical",
            IncidentType.DAMAGE: "high",
            IncidentType.VIOLATION: "medium",
            IncidentType.OTHER: "low",
        }
        incident_data["severity"] = severity_mapping.get(incident_in.incident_type, "low")
        logger.info(
            f"Auto-categorized incident severity as '{incident_data['severity']}' "
            f"based on type '{incident_in.incident_type.value}'"
        )

    # Create the incident with auto-categorized severity
    incident_create = IncidentCreate(**incident_data)
    incident = incident_service.create(db, obj_in=incident_create, organization_id=current_org.id)

    # Send notification to supervisor
    try:
        if courier and courier.supervisor_name:
            # Build notification message
            severity_label = incident_data.get("severity", "unknown")
            message = (
                f"تنبيه حادث جديد\n"
                f"النوع: {incident_in.incident_type.value}\n"
                f"الخطورة: {severity_label}\n"
                f"الموظف: {courier.full_name}\n"
                f"التاريخ: {incident_in.incident_date.strftime('%Y-%m-%d')}\n"
                f"BARQ Fleet Management"
            )
            # If courier has mobile number, send to them (supervisor notification)
            if courier.mobile_number:
                sms_notification_service.send_sms(courier.mobile_number, message)
                logger.info(
                    f"Incident notification sent for incident ID {incident.id} "
                    f"to courier {courier.barq_id}"
                )
    except Exception as e:
        logger.error(f"Failed to send incident notification: {str(e)}")

    return incident


@router.put("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: int,
    incident_in: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update an incident

    Business Logic:
    - Updates incident details
    - Tracks status changes
    - Logs resolution information
    - Updates cost if applicable
    """
    incident = incident_service.get(db, id=incident_id)
    if not incident or incident.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    incident = incident_service.update(db, db_obj=incident, obj_in=incident_in)
    return incident


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Delete an incident"""
    incident = incident_service.get(db, id=incident_id)
    if not incident or incident.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    incident_service.remove(db, id=incident_id)
    return None


@router.post("/{incident_id}/resolve", response_model=IncidentResponse)
def resolve_incident(
    incident_id: int,
    resolution: str,
    cost: int = 0,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Resolve an incident

    Business Logic:
    - Updates status to RESOLVED
    - Records resolution details
    - Updates cost
    - Closes incident workflow
    """
    incident = incident_service.get(db, id=incident_id)
    if not incident or incident.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    incident_update = IncidentUpdate(status="resolved", resolution=resolution, cost=cost)
    incident = incident_service.update(db, db_obj=incident, obj_in=incident_update)
    return incident


@router.get("/analytics/summary")
def get_incident_analytics(
    start_date: date = Query(None),
    end_date: date = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
) -> Dict[str, Any]:
    """Get incident analytics

    Returns:
    - Total incidents by type
    - Incidents by status
    - Average resolution time
    - Total cost impact
    - Top couriers/vehicles with incidents
    - Trend analysis
    """
    # Build base query with organization filter
    base_query = db.query(Incident).filter(Incident.organization_id == current_org.id)

    # Apply date filters if provided
    if start_date:
        base_query = base_query.filter(Incident.incident_date >= start_date)
    if end_date:
        base_query = base_query.filter(Incident.incident_date <= end_date)

    # Get all incidents for analysis
    incidents = base_query.all()
    total_incidents = len(incidents)

    # Count by type
    by_type = {}
    for incident_type in IncidentType:
        count = sum(1 for i in incidents if i.incident_type == incident_type)
        by_type[incident_type.value] = count

    # Count by status
    by_status = {}
    for incident_status in IncidentStatus:
        count = sum(1 for i in incidents if i.status == incident_status)
        by_status[incident_status.value] = count

    # Calculate average resolution time (for resolved/closed incidents)
    resolved_incidents = [
        i for i in incidents
        if i.status in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]
        and i.updated_at and i.created_at
    ]
    avg_resolution_time_days = 0.0
    if resolved_incidents:
        total_days = sum(
            (i.updated_at - i.created_at).days for i in resolved_incidents
        )
        avg_resolution_time_days = total_days / len(resolved_incidents)

    # Calculate total cost
    total_cost = sum(float(i.cost or 0) for i in incidents)

    # Top couriers with incidents
    courier_counts = {}
    for i in incidents:
        if i.courier_id:
            courier_counts[i.courier_id] = courier_counts.get(i.courier_id, 0) + 1

    top_courier_ids = sorted(courier_counts.keys(), key=lambda x: courier_counts[x], reverse=True)[:5]
    top_couriers = []
    for courier_id in top_courier_ids:
        courier = db.query(Courier).filter(Courier.id == courier_id).first()
        if courier:
            top_couriers.append({
                "courier_id": courier_id,
                "name": courier.full_name,
                "barq_id": courier.barq_id,
                "incident_count": courier_counts[courier_id]
            })

    # Top vehicles with incidents
    vehicle_counts = {}
    for i in incidents:
        if i.vehicle_id:
            vehicle_counts[i.vehicle_id] = vehicle_counts.get(i.vehicle_id, 0) + 1

    top_vehicle_ids = sorted(vehicle_counts.keys(), key=lambda x: vehicle_counts[x], reverse=True)[:5]
    top_vehicles = []
    for vehicle_id in top_vehicle_ids:
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if vehicle:
            top_vehicles.append({
                "vehicle_id": vehicle_id,
                "plate_number": vehicle.plate_number,
                "make_model": f"{vehicle.make} {vehicle.model}",
                "incident_count": vehicle_counts[vehicle_id]
            })

    return {
        "total_incidents": total_incidents,
        "by_type": by_type,
        "by_status": by_status,
        "avg_resolution_time_days": round(avg_resolution_time_days, 1),
        "total_cost": total_cost,
        "top_couriers": top_couriers,
        "top_vehicles": top_vehicles,
        "date_range": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
        }
    }


@router.get("/analytics/trends")
def get_incident_trends(
    period: str = Query("month", regex="^(week|month|quarter|year)$"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
) -> Dict[str, Any]:
    """Get incident trend analysis

    Business Logic:
    - Analyzes incident patterns over time
    - Identifies recurring issues
    - Highlights risk areas
    - Suggests preventive measures
    """
    # Calculate date range based on period
    today = date.today()
    period_days = {
        "week": 7,
        "month": 30,
        "quarter": 90,
        "year": 365,
    }
    days = period_days.get(period, 30)
    start_date = today - timedelta(days=days)

    # Get incidents in the current period
    current_incidents = db.query(Incident).filter(
        Incident.organization_id == current_org.id,
        Incident.incident_date >= start_date,
        Incident.incident_date <= today
    ).all()

    # Get incidents in the previous period for comparison
    prev_start_date = start_date - timedelta(days=days)
    prev_incidents = db.query(Incident).filter(
        Incident.organization_id == current_org.id,
        Incident.incident_date >= prev_start_date,
        Incident.incident_date < start_date
    ).all()

    current_count = len(current_incidents)
    prev_count = len(prev_incidents)

    # Determine trend direction
    if prev_count == 0:
        trend = "stable" if current_count == 0 else "increasing"
        change_percentage = 0.0
    else:
        change_percentage = ((current_count - prev_count) / prev_count) * 100
        if change_percentage > 10:
            trend = "increasing"
        elif change_percentage < -10:
            trend = "decreasing"
        else:
            trend = "stable"

    # Identify recurring issues (types that appear frequently)
    type_counts = {}
    for incident in current_incidents:
        incident_type = incident.incident_type.value if incident.incident_type else "unknown"
        type_counts[incident_type] = type_counts.get(incident_type, 0) + 1

    # Recurring issues are types that appear more than 20% of the time
    threshold = max(1, current_count * 0.2)
    recurring_issues = [
        {"type": t, "count": c, "percentage": round((c / current_count) * 100, 1)}
        for t, c in type_counts.items() if c >= threshold
    ]
    recurring_issues.sort(key=lambda x: x["count"], reverse=True)

    # Identify risk areas (couriers or vehicles with multiple incidents)
    courier_incidents = {}
    vehicle_incidents = {}
    for incident in current_incidents:
        if incident.courier_id:
            courier_incidents[incident.courier_id] = courier_incidents.get(incident.courier_id, 0) + 1
        if incident.vehicle_id:
            vehicle_incidents[incident.vehicle_id] = vehicle_incidents.get(incident.vehicle_id, 0) + 1

    # Risk threshold: 2+ incidents in the period
    risk_areas = []

    # High-risk couriers
    high_risk_couriers = [cid for cid, count in courier_incidents.items() if count >= 2]
    for courier_id in high_risk_couriers[:5]:
        courier = db.query(Courier).filter(Courier.id == courier_id).first()
        if courier:
            risk_areas.append({
                "type": "courier",
                "id": courier_id,
                "name": courier.full_name,
                "barq_id": courier.barq_id,
                "incident_count": courier_incidents[courier_id],
                "recommendation": "Review courier performance and provide additional training"
            })

    # High-risk vehicles
    high_risk_vehicles = [vid for vid, count in vehicle_incidents.items() if count >= 2]
    for vehicle_id in high_risk_vehicles[:5]:
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if vehicle:
            risk_areas.append({
                "type": "vehicle",
                "id": vehicle_id,
                "plate_number": vehicle.plate_number,
                "make_model": f"{vehicle.make} {vehicle.model}",
                "incident_count": vehicle_incidents[vehicle_id],
                "recommendation": "Schedule vehicle inspection and maintenance"
            })

    # Generate preventive measures based on analysis
    preventive_measures = []
    if any(t["type"] == "accident" for t in recurring_issues):
        preventive_measures.append({
            "issue": "High accident rate",
            "measure": "Implement defensive driving training program",
            "priority": "high"
        })
    if any(t["type"] == "violation" for t in recurring_issues):
        preventive_measures.append({
            "issue": "Traffic violations",
            "measure": "Review traffic rules awareness and conduct refresher courses",
            "priority": "medium"
        })
    if any(t["type"] == "damage" for t in recurring_issues):
        preventive_measures.append({
            "issue": "Vehicle damage incidents",
            "measure": "Review vehicle handling procedures and parking guidelines",
            "priority": "medium"
        })
    if len(high_risk_couriers) > 0:
        preventive_measures.append({
            "issue": "Multiple incidents by same couriers",
            "measure": "Individual performance review and targeted coaching",
            "priority": "high"
        })
    if len(high_risk_vehicles) > 0:
        preventive_measures.append({
            "issue": "Multiple incidents involving same vehicles",
            "measure": "Comprehensive vehicle inspection and potential replacement",
            "priority": "high"
        })

    return {
        "period": period,
        "date_range": {
            "start_date": start_date.isoformat(),
            "end_date": today.isoformat(),
        },
        "trend": trend,
        "statistics": {
            "current_period_count": current_count,
            "previous_period_count": prev_count,
            "change_percentage": round(change_percentage, 1),
        },
        "recurring_issues": recurring_issues,
        "risk_areas": risk_areas,
        "preventive_measures": preventive_measures,
    }
