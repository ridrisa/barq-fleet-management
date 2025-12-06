from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_organization, get_current_user, get_db
from app.models.fleet import Vehicle, VehicleStatus, VehicleType
from app.models.fleet.maintenance import VehicleMaintenance
from app.models.fleet.fuel_log import FuelLog
from app.models.fleet.assignment import CourierVehicleAssignment
from app.models.tenant.organization import Organization
from app.models.user import User
from app.schemas.fleet import (
    VehicleBulkUpdate,
    VehicleCreate,
    VehicleDocumentStatus,
    VehicleList,
    VehicleOption,
    VehicleResponse,
    VehicleStats,
    VehicleUpdate,
)
from app.schemas.analytics import VehicleStatisticsResponse, VehicleStatusBreakdown
from app.services.fleet import vehicle_service

router = APIRouter()


@router.get("/", response_model=List[VehicleList])
def get_vehicles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[VehicleStatus] = None,
    vehicle_type: Optional[VehicleType] = None,
    city: Optional[str] = None,
    search: Optional[str] = None,
):
    """Get list of vehicles with filtering"""
    if search:
        return vehicle_service.search_vehicles(
            db, search_term=search, skip=skip, limit=limit, organization_id=current_org.id
        )

    filters = {"organization_id": current_org.id}
    if status:
        filters["status"] = status
    if vehicle_type:
        filters["vehicle_type"] = vehicle_type
    if city:
        filters["assigned_to_city"] = city

    return vehicle_service.get_multi(db, skip=skip, limit=limit, filters=filters)


@router.get("/active", response_model=List[VehicleList])
def get_active_vehicles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    vehicle_type: Optional[VehicleType] = None,
):
    """Get active vehicles"""
    return vehicle_service.get_active_vehicles(
        db, skip=skip, limit=limit, vehicle_type=vehicle_type, organization_id=current_org.id
    )


@router.get("/available", response_model=List[VehicleList])
def get_available_vehicles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    vehicle_type: Optional[VehicleType] = None,
):
    """Get available vehicles (not assigned)"""
    return vehicle_service.get_available_vehicles(
        db, skip=skip, limit=limit, vehicle_type=vehicle_type, organization_id=current_org.id
    )


@router.get("/due-for-service", response_model=List[VehicleList])
def get_vehicles_due_for_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    days: int = Query(7, ge=1, le=365),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """Get vehicles due for service"""
    return vehicle_service.get_due_for_service(
        db, days_threshold=days, skip=skip, limit=limit, organization_id=current_org.id
    )


@router.get("/options", response_model=List[VehicleOption])
def get_vehicle_options(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    status: Optional[VehicleStatus] = Query(None),
):
    """Get vehicle options for dropdowns"""
    filters = {"organization_id": current_org.id}
    if status:
        filters["status"] = status
    vehicles = vehicle_service.get_multi(db, skip=0, limit=1000, filters=filters)
    return [
        VehicleOption(
            id=v.id,
            plate_number=v.plate_number,
            vehicle_type=v.vehicle_type,
            make=v.make,
            model=v.model,
            status=v.status,
        )
        for v in vehicles
    ]


@router.get("/statistics", response_model=VehicleStatisticsResponse)
def get_vehicle_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
) -> VehicleStatisticsResponse:
    """Get vehicle statistics with typed response"""
    stats = vehicle_service.get_statistics(db, organization_id=current_org.id)

    # Convert raw statistics to typed response
    status_breakdown = stats.get("status_breakdown", {})
    total = stats.get("total", 0)
    assigned = stats.get("assigned", 0)
    available = stats.get("available", 0)

    # Extract counts from status breakdown (keys might be enum values)
    available_count = 0
    assigned_count = 0
    maintenance_count = 0
    out_of_service_count = 0

    for status_key, count in status_breakdown.items():
        status_value = status_key.value if hasattr(status_key, "value") else str(status_key)
        if status_value == "available":
            available_count = count
        elif status_value == "assigned":
            assigned_count = count
        elif status_value == "maintenance":
            maintenance_count = count
        elif status_value == "out_of_service":
            out_of_service_count = count

    # Calculate active/inactive vehicles
    active_vehicles = available_count + assigned_count
    inactive_vehicles = maintenance_count + out_of_service_count

    # Calculate utilization rate
    utilization_rate = round((assigned / total * 100) if total > 0 else 0, 1)

    return VehicleStatisticsResponse(
        total_vehicles=total,
        active_vehicles=active_vehicles,
        inactive_vehicles=inactive_vehicles,
        maintenance_due=maintenance_count,
        status_breakdown=VehicleStatusBreakdown(
            available=available_count,
            assigned=assigned_count,
            maintenance=maintenance_count,
            out_of_service=out_of_service_count,
        ),
        utilization_rate=utilization_rate,
    )


@router.get("/documents/expiring", response_model=List[VehicleDocumentStatus])
def get_expiring_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    days: int = Query(30, ge=1, le=365),
):
    """Get vehicles with documents expiring soon"""
    return vehicle_service.get_expiring_documents(
        db, days_threshold=days, organization_id=current_org.id
    )


@router.get("/{vehicle_id}/history")
def get_vehicle_history(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
) -> Dict[str, Any]:
    """Get vehicle history including maintenance, fuel logs, and assignments"""
    # Verify vehicle belongs to the organization
    vehicle = vehicle_service.get(db, id=vehicle_id)
    if not vehicle or vehicle.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # Get maintenance records
    maintenance_records = (
        db.query(VehicleMaintenance)
        .filter(
            VehicleMaintenance.vehicle_id == vehicle_id,
            VehicleMaintenance.organization_id == current_org.id,
        )
        .order_by(VehicleMaintenance.scheduled_date.desc())
        .limit(50)
        .all()
    )

    # Get fuel logs
    fuel_logs = (
        db.query(FuelLog)
        .filter(
            FuelLog.vehicle_id == vehicle_id,
            FuelLog.organization_id == current_org.id,
        )
        .order_by(FuelLog.fuel_date.desc())
        .limit(50)
        .all()
    )

    # Get assignment history with courier info
    assignments = (
        db.query(CourierVehicleAssignment)
        .filter(
            CourierVehicleAssignment.vehicle_id == vehicle_id,
            CourierVehicleAssignment.organization_id == current_org.id,
        )
        .order_by(CourierVehicleAssignment.start_date.desc())
        .limit(50)
        .all()
    )

    # Calculate summary statistics
    total_maintenance_cost = sum(
        float(m.total_cost or 0) for m in maintenance_records
    )
    total_fuel_cost = sum(float(f.fuel_cost or 0) for f in fuel_logs)
    total_fuel_quantity = sum(float(f.fuel_quantity or 0) for f in fuel_logs)

    # Calculate average fuel efficiency
    avg_fuel_efficiency = 0.0
    if fuel_logs and total_fuel_quantity > 0:
        odometer_readings = [float(f.odometer_reading) for f in fuel_logs if f.odometer_reading]
        if len(odometer_readings) >= 2:
            distance = max(odometer_readings) - min(odometer_readings)
            if distance > 0:
                avg_fuel_efficiency = round(distance / total_fuel_quantity, 2)

    # Format maintenance records
    maintenance_data = [
        {
            "date": str(m.scheduled_date) if m.scheduled_date else str(m.created_at.date()),
            "type": m.maintenance_type.value if m.maintenance_type else "unknown",
            "cost": float(m.total_cost or 0),
            "mileage": float(m.mileage_at_service or 0),
        }
        for m in maintenance_records
    ]

    # Format fuel logs
    fuel_data = [
        {
            "date": str(f.fuel_date) if f.fuel_date else str(f.created_at.date()),
            "liters": float(f.fuel_quantity or 0),
            "cost": float(f.fuel_cost or 0),
            "odometer": float(f.odometer_reading or 0),
        }
        for f in fuel_logs
    ]

    # Format assignments
    assignment_data = []
    for a in assignments:
        duration_days = a.duration_days
        duration_str = f"{duration_days} days" if duration_days else "Ongoing"
        courier_name = a.courier.full_name if a.courier else "Unknown"
        assignment_data.append({
            "courier": courier_name,
            "startDate": str(a.start_date) if a.start_date else "",
            "endDate": str(a.end_date) if a.end_date else "",
            "duration": duration_str,
        })

    return {
        "summary": {
            "mileage": float(vehicle.current_mileage or 0),
            "total_maintenance_cost": total_maintenance_cost,
            "total_fuel_cost": total_fuel_cost,
            "avg_fuel_efficiency": avg_fuel_efficiency,
        },
        "maintenance": maintenance_data,
        "fuel_logs": fuel_data,
        "assignments": assignment_data,
    }


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get vehicle by ID"""
    vehicle = vehicle_service.get(db, id=vehicle_id)
    if not vehicle or vehicle.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    vehicle_in: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Create new vehicle"""
    existing = vehicle_service.get_by_plate_number(db, plate_number=vehicle_in.plate_number)
    if existing and existing.organization_id == current_org.id:
        raise HTTPException(status_code=400, detail="Vehicle with this plate number already exists")

    return vehicle_service.create(db, obj_in=vehicle_in, organization_id=current_org.id)


@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: int,
    vehicle_in: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update vehicle"""
    vehicle = vehicle_service.get(db, id=vehicle_id)
    if not vehicle or vehicle.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    if vehicle_in.plate_number and vehicle_in.plate_number != vehicle.plate_number:
        existing = vehicle_service.get_by_plate_number(db, plate_number=vehicle_in.plate_number)
        if existing and existing.organization_id == current_org.id:
            raise HTTPException(
                status_code=400, detail="Vehicle with this plate number already exists"
            )

    return vehicle_service.update(db, db_obj=vehicle, obj_in=vehicle_in)


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Delete vehicle"""
    vehicle = vehicle_service.get(db, id=vehicle_id)
    if not vehicle or vehicle.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    vehicle_service.delete(db, id=vehicle_id)
    return None


@router.post("/{vehicle_id}/update-mileage")
def update_vehicle_mileage(
    vehicle_id: int,
    new_mileage: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update vehicle mileage"""
    vehicle = vehicle_service.get(db, id=vehicle_id)
    if not vehicle or vehicle.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    updated = vehicle_service.update_mileage(db, vehicle_id=vehicle_id, new_mileage=new_mileage)
    return {
        "message": "Mileage updated successfully",
        "vehicle_id": vehicle_id,
        "new_mileage": new_mileage,
    }


@router.patch("/{vehicle_id}/update-status")
def update_vehicle_status(
    vehicle_id: int,
    new_status: VehicleStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update vehicle status"""
    vehicle = vehicle_service.get(db, id=vehicle_id)
    if not vehicle or vehicle.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    updated = vehicle_service.update_status(db, vehicle_id=vehicle_id, status=new_status)
    return {
        "message": "Status updated successfully",
        "vehicle_id": vehicle_id,
        "new_status": new_status,
    }


@router.post("/bulk-update")
def bulk_update_vehicles(
    bulk_data: VehicleBulkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Bulk update vehicles"""
    update_fields = bulk_data.model_dump(exclude_unset=True, exclude={"vehicle_ids"})

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Verify all vehicle IDs belong to the organization
    for vehicle_id in bulk_data.vehicle_ids:
        vehicle = vehicle_service.get(db, id=vehicle_id)
        if not vehicle or vehicle.organization_id != current_org.id:
            raise HTTPException(status_code=404, detail=f"Vehicle with ID {vehicle_id} not found")

    count = vehicle_service.bulk_update(db, ids=bulk_data.vehicle_ids, update_data=update_fields)
    return {"message": f"Updated {count} vehicles", "count": count}
