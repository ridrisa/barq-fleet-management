from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Body
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.api.deps import get_db
from app.crud.workflow import workflow_attachment
from app.schemas.workflow import (
    WorkflowAttachmentCreate,
    WorkflowAttachmentUpdate,
    WorkflowAttachmentResponse,
    AttachmentUploadRequest,
    AttachmentDownloadResponse,
)

router = APIRouter()


@router.get("/", response_model=List[WorkflowAttachmentResponse])
def list_attachments(
    workflow_instance_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List workflow attachments with optional filtering by workflow instance"""
    if workflow_instance_id:
        attachments = db.query(workflow_attachment.model).filter(
            workflow_attachment.model.workflow_instance_id == workflow_instance_id
        ).offset(skip).limit(limit).all()
    else:
        attachments = workflow_attachment.get_multi(db, skip=skip, limit=limit)
    return attachments


@router.post("/upload", response_model=WorkflowAttachmentResponse, status_code=201)
async def upload_attachment(
    workflow_instance_id: int = Body(...),
    uploaded_by_id: int = Body(...),
    description: Optional[str] = Body(None),
    is_public: bool = Body(False),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload a file attachment to a workflow instance"""
    # In production, this would upload to S3 or similar storage
    # For now, we'll simulate the upload

    file_path = f"/uploads/workflows/{workflow_instance_id}/{file.filename}"
    file_size = 0  # Would get actual size from upload

    attachment_in = WorkflowAttachmentCreate(
        workflow_instance_id=workflow_instance_id,
        uploaded_by_id=uploaded_by_id,
        file_name=file.filename,
        file_path=file_path,
        file_size=file_size,
        file_type=file.content_type,
        description=description,
        is_public=is_public,
    )

    attachment = workflow_attachment.create(db, obj_in=attachment_in)
    return attachment


@router.get("/{attachment_id}", response_model=WorkflowAttachmentResponse)
def get_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
):
    """Get a workflow attachment by ID"""
    attachment = workflow_attachment.get(db, id=attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    return attachment


@router.get("/{attachment_id}/download", response_model=AttachmentDownloadResponse)
def get_download_url(
    attachment_id: int,
    db: Session = Depends(get_db),
):
    """Get a temporary download URL for an attachment"""
    attachment = workflow_attachment.get(db, id=attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # Increment download count
    attachment.download_count += 1
    db.commit()

    # Generate temporary download URL (valid for 1 hour)
    # In production, this would be a pre-signed S3 URL
    download_url = f"/api/files/download/{attachment.file_path}"
    expires_at = datetime.utcnow() + timedelta(hours=1)

    return AttachmentDownloadResponse(
        file_url=download_url,
        file_name=attachment.file_name,
        file_size=attachment.file_size or 0,
        expires_at=expires_at,
    )


@router.put("/{attachment_id}", response_model=WorkflowAttachmentResponse)
def update_attachment(
    attachment_id: int,
    attachment_in: WorkflowAttachmentUpdate,
    db: Session = Depends(get_db),
):
    """Update attachment metadata"""
    attachment = workflow_attachment.get(db, id=attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    attachment = workflow_attachment.update(db, db_obj=attachment, obj_in=attachment_in)
    return attachment


@router.delete("/{attachment_id}", status_code=204)
def delete_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
):
    """Delete a workflow attachment"""
    attachment = workflow_attachment.get(db, id=attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # In production, would also delete the file from storage
    workflow_attachment.remove(db, id=attachment_id)
    return None


@router.post("/{attachment_id}/scan", response_model=WorkflowAttachmentResponse)
def trigger_virus_scan(
    attachment_id: int,
    db: Session = Depends(get_db),
):
    """Trigger a virus scan for an attachment"""
    attachment = workflow_attachment.get(db, id=attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # In production, this would trigger actual virus scanning
    # For now, we'll mark it as scanned and clean
    attachment.is_scanned = True
    attachment.scan_result = "clean"
    attachment.scan_date = datetime.utcnow()
    db.commit()
    db.refresh(attachment)

    return attachment
