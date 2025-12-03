"""Backup Model for Database Backups"""
import enum
from sqlalchemy import Column, Integer, String, BigInteger, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class BackupType(str, enum.Enum):
    """Backup types"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"


class BackupStatus(str, enum.Enum):
    """Backup status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"
    CORRUPTED = "corrupted"


class BackupStorage(str, enum.Enum):
    """Backup storage locations"""
    LOCAL = "local"
    S3 = "s3"
    GCS = "gcs"  # Google Cloud Storage
    AZURE = "azure"
    FTP = "ftp"
    SFTP = "sftp"


class Backup(TenantMixin, BaseModel):
    """
    Backup model for database backup management

    This model tracks database backups including:
    - Backup metadata (type, size, status)
    - Storage location
    - Verification status
    - Restoration information
    - Retention policy

    Features:
    - Scheduled backups
    - Manual on-demand backups
    - Backup verification
    - Multi-location storage
    - Retention management
    - Point-in-time recovery
    """
    __tablename__ = "backups"

    # Basic information
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    backup_type = Column(String(20), default=BackupType.FULL.value, nullable=False)

    # Status
    status = Column(String(20), default=BackupStatus.PENDING.value, nullable=False)
    error_message = Column(Text, nullable=True)

    # Creator
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_by = relationship("User", foreign_keys=[created_by_id])

    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    # Size and content
    size_bytes = Column(BigInteger, nullable=True)  # Backup file size
    compressed_size_bytes = Column(BigInteger, nullable=True)
    record_count = Column(Integer, nullable=True)  # Number of records backed up
    table_count = Column(Integer, nullable=True)  # Number of tables backed up

    # Storage
    storage_type = Column(String(20), default=BackupStorage.LOCAL.value, nullable=False)
    storage_path = Column(String(500), nullable=True)  # Local path or cloud URL
    storage_bucket = Column(String(200), nullable=True)  # S3 bucket, GCS bucket, etc.
    storage_key = Column(String(500), nullable=True)  # Object key in cloud storage

    # Compression and encryption
    is_compressed = Column(Boolean, default=True, nullable=False)
    compression_algorithm = Column(String(20), default="gzip", nullable=True)
    is_encrypted = Column(Boolean, default=False, nullable=False)
    encryption_algorithm = Column(String(20), nullable=True)

    # Verification
    is_verified = Column(Boolean, default=False, nullable=False)
    verified_at = Column(DateTime, nullable=True)
    checksum = Column(String(128), nullable=True)  # SHA256 checksum
    checksum_algorithm = Column(String(20), default="sha256", nullable=True)

    # Retention
    expires_at = Column(DateTime, nullable=True)  # When backup should be deleted
    is_pinned = Column(Boolean, default=False, nullable=False)  # If true, never auto-delete

    # Restoration tracking
    last_restored_at = Column(DateTime, nullable=True)
    restoration_count = Column(Integer, default=0, nullable=False)
    last_restored_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    last_restored_by = relationship("User", foreign_keys=[last_restored_by_id])

    # Metadata
    database_version = Column(String(50), nullable=True)
    application_version = Column(String(50), nullable=True)
    environment = Column(String(50), nullable=True)  # production, staging, development
    tags = Column(String(500), nullable=True)  # Comma-separated tags

    # Schedule reference
    schedule_name = Column(String(100), nullable=True)  # If created by schedule
    is_scheduled = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<Backup(name={self.name}, type={self.backup_type}, status={self.status})>"

    def calculate_duration(self):
        """Calculate and update backup duration"""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            self.duration_seconds = int(delta.total_seconds())

    def mark_started(self):
        """Mark backup as started"""
        self.status = BackupStatus.IN_PROGRESS.value
        self.started_at = datetime.utcnow()

    def mark_completed(self, size_bytes: int = None):
        """Mark backup as completed"""
        self.status = BackupStatus.COMPLETED.value
        self.completed_at = datetime.utcnow()
        if size_bytes:
            self.size_bytes = size_bytes
        self.calculate_duration()

    def mark_failed(self, error_message: str):
        """Mark backup as failed"""
        self.status = BackupStatus.FAILED.value
        self.error_message = error_message
        self.completed_at = datetime.utcnow()
        self.calculate_duration()

    def mark_verified(self, checksum: str = None):
        """Mark backup as verified"""
        self.is_verified = True
        self.verified_at = datetime.utcnow()
        self.status = BackupStatus.VERIFIED.value
        if checksum:
            self.checksum = checksum

    def is_expired(self) -> bool:
        """Check if backup has expired"""
        if self.is_pinned:
            return False
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def get_size_mb(self) -> float:
        """Get backup size in MB"""
        if not self.size_bytes:
            return 0.0
        return round(self.size_bytes / (1024 * 1024), 2)

    def get_compressed_size_mb(self) -> float:
        """Get compressed backup size in MB"""
        if not self.compressed_size_bytes:
            return 0.0
        return round(self.compressed_size_bytes / (1024 * 1024), 2)

    def get_compression_ratio(self) -> float:
        """Get compression ratio"""
        if not self.size_bytes or not self.compressed_size_bytes:
            return 0.0
        return round((1 - self.compressed_size_bytes / self.size_bytes) * 100, 2)
