#!/bin/bash

# Emergency Rollback Script for Production
# Usage: ./rollback-production.sh [REVISION_NAME]

set -euo pipefail

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-barq-fleet}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="barq-api-production"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

confirm_rollback() {
    echo ""
    log_warn "⚠️  EMERGENCY ROLLBACK - PRODUCTION"
    echo "You are about to rollback production to: ${TARGET_REVISION}"
    echo ""
    read -p "Are you absolutely sure? (yes/no): " -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log_info "Rollback cancelled"
        exit 0
    fi
}

# Set project
gcloud config set project "${PROJECT_ID}"

# Get current revisions
log_info "Fetching current revisions..."

REVISIONS=$(gcloud run revisions list \
    --service "${SERVICE_NAME}" \
    --region "${REGION}" \
    --format "table(metadata.name,status.conditions[0].status,metadata.creationTimestamp)" \
    --limit 10)

echo ""
echo "Available revisions:"
echo "${REVISIONS}"
echo ""

# Determine target revision
if [ $# -eq 0 ]; then
    # No argument provided - get previous revision
    log_info "No revision specified. Finding previous revision..."

    CURRENT_REVISION=$(gcloud run services describe "${SERVICE_NAME}" \
        --region "${REGION}" \
        --format 'value(status.traffic[0].revisionName)')

    log_info "Current revision: ${CURRENT_REVISION}"

    # Get all revisions sorted by creation time
    ALL_REVISIONS=$(gcloud run revisions list \
        --service "${SERVICE_NAME}" \
        --region "${REGION}" \
        --format 'value(metadata.name)' \
        --sort-by '~metadata.creationTimestamp')

    # Find previous revision (the one right after current in the list)
    TARGET_REVISION=$(echo "${ALL_REVISIONS}" | grep -A1 "^${CURRENT_REVISION}$" | tail -n1)

    if [ -z "${TARGET_REVISION}" ] || [ "${TARGET_REVISION}" == "${CURRENT_REVISION}" ]; then
        log_error "Could not find previous revision!"
        echo ""
        echo "Please specify a revision manually:"
        echo "  ./rollback-production.sh <revision-name>"
        exit 1
    fi

    log_info "Previous revision: ${TARGET_REVISION}"
else
    TARGET_REVISION=$1
    log_info "Target revision: ${TARGET_REVISION}"

    # Verify revision exists
    if ! gcloud run revisions describe "${TARGET_REVISION}" \
        --region "${REGION}" \
        --service "${SERVICE_NAME}" \
        --format 'value(metadata.name)' > /dev/null 2>&1; then
        log_error "Revision ${TARGET_REVISION} not found!"
        exit 1
    fi
fi

# Confirm rollback
confirm_rollback

# Record start time
START_TIME=$(date +%s)

log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "🚨 STARTING EMERGENCY ROLLBACK"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Perform rollback
log_info "Rolling back to: ${TARGET_REVISION}"

gcloud run services update-traffic "${SERVICE_NAME}" \
    --to-revisions "${TARGET_REVISION}=100" \
    --region "${REGION}" \
    --quiet

# Calculate rollback time
END_TIME=$(date +%s)
ROLLBACK_TIME=$((END_TIME - START_TIME))

log_info "Rollback completed in ${ROLLBACK_TIME} seconds"

# Wait for traffic to stabilize
log_info "Waiting for traffic to stabilize..."
sleep 30

# Verify rollback
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
    --region "${REGION}" \
    --format 'value(status.url)')

log_info "Running health checks..."

# Health check
if curl -f -s "${SERVICE_URL}/health" > /dev/null; then
    log_info "✅ Health check passed"
else
    log_error "❌ Health check failed!"
    log_error "Manual intervention required!"
    exit 1
fi

# Get detailed health status
HEALTH_RESPONSE=$(curl -s "${SERVICE_URL}/health/detailed")
HEALTH_STATUS=$(echo "${HEALTH_RESPONSE}" | jq -r '.status')
HEALTH_VERSION=$(echo "${HEALTH_RESPONSE}" | jq -r '.version')

if [ "${HEALTH_STATUS}" == "healthy" ]; then
    log_info "✅ Service is healthy"
    echo "Version: ${HEALTH_VERSION}"
else
    log_warn "⚠️  Service health check returned: ${HEALTH_STATUS}"
fi

# Display current traffic distribution
log_info "Current traffic distribution:"
gcloud run services describe "${SERVICE_NAME}" \
    --region "${REGION}" \
    --format 'table(status.traffic.revisionName,status.traffic.percent)'

# Success
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "✅ ROLLBACK COMPLETED SUCCESSFULLY"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Service URL: ${SERVICE_URL}"
echo "Rollback Time: ${ROLLBACK_TIME} seconds (Target: < 300s)"
echo "Active Revision: ${TARGET_REVISION}"
echo ""
log_info "Next steps:"
echo "  1. Monitor error rates and performance metrics"
echo "  2. Investigate root cause of the issue"
echo "  3. Create incident report"
echo "  4. Fix the issue and redeploy"
echo ""
log_info "Monitor logs:"
echo "  gcloud logging tail \"resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE_NAME}\""
echo ""
