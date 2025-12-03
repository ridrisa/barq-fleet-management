from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_organization, get_current_user, get_db
from app.models.fleet import Vehicle, VehicleStatus, VehicleType
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


@router.get("/statistics")
def get_vehicle_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get vehicle statistics"""
    return vehicle_service.get_statistics(db, organization_id=current_org.id)


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
