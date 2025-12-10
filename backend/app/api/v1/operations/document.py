"""
Operations Document API Routes
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_organization, get_current_user, get_db
from app.services.operations import operations_document_service
from app.models.operations.document import DocumentCategory
from app.models.tenant.organization import Organization
from app.models.user import User
from app.schemas.operations.document import (
    OperationsDocumentCreate,
    OperationsDocumentResponse,
    OperationsDocumentUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[OperationsDocumentResponse])
def get_documents(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search query"),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """
    Get list of operations documents with optional filtering

    Filters:
    - category: Filter by document category (Procedures, Policies, Training, Reports)
    - search: Search by name, description, or tags
    """
    # Parse category if provided
    doc_category = None
    if category:
        try:
            doc_category = DocumentCategory(category)
        except ValueError:
            pass  # Invalid category, ignore filter

    # Search or filter
    if search:
        return operations_document_service.search(
            db,
            query=search,
            category=doc_category,
            skip=skip,
            limit=limit,
            organization_id=current_org.id,
        )

    if doc_category:
        return operations_document_service.get_by_category(
            db, category=doc_category, skip=skip, limit=limit, organization_id=current_org.id
        )

    return operations_document_service.get_multi(db, skip=skip, limit=limit, filters={"organization_id": current_org.id})


@router.post("/", response_model=OperationsDocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    document_in: OperationsDocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Create new operations document"""
    # Set uploader info from current user if not provided
    doc_data = document_in.model_dump()
    if not doc_data.get("uploaded_by") and current_user:
        doc_data["uploaded_by"] = current_user.full_name or current_user.email
        doc_data["uploader_email"] = current_user.email
        doc_data["uploaded_by_id"] = current_user.id

    doc_create = OperationsDocumentCreate(**doc_data)
    return operations_document_service.create(db, obj_in=doc_create, organization_id=current_org.id)


@router.get("/{document_id}", response_model=OperationsDocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get document by ID"""
    doc = operations_document_service.get(db, id=document_id)
    if not doc or doc.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.put("/{document_id}", response_model=OperationsDocumentResponse)
def update_document(
    document_id: int,
    document_in: OperationsDocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update document"""
    doc = operations_document_service.get(db, id=document_id)
    if not doc or doc.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Document not found")

    return operations_document_service.update(db, db_obj=doc, obj_in=document_in)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Delete document"""
    doc = operations_document_service.get(db, id=document_id)
    if not doc or doc.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Document not found")

    operations_document_service.delete(db, id=document_id)
    return None


@router.post("/{document_id}/view", response_model=OperationsDocumentResponse)
def record_view(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Record document view and return document"""
    # Verify document belongs to organization
    existing = operations_document_service.get(db, id=document_id)
    if not existing or existing.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Document not found")

    doc = operations_document_service.increment_view_count(db, doc_id=document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.post("/{document_id}/download", response_model=OperationsDocumentResponse)
def record_download(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Record document download and return document with file URL"""
    # Verify document belongs to organization
    existing = operations_document_service.get(db, id=document_id)
    if not existing or existing.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Document not found")

    doc = operations_document_service.increment_download_count(db, doc_id=document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/categories/stats", response_model=dict)
def get_category_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get document count by category"""
    from sqlalchemy import func

    from app.models.operations.document import OperationsDocument

    results = (
        db.query(OperationsDocument.category, func.count(OperationsDocument.id).label("count"))
        .filter(OperationsDocument.organization_id == current_org.id)
        .group_by(OperationsDocument.category)
        .all()
    )

    stats = {cat.value: 0 for cat in DocumentCategory}
    for row in results:
        if row.category:
            stats[row.category.value] = row.count

    stats["total"] = sum(stats.values())
    return stats
