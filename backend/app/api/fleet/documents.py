from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.crud.fleet.document import document as crud_document
from app.schemas.fleet.document import DocumentCreate, DocumentResponse, DocumentUpdate

router = APIRouter()


@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    skip: int = 0,
    limit: int = 100,
    entity_type: str = Query(None, description="Filter by entity type (courier or vehicle)"),
    entity_id: int = Query(None, description="Filter by entity ID"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all documents with optional filtering"""
    if entity_type and entity_id:
        # Filter by both entity_type and entity_id
        from app.models.fleet.document import Document

        documents = (
            db.query(Document)
            .filter(Document.entity_type == entity_type, Document.entity_id == entity_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    elif entity_type:
        # Filter by entity_type only
        from app.models.fleet.document import Document

        documents = (
            db.query(Document)
            .filter(Document.entity_type == entity_type)
            .offset(skip)
            .limit(limit)
            .all()
        )
    elif entity_id:
        # Filter by entity_id only
        from app.models.fleet.document import Document

        documents = (
            db.query(Document)
            .filter(Document.entity_id == entity_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    else:
        # No filter, get all documents
        documents = crud_document.get_multi(db, skip=skip, limit=limit)

    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Get a specific document by ID"""
    document = crud_document.get(db, id=document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    document_in: DocumentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new document"""
    document = crud_document.create(db, obj_in=document_in)
    return document


@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    document_in: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a document"""
    document = crud_document.get(db, id=document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    document = crud_document.update(db, db_obj=document, obj_in=document_in)
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Delete a document"""
    document = crud_document.get(db, id=document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    crud_document.remove(db, id=document_id)
    return None
