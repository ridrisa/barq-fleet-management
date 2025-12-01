"""Backup Schemas"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class BackupBase(BaseModel):
    """Base Backup schema"""
    name: str = Field(..., min_length=1, max_length=200, description="Backup name")
    description: Optional[str] = Field(None, description="Backup description")
    backup_type: str = Field("full", description="Backup type (full, incremental, differential)")
    storage_type: str = Field("local", description="Storage location type")
    storage_path: Optional[str] = Field(None, description="Storage path or URL")
    storage_bucket: Optional[str] = Field(None, description="Cloud storage bucket name")
    is_compressed: bool = Field(True, description="Whether backup is compressed")
    compression_algorithm: Optional[str] = Field("gzip", description="Compression algorithm")
    is_encrypted: bool = Field(False, description="Whether backup is encrypted")
    encryption_algorithm: Optional[str] = Field(None, description="Encryption algorithm")
    expires_at: Optional[datetime] = Field(None, description="Expiration date")
    is_pinned: bool = Field(False, description="Whether backup is pinned (never auto-deleted)")
    environment: Optional[str] = Field(None, description="Environment (production, staging, dev)")
    tags: Optional[str] = Field(None, description="Comma-separated tags")


class BackupCreate(BackupBase):
    """Schema for creating a backup"""
    pass


class BackupUpdate(BaseModel):
    """Schema for updating a backup"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    is_pinned: Optional[bool] = None
    expires_at: Optional[datetime] = None
    tags: Optional[str] = None


class BackupResponse(BaseModel):
    """Schema for backup response"""
    id: int
    name: str
    description: Optional[str]
    backup_type: str
    status: str
    error_message: Optional[str]
    created_by_id: Optional[int]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    size_bytes: Optional[int]
    compressed_size_bytes: Optional[int]
    record_count: Optional[int]
    table_count: Optional[int]
    storage_type: str
    storage_path: Optional[str]
    storage_bucket: Optional[str]
    storage_key: Optional[str]
    is_compressed: bool
    compression_algorithm: Optional[str]
    is_encrypted: bool
    encryption_algorithm: Optional[str]
    is_verified: bool
    verified_at: Optional[datetime]
    checksum: Optional[str]
    checksum_algorithm: Optional[str]
    expires_at: Optional[datetime]
    is_pinned: bool
    last_restored_at: Optional[datetime]
    restoration_count: int
    last_restored_by_id: Optional[int]
    database_version: Optional[str]
    application_version: Optional[str]
    environment: Optional[str]
    tags: Optional[str]
    schedule_name: Optional[str]
    is_scheduled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BackupListResponse(BaseModel):
    """Schema for paginated backup list"""
    items: List[BackupResponse]
    total: int
    skip: int
    limit: int


class BackupStatsResponse(BaseModel):
    """Schema for backup statistics"""
    total_backups: int
    total_size_bytes: int
    total_size_gb: float
    successful_backups: int
    failed_backups: int
    oldest_backup: Optional[datetime]
    newest_backup: Optional[datetime]
    average_size_mb: float
    total_compressed_size_bytes: int
    total_compressed_size_gb: float
    average_compression_ratio: float


class BackupRestoreRequest(BaseModel):
    """Schema for backup restore request"""
    target_database: Optional[str] = Field(None, description="Target database name (optional)")
    confirm: bool = Field(False, description="Confirmation flag (must be true)")
    restore_specific_tables: Optional[List[str]] = Field(None, description="Restore only specific tables")


class BackupRestoreResponse(BaseModel):
    """Schema for backup restore response"""
    success: bool
    message: str
    backup_id: int
    restored_at: datetime
    duration_seconds: Optional[int]
    tables_restored: Optional[int]
    records_restored: Optional[int]
