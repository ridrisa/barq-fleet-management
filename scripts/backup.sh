#!/bin/bash

################################################################################
# BARQ Fleet Management - Database Backup Script
# Usage: ./scripts/backup.sh [environment]
################################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
ENVIRONMENT="${1:-production}"
PROJECT_ID="${GCP_PROJECT_ID:-}"
BACKUP_BUCKET="${BACKUP_BUCKET:-barq-fleet-backups}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

backup_database() {
    log_info "Starting database backup for ${ENVIRONMENT}..."

    local INSTANCE_NAME="barq-postgres-${ENVIRONMENT}"
    local BACKUP_NAME="barq-backup-${ENVIRONMENT}-${TIMESTAMP}"

    # Create Cloud SQL backup
    gcloud sql backups create \
        --instance="${INSTANCE_NAME}" \
        --description="Automated backup on ${TIMESTAMP}" \
        --project="${PROJECT_ID}"

    log_success "Database backup created: ${BACKUP_NAME}"

    # Export to GCS
    local GCS_PATH="gs://${BACKUP_BUCKET}/sql/${ENVIRONMENT}/${BACKUP_NAME}.sql"

    gcloud sql export sql "${INSTANCE_NAME}" "${GCS_PATH}" \
        --database=barq_fleet \
        --project="${PROJECT_ID}"

    log_success "Database exported to: ${GCS_PATH}"
}

backup_redis() {
    log_info "Starting Redis backup for ${ENVIRONMENT}..."

    # TODO: Implement Redis backup
    log_info "Redis backup not implemented (uses persistence)"
}

cleanup_old_backups() {
    log_info "Cleaning up backups older than ${RETENTION_DAYS} days..."

    local CUTOFF_DATE=$(date -d "${RETENTION_DAYS} days ago" +%Y%m%d 2>/dev/null || date -v-${RETENTION_DAYS}d +%Y%m%d)

    # List and delete old backups
    gsutil ls "gs://${BACKUP_BUCKET}/sql/${ENVIRONMENT}/" | while read -r backup; do
        local backup_date=$(echo "$backup" | grep -oE '[0-9]{8}' | head -1)
        if [[ "$backup_date" < "$CUTOFF_DATE" ]]; then
            log_info "Deleting old backup: $backup"
            gsutil rm "$backup"
        fi
    done

    log_success "Cleanup completed"
}

verify_backup() {
    log_info "Verifying backup..."

    local GCS_PATH="gs://${BACKUP_BUCKET}/sql/${ENVIRONMENT}/barq-backup-${ENVIRONMENT}-${TIMESTAMP}.sql"

    if gsutil stat "$GCS_PATH" &> /dev/null; then
        local SIZE=$(gsutil du -s "$GCS_PATH" | awk '{print $1}')
        log_success "Backup verified. Size: $(numfmt --to=iec-i --suffix=B $SIZE)"
    else
        log_error "Backup verification failed"
        exit 1
    fi
}

main() {
    echo "========================================="
    echo "  BARQ Fleet Backup"
    echo "========================================="
    echo "Environment: ${ENVIRONMENT}"
    echo "Project: ${PROJECT_ID}"
    echo "Bucket: ${BACKUP_BUCKET}"
    echo "========================================="

    backup_database
    backup_redis
    verify_backup
    cleanup_old_backups

    log_success "Backup completed successfully! 💾"
}

main "$@"
