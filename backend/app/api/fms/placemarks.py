"""
FMS Placemarks API Routes
Provides endpoints for placemark/POI management from machinettalk.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Body
from pydantic import BaseModel, Field
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.fms import get_fms_client

router = APIRouter()


class PlacemarkCreate(BaseModel):
    """Schema for creating a placemark."""
    PlacemarkName: str = Field(..., min_length=1, max_length=200, description="English name")
    PlacemarkNameAr: str = Field(..., min_length=1, max_length=200, description="Arabic name")
    Latitude: float = Field(..., ge=-90, le=90)
    Longitude: float = Field(..., ge=-180, le=180)
    Color: Optional[str] = Field(None, description="Marker color (hex or name)")


class PlacemarkUpdate(BaseModel):
    """Schema for updating a placemark."""
    PlacemarkName: Optional[str] = Field(None, min_length=1, max_length=200)
    PlacemarkNameAr: Optional[str] = Field(None, min_length=1, max_length=200)
    Latitude: Optional[float] = Field(None, ge=-90, le=90)
    Longitude: Optional[float] = Field(None, ge=-180, le=180)
    Color: Optional[str] = None


@router.get("/")
async def get_placemarks(
    page_size: int = Query(100, ge=1, le=500, description="Items per page"),
    page_index: int = Query(0, ge=0, description="Page index"),
    current_user: User = Depends(get_current_user),
):
    """
    Get all placemarks/points of interest.
    """
    client = get_fms_client()
    result = client.get_placemarks(page_size=page_size, page_index=page_index)

    if result.get("error"):
        raise HTTPException(
            status_code=502,
            detail=result.get("message", "FMS service unavailable")
        )

    return result


@router.get("/{placemark_id}")
async def get_placemark_by_id(
    placemark_id: int,
    current_user: User = Depends(get_current_user),
):
    """
    Get placemark details by ID.
    """
    client = get_fms_client()
    result = client.get_placemark_by_id(placemark_id)

    if result.get("error"):
        raise HTTPException(
            status_code=502 if "unavailable" in str(result.get("message", "")).lower() else 404,
            detail=result.get("message", "Placemark not found")
        )

    return result


@router.post("/")
async def create_placemark(
    placemark: PlacemarkCreate,
    current_user: User = Depends(get_current_user),
):
    """
    Create a new placemark/POI.
    """
    client = get_fms_client()
    result = client.create_placemark(placemark.model_dump(exclude_none=True))

    if result.get("error"):
        raise HTTPException(
            status_code=502,
            detail=result.get("message", "Failed to create placemark")
        )

    return result


@router.put("/{placemark_id}")
async def update_placemark(
    placemark_id: int,
    placemark: PlacemarkUpdate,
    current_user: User = Depends(get_current_user),
):
    """
    Update a placemark/POI.
    """
    client = get_fms_client()
    result = client.update_placemark(placemark_id, placemark.model_dump(exclude_none=True))

    if result.get("error"):
        raise HTTPException(
            status_code=502,
            detail=result.get("message", "Failed to update placemark")
        )

    return result


@router.delete("/{placemark_id}")
async def delete_placemark(
    placemark_id: int,
    current_user: User = Depends(get_current_user),
):
    """
    Delete a placemark/POI.
    """
    client = get_fms_client()
    result = client.delete_placemark(placemark_id)

    if result.get("error"):
        raise HTTPException(
            status_code=502,
            detail=result.get("message", "Failed to delete placemark")
        )

    return {"message": "Placemark deleted successfully"}
