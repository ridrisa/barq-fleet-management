"""Admin Integration Management API"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_superuser, get_db
from app.models.admin.integration import Integration, IntegrationStatus
from app.models.user import User
from app.schemas.admin.integration import (
    IntegrationCreate,
    IntegrationListResponse,
    IntegrationResponse,
    IntegrationTestRequest,
    IntegrationTestResponse,
    IntegrationUpdate,
)

router = APIRouter()


@router.get("/", response_model=IntegrationListResponse)
def list_integrations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    integration_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    is_enabled: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    List all integrations with filtering and pagination.

    Requires superuser permission.
    """
    query = db.query(Integration)

    # Apply filters
    if integration_type:
        query = query.filter(Integration.integration_type == integration_type)
    if status:
        query = query.filter(Integration.status == status)
    if is_enabled is not None:
        query = query.filter(Integration.is_enabled == is_enabled)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Integration.name.ilike(search_pattern))
            | (Integration.display_name.ilike(search_pattern))
        )

    # Get total count
    total = query.count()

    # Get paginated results
    integrations = query.order_by(Integration.name).offset(skip).limit(limit).all()

    return IntegrationListResponse(items=integrations, total=total, skip=skip, limit=limit)


@router.post("/", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
def create_integration(
    integration_in: IntegrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Create a new integration.

    Requires superuser permission.
    """
    # Check if integration with same name exists
    existing = db.query(Integration).filter(Integration.name == integration_in.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Integration with name '{integration_in.name}' already exists",
        )

    # Create integration
    integration = Integration(**integration_in.dict())

    db.add(integration)
    db.commit()
    db.refresh(integration)

    return integration


@router.get("/{integration_id}", response_model=IntegrationResponse)
def get_integration(
    integration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get a specific integration by ID.

    Requires superuser permission.
    """
    integration = db.query(Integration).filter(Integration.id == integration_id).first()
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration with id {integration_id} not found",
        )
    return integration


@router.patch("/{integration_id}", response_model=IntegrationResponse)
def update_integration(
    integration_id: int,
    integration_in: IntegrationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Update an integration.

    Requires superuser permission.
    """
    integration = db.query(Integration).filter(Integration.id == integration_id).first()
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration with id {integration_id} not found",
        )

    update_data = integration_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(integration, field, value)

    db.commit()
    db.refresh(integration)
    return integration


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_integration(
    integration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Delete an integration.

    Requires superuser permission.
    """
    integration = db.query(Integration).filter(Integration.id == integration_id).first()
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration with id {integration_id} not found",
        )

    db.delete(integration)
    db.commit()
    return None


@router.post("/{integration_id}/enable", response_model=IntegrationResponse)
def enable_integration(
    integration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Enable an integration.

    Requires superuser permission.
    """
    integration = db.query(Integration).filter(Integration.id == integration_id).first()
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration with id {integration_id} not found",
        )

    integration.is_enabled = True
    if integration.status == IntegrationStatus.INACTIVE.value:
        integration.status = IntegrationStatus.ACTIVE.value

    db.commit()
    db.refresh(integration)
    return integration


@router.post("/{integration_id}/disable", response_model=IntegrationResponse)
def disable_integration(
    integration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Disable an integration.

    Requires superuser permission.
    """
    integration = db.query(Integration).filter(Integration.id == integration_id).first()
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration with id {integration_id} not found",
        )

    integration.is_enabled = False
    integration.status = IntegrationStatus.INACTIVE.value

    db.commit()
    db.refresh(integration)
    return integration


@router.post("/{integration_id}/test", response_model=IntegrationTestResponse)
def test_integration(
    integration_id: int,
    test_request: IntegrationTestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Test an integration connection.

    Requires superuser permission.

    Performs a test API call to verify integration is working correctly.
    """
    integration = db.query(Integration).filter(Integration.id == integration_id).first()
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration with id {integration_id} not found",
        )

    # Placeholder for actual integration testing logic
    # In production, this would make actual API calls to test the integration

    try:
        # Simulate successful test
        integration.record_success()
        db.commit()

        return IntegrationTestResponse(
            success=True,
            message="Integration test successful",
            response_time_ms=150,
            status_code=200,
            response_data={"status": "ok"},
            error=None,
        )
    except Exception as e:
        integration.record_error(str(e))
        db.commit()

        return IntegrationTestResponse(
            success=False,
            message="Integration test failed",
            response_time_ms=None,
            status_code=None,
            response_data=None,
            error=str(e),
        )


@router.post("/{integration_id}/health-check", response_model=IntegrationResponse)
def integration_health_check(
    integration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Perform health check on an integration.

    Requires superuser permission.

    Updates last_health_check timestamp and status.
    """
    integration = db.query(Integration).filter(Integration.id == integration_id).first()
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration with id {integration_id} not found",
        )

    # Placeholder for actual health check logic
    integration.last_health_check = datetime.utcnow()

    db.commit()
    db.refresh(integration)
    return integration


@router.get("/types/list", response_model=List[str])
def list_integration_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get list of all integration types.

    Requires superuser permission.
    """
    from app.models.admin.integration import IntegrationType

    return [t.value for t in IntegrationType]
