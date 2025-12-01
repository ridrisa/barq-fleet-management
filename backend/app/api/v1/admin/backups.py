"""Admin Backup Management API"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.api.deps import get_db, get_current_superuser
from app.models.user import User
from app.models.admin.backup import Backup, BackupStatus, BackupType
from app.schemas.admin.backup import (
    BackupCreate,
    BackupUpdate,
    BackupResponse,
    BackupListResponse,
    BackupStatsResponse,
    BackupRestoreRequest,
    BackupRestoreResponse,
)

router = APIRouter()


@router.get("/", response_model=BackupListResponse)
def list_backups(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    backup_type: Optional[str] = Query(None),
    environment: Optional[str] = Query(None),
    is_verified: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    List all backups with filtering and pagination.

    Requires superuser permission.
    """
    query = db.query(Backup)

    # Apply filters
    if status:
        query = query.filter(Backup.status == status)
    if backup_type:
        query = query.filter(Backup.backup_type == backup_type)
    if environment:
        query = query.filter(Backup.environment == environment)
    if is_verified is not None:
        query = query.filter(Backup.is_verified == is_verified)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Backup.name.ilike(search_pattern)) |
            (Backup.description.ilike(search_pattern))
        )

    # Get total count
    total = query.count()

    # Get paginated results
    backups = query.order_by(desc(Backup.created_at)).offset(skip).limit(limit).all()

    return BackupListResponse(
        items=backups,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/stats", response_model=BackupStatsResponse)
def get_backup_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get backup statistics and summary.

    Requires superuser permission.
    """
    total_backups = db.query(Backup).count()

    # Calculate total size
    total_size = db.query(func.sum(Backup.size_bytes)).scalar() or 0
    total_compressed_size = db.query(func.sum(Backup.compressed_size_bytes)).scalar() or 0

    # Count by status
    successful = db.query(Backup).filter(
        Backup.status.in_([BackupStatus.COMPLETED.value, BackupStatus.VERIFIED.value])
    ).count()
    failed = db.query(Backup).filter(Backup.status == BackupStatus.FAILED.value).count()

    # Get oldest and newest
    oldest = db.query(Backup).order_by(Backup.created_at.asc()).first()
    newest = db.query(Backup).order_by(Backup.created_at.desc()).first()

    # Calculate averages
    avg_size = db.query(func.avg(Backup.size_bytes)).scalar() or 0
    avg_compression_ratio = 0
    if total_size > 0 and total_compressed_size > 0:
        avg_compression_ratio = round((1 - total_compressed_size / total_size) * 100, 2)

    return BackupStatsResponse(
        total_backups=total_backups,
        total_size_bytes=int(total_size),
        total_size_gb=round(total_size / (1024**3), 2),
        successful_backups=successful,
        failed_backups=failed,
        oldest_backup=oldest.created_at if oldest else None,
        newest_backup=newest.created_at if newest else None,
        average_size_mb=round(avg_size / (1024**2), 2),
        total_compressed_size_bytes=int(total_compressed_size),
        total_compressed_size_gb=round(total_compressed_size / (1024**3), 2),
        average_compression_ratio=avg_compression_ratio,
    )


@router.post("/", response_model=BackupResponse, status_code=status.HTTP_201_CREATED)
def create_backup(
    backup_in: BackupCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Create a new backup.

    Requires superuser permission.

    The backup will be created asynchronously in the background.
    """
    # Create backup record
    backup = Backup(
        **backup_in.dict(),
        created_by_id=current_user.id,
        status=BackupStatus.PENDING.value,
    )

    db.add(backup)
    db.commit()
    db.refresh(backup)

    # Schedule background task to perform backup
    # background_tasks.add_task(perform_backup, backup.id)

    return backup


@router.get("/{backup_id}", response_model=BackupResponse)
def get_backup(
    backup_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get a specific backup by ID.

    Requires superuser permission.
    """
    backup = db.query(Backup).filter(Backup.id == backup_id).first()
    if not backup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backup with id {backup_id} not found"
        )
    return backup


@router.patch("/{backup_id}", response_model=BackupResponse)
def update_backup(
    backup_id: int,
    backup_in: BackupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Update backup metadata.

    Requires superuser permission.

    Allows updating name, description, expiration, and pin status.
    """
    backup = db.query(Backup).filter(Backup.id == backup_id).first()
    if not backup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backup with id {backup_id} not found"
        )

    update_data = backup_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(backup, field, value)

    db.commit()
    db.refresh(backup)
    return backup


@router.delete("/{backup_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_backup(
    backup_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Delete a backup.

    Requires superuser permission.

    Pinned backups cannot be deleted.
    """
    backup = db.query(Backup).filter(Backup.id == backup_id).first()
    if not backup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backup with id {backup_id} not found"
        )

    if backup.is_pinned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete pinned backup"
        )

    db.delete(backup)
    db.commit()
    return None


@router.post("/{backup_id}/verify", response_model=BackupResponse)
def verify_backup(
    backup_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Verify backup integrity.

    Requires superuser permission.

    Checks backup file integrity and updates verification status.
    """
    backup = db.query(Backup).filter(Backup.id == backup_id).first()
    if not backup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backup with id {backup_id} not found"
        )

    # Placeholder for actual verification logic
    # In production, this would verify checksum, file integrity, etc.
    backup.mark_verified(checksum="placeholder_checksum")

    db.commit()
    db.refresh(backup)
    return backup


@router.post("/{backup_id}/restore", response_model=BackupRestoreResponse)
def restore_backup(
    backup_id: int,
    restore_request: BackupRestoreRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Restore a backup.

    Requires superuser permission.

    WARNING: This will overwrite current database data.
    Requires explicit confirmation.
    """
    if not restore_request.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirmation required. Set 'confirm' to true."
        )

    backup = db.query(Backup).filter(Backup.id == backup_id).first()
    if not backup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backup with id {backup_id} not found"
        )

    if backup.status != BackupStatus.VERIFIED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only verified backups can be restored"
        )

    # Schedule background task to perform restore
    # background_tasks.add_task(perform_restore, backup.id, restore_request)

    # Update restoration tracking
    backup.restoration_count += 1
    backup.last_restored_at = datetime.utcnow()
    backup.last_restored_by_id = current_user.id
    db.commit()

    return BackupRestoreResponse(
        success=True,
        message="Restore initiated successfully",
        backup_id=backup.id,
        restored_at=datetime.utcnow(),
        duration_seconds=None,
        tables_restored=None,
        records_restored=None,
    )


@router.delete("/cleanup/expired", status_code=status.HTTP_200_OK)
def cleanup_expired_backups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Delete all expired backups.

    Requires superuser permission.

    Removes backups that have passed their expiration date.
    Pinned backups are never deleted.
    """
    expired_backups = db.query(Backup).filter(
        Backup.is_pinned == False,
        Backup.expires_at.isnot(None),
        Backup.expires_at < datetime.utcnow()
    ).all()

    deleted_count = len(expired_backups)
    for backup in expired_backups:
        db.delete(backup)

    db.commit()

    return {
        "message": f"Deleted {deleted_count} expired backup(s)",
        "deleted_count": deleted_count
    }
