from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_organization, get_current_user, get_db
from app.models.fleet import Courier, CourierStatus
from app.models.tenant.organization import Organization
from app.models.user import User
from app.schemas.fleet import (
    CourierBulkUpdate,
    CourierCreate,
    CourierDocumentStatus,
    CourierList,
    CourierOption,
    CourierResponse,
    CourierStats,
    CourierUpdate,
)
from app.schemas.analytics import (
    CourierStatisticsResponse,
    CourierStatusBreakdown,
    SponsorshipBreakdown,
    ProjectBreakdown,
)
from app.services.fleet import courier_service

router = APIRouter()


@router.get("/", response_model=List[CourierList])
def get_couriers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=2000),
    status: Optional[CourierStatus] = None,
    city: Optional[str] = None,
    search: Optional[str] = None,
):
    """Get list of couriers with filtering"""
    if search:
        return courier_service.search_couriers(
            db, search_term=search, skip=skip, limit=limit, organization_id=current_org.id
        )

    filters = {"organization_id": current_org.id}
    if status:
        filters["status"] = status
    if city:
        filters["city"] = city

    return courier_service.get_multi(db, skip=skip, limit=limit, filters=filters)


@router.get("/active", response_model=List[CourierList])
def get_active_couriers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=2000),
    city: Optional[str] = None,
):
    """Get active couriers"""
    return courier_service.get_active_couriers(
        db, skip=skip, limit=limit, city=city, organization_id=current_org.id
    )


@router.get("/without-vehicle", response_model=List[CourierList])
def get_couriers_without_vehicle(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=2000),
):
    """Get couriers without assigned vehicle"""
    return courier_service.get_without_vehicle(
        db, skip=skip, limit=limit, organization_id=current_org.id
    )


@router.get("/options", response_model=List[CourierOption])
def get_courier_options(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    status: Optional[CourierStatus] = Query(None),
):
    """Get courier options for dropdowns"""
    filters = {"organization_id": current_org.id}
    if status:
        filters["status"] = status
    couriers = courier_service.get_multi(db, skip=0, limit=1000, filters=filters)
    return [
        CourierOption(id=c.id, barq_id=c.barq_id, full_name=c.full_name, status=c.status)
        for c in couriers
    ]


@router.get("/statistics", response_model=CourierStatisticsResponse)
def get_courier_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
) -> CourierStatisticsResponse:
    """Get courier statistics with typed response"""
    stats = courier_service.get_statistics(db, organization_id=current_org.id)

    # Convert raw statistics to typed response
    status_breakdown_raw = stats.get("status_breakdown", {})
    sponsorship_breakdown_raw = stats.get("sponsorship_breakdown", {})
    project_breakdown_raw = stats.get("project_breakdown", {})
    total = stats.get("total", 0)
    with_vehicle = stats.get("with_vehicle", 0)

    # Helper function to get enum value
    def get_enum_value(key) -> str:
        return key.value if hasattr(key, "value") else str(key)

    # Extract counts from status breakdown (keys might be enum values)
    active_count = 0
    inactive_count = 0
    on_leave_count = 0
    onboarding_count = 0
    suspended_count = 0
    terminated_count = 0

    for status_key, count in status_breakdown_raw.items():
        status_value = get_enum_value(status_key)
        if status_value == "active":
            active_count = count
        elif status_value == "inactive":
            inactive_count = count
        elif status_value == "on_leave":
            on_leave_count = count
        elif status_value == "onboarding":
            onboarding_count = count
        elif status_value == "suspended":
            suspended_count = count
        elif status_value == "terminated":
            terminated_count = count

    # Extract sponsorship breakdown
    ajeer_count = 0
    inhouse_count = 0
    freelancer_count = 0

    for sponsor_key, count in sponsorship_breakdown_raw.items():
        sponsor_value = get_enum_value(sponsor_key)
        if sponsor_value == "ajeer":
            ajeer_count = count
        elif sponsor_value == "inhouse":
            inhouse_count = count
        elif sponsor_value == "freelancer":
            freelancer_count = count

    # Extract project breakdown
    ecommerce_count = 0
    food_count = 0
    warehouse_count = 0
    barq_count = 0

    for project_key, count in project_breakdown_raw.items():
        project_value = get_enum_value(project_key)
        if project_value == "ecommerce":
            ecommerce_count = count
        elif project_value == "food":
            food_count = count
        elif project_value == "warehouse":
            warehouse_count = count
        elif project_value == "barq":
            barq_count = count

    # Calculate utilization rate (active couriers with vehicles)
    utilization_rate = round((with_vehicle / active_count * 100) if active_count > 0 else 0, 1)

    return CourierStatisticsResponse(
        total_couriers=total,
        active_couriers=active_count,
        couriers_with_vehicle=with_vehicle,
        status_breakdown=CourierStatusBreakdown(
            active=active_count,
            inactive=inactive_count,
            on_leave=on_leave_count,
            onboarding=onboarding_count,
            suspended=suspended_count,
            terminated=terminated_count,
        ),
        sponsorship_breakdown=SponsorshipBreakdown(
            ajeer=ajeer_count,
            inhouse=inhouse_count,
            freelancer=freelancer_count,
        ),
        project_breakdown=ProjectBreakdown(
            ecommerce=ecommerce_count,
            food=food_count,
            warehouse=warehouse_count,
            barq=barq_count,
        ),
        utilization_rate=utilization_rate,
    )


@router.get("/documents/expiring", response_model=List[CourierDocumentStatus])
def get_expiring_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    days: int = Query(30, ge=1, le=365),
):
    """Get couriers with documents expiring soon"""
    return courier_service.get_expiring_documents(
        db, days_threshold=days, organization_id=current_org.id
    )


@router.get("/by-barq-id/{barq_id}", response_model=CourierResponse)
def get_courier_by_barq_id(
    barq_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get courier by BARQ ID"""
    courier = courier_service.get_by_barq_id(db, barq_id=barq_id)
    if not courier or courier.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Courier not found")
    return courier


@router.get("/{courier_id}", response_model=CourierResponse)
def get_courier(
    courier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get courier by ID"""
    courier = courier_service.get(db, id=courier_id)
    if not courier or courier.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Courier not found")
    return courier


@router.post("/", response_model=CourierResponse, status_code=status.HTTP_201_CREATED)
def create_courier(
    courier_in: CourierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Create new courier"""
    # Check if BARQ ID already exists within the organization
    existing = courier_service.get_by_barq_id(db, barq_id=courier_in.barq_id)
    if existing and existing.organization_id == current_org.id:
        raise HTTPException(status_code=400, detail="Courier with this BARQ ID already exists")

    # Check if email already exists within the organization
    if courier_in.email:
        existing_email = courier_service.get_by_email(db, email=courier_in.email)
        if existing_email and existing_email.organization_id == current_org.id:
            raise HTTPException(status_code=400, detail="Courier with this email already exists")

    return courier_service.create(db, obj_in=courier_in, organization_id=current_org.id)


@router.put("/{courier_id}", response_model=CourierResponse)
def update_courier(
    courier_id: int,
    courier_in: CourierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update courier"""
    courier = courier_service.get(db, id=courier_id)
    if not courier or courier.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Courier not found")

    # Check if updating BARQ ID and if it already exists within the organization
    if courier_in.barq_id and courier_in.barq_id != courier.barq_id:
        existing = courier_service.get_by_barq_id(db, barq_id=courier_in.barq_id)
        if existing and existing.organization_id == current_org.id:
            raise HTTPException(status_code=400, detail="Courier with this BARQ ID already exists")

    # Check if updating email and if it already exists within the organization
    if courier_in.email and courier_in.email != courier.email:
        existing_email = courier_service.get_by_email(db, email=courier_in.email)
        if existing_email and existing_email.organization_id == current_org.id:
            raise HTTPException(status_code=400, detail="Courier with this email already exists")

    return courier_service.update(db, db_obj=courier, obj_in=courier_in)


@router.delete("/{courier_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_courier(
    courier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Delete courier"""
    courier = courier_service.get(db, id=courier_id)
    if not courier or courier.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Courier not found")

    courier_service.delete(db, id=courier_id)
    return None


@router.post("/{courier_id}/assign-vehicle")
def assign_vehicle_to_courier(
    courier_id: int,
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Assign vehicle to courier"""
    courier = courier_service.get(db, id=courier_id)
    if not courier or courier.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Courier not found")

    # Also verify vehicle belongs to the same organization
    from app.services.fleet import vehicle_service

    vehicle = vehicle_service.get(db, id=vehicle_id)
    if not vehicle or vehicle.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    updated = courier_service.assign_vehicle(db, courier_id=courier_id, vehicle_id=vehicle_id)
    return {
        "message": "Vehicle assigned successfully",
        "courier_id": courier_id,
        "vehicle_id": vehicle_id,
    }


@router.post("/{courier_id}/unassign-vehicle")
def unassign_vehicle_from_courier(
    courier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Unassign vehicle from courier"""
    courier = courier_service.get(db, id=courier_id)
    if not courier or courier.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Courier not found")

    updated = courier_service.unassign_vehicle(db, courier_id=courier_id)
    return {"message": "Vehicle unassigned successfully", "courier_id": courier_id}


@router.patch("/{courier_id}/update-status")
def update_courier_status(
    courier_id: int,
    new_status: CourierStatus,
    last_working_day: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update courier status"""
    courier = courier_service.get(db, id=courier_id)
    if not courier or courier.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Courier not found")

    from datetime import datetime

    lwd = datetime.strptime(last_working_day, "%Y-%m-%d").date() if last_working_day else None

    updated = courier_service.update_status(
        db, courier_id=courier_id, status=new_status, last_working_day=lwd
    )
    return {
        "message": "Status updated successfully",
        "courier_id": courier_id,
        "new_status": new_status,
    }


@router.post("/bulk-update")
def bulk_update_couriers(
    bulk_data: CourierBulkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Bulk update couriers"""
    update_fields = bulk_data.model_dump(exclude_unset=True, exclude={"courier_ids"})

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Verify all courier IDs belong to the organization
    for courier_id in bulk_data.courier_ids:
        courier = courier_service.get(db, id=courier_id)
        if not courier or courier.organization_id != current_org.id:
            raise HTTPException(status_code=404, detail=f"Courier with ID {courier_id} not found")

    count = courier_service.bulk_update(db, ids=bulk_data.courier_ids, update_data=update_fields)
    return {"message": f"Updated {count} couriers", "count": count}
