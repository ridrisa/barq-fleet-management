#!/bin/bash

# Deploy to Production Environment with Canary Strategy
# Usage: ./deploy-production.sh [IMAGE_TAG]

set -euo pipefail

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-barq-fleet}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="barq-api-production"
ARTIFACT_REGISTRY="us-central1-docker.pkg.dev"

# Canary configuration
CANARY_STEP_1=10  # 10% traffic
CANARY_STEP_2=50  # 50% traffic
CANARY_WAIT_TIME=300  # 5 minutes between steps
ERROR_THRESHOLD=5  # Maximum errors allowed

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

confirm_deployment() {
    echo ""
    log_warn "⚠️  You are about to deploy to PRODUCTION!"
    echo "Image: ${IMAGE_URL}"
    echo ""
    read -p "Are you sure you want to continue? (yes/no): " -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log_info "Deployment cancelled"
        exit 0
    fi
}

check_errors() {
    local revision=$1
    local time_window=$2

    log_info "Checking error rate for revision: ${revision}"

    ERROR_COUNT=$(gcloud logging read \
        "resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE_NAME} AND resource.labels.revision_name=${revision} AND severity>=ERROR" \
        --limit 100 \
        --format json \
        --freshness="${time_window}m" | jq '. | length')

    log_info "Errors found in last ${time_window} minutes: ${ERROR_COUNT}"

    if [ "${ERROR_COUNT}" -gt "${ERROR_THRESHOLD}" ]; then
        log_error "Error threshold exceeded! (${ERROR_COUNT} > ${ERROR_THRESHOLD})"
        return 1
    fi

    log_info "✅ Error rate within acceptable limits"
    return 0
}

rollback() {
    local previous_revision=$1

    log_error "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_error "🚨 ROLLING BACK TO PREVIOUS REVISION"
    log_error "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    gcloud run services update-traffic "${SERVICE_NAME}" \
        --to-revisions "${previous_revision}=100" \
        --region "${REGION}" \
        --quiet

    log_info "✅ Rollback completed. Previous revision is serving 100% traffic"
    exit 1
}

# Get image tag (use argument or latest)
IMAGE_TAG="${1:-latest}"
IMAGE_URL="${ARTIFACT_REGISTRY}/${PROJECT_ID}/barq-artifacts/barq-api:${IMAGE_TAG}"

log_info "Starting production deployment with canary strategy..."
log_info "Image: ${IMAGE_URL}"

# Confirm deployment
confirm_deployment

# Verify gcloud authentication
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    log_error "Not authenticated with gcloud. Run: gcloud auth login"
    exit 1
fi

# Set project
gcloud config set project "${PROJECT_ID}"

# Get current production revision
log_step "Getting current production revision..."
CURRENT_REVISION=$(gcloud run services describe "${SERVICE_NAME}" \
    --region "${REGION}" \
    --format 'value(status.traffic[0].revisionName)' 2>/dev/null || echo "none")

if [ "${CURRENT_REVISION}" == "none" ]; then
    log_warn "No current revision found. This is a fresh deployment."
else
    log_info "Current revision: ${CURRENT_REVISION}"
fi

# Deploy new revision without traffic
log_step "Deploying new revision (0% traffic)..."
gcloud run deploy "${SERVICE_NAME}" \
    --image "${IMAGE_URL}" \
    --region "${REGION}" \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "ENVIRONMENT=production,DEPLOYED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --set-secrets "DATABASE_URL=production-database-url:latest,SECRET_KEY=production-secret-key:latest" \
    --cpu 4 \
    --memory 4Gi \
    --min-instances 2 \
    --max-instances 50 \
    --concurrency 100 \
    --timeout 300 \
    --no-traffic \
    --quiet

# Get new revision
NEW_REVISION=$(gcloud run services describe "${SERVICE_NAME}" \
    --region "${REGION}" \
    --format 'value(status.latestCreatedRevisionName)')

log_info "New revision: ${NEW_REVISION}"

# Get service URL
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
    --region "${REGION}" \
    --format 'value(status.url)')

# Run smoke tests on new revision
log_step "Running smoke tests on new revision..."

# The new revision is tagged, so we can test it directly
REVISION_URL=$(gcloud run services describe "${SERVICE_NAME}" \
    --region "${REGION}" \
    --format "value(status.traffic.where(revisionName='${NEW_REVISION}').url.first())")

if [ -z "${REVISION_URL}" ]; then
    REVISION_URL="${SERVICE_URL}"
fi

# Smoke tests
if ! curl -f -s "${SERVICE_URL}/health/live" > /dev/null; then
    log_error "Liveness check failed!"
    exit 1
fi

if ! curl -f -s "${SERVICE_URL}/health/ready" > /dev/null; then
    log_error "Readiness check failed!"
    exit 1
fi

log_info "✅ Smoke tests passed"

# Canary Step 1: 10% traffic
log_step "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_step "Canary Step 1: Shifting ${CANARY_STEP_1}% traffic to new revision"
log_step "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

gcloud run services update-traffic "${SERVICE_NAME}" \
    --to-revisions "${NEW_REVISION}=${CANARY_STEP_1}" \
    --region "${REGION}" \
    --quiet

log_info "Monitoring for ${CANARY_WAIT_TIME} seconds..."
sleep "${CANARY_WAIT_TIME}"

if ! check_errors "${NEW_REVISION}" 5; then
    rollback "${CURRENT_REVISION}"
fi

# Canary Step 2: 50% traffic
log_step "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_step "Canary Step 2: Shifting ${CANARY_STEP_2}% traffic to new revision"
log_step "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

gcloud run services update-traffic "${SERVICE_NAME}" \
    --to-revisions "${NEW_REVISION}=${CANARY_STEP_2}" \
    --region "${REGION}" \
    --quiet

log_info "Monitoring for ${CANARY_WAIT_TIME} seconds..."
sleep "${CANARY_WAIT_TIME}"

if ! check_errors "${NEW_REVISION}" 5; then
    rollback "${CURRENT_REVISION}"
fi

# Full rollout: 100% traffic
log_step "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_step "Final Step: Shifting 100% traffic to new revision"
log_step "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

gcloud run services update-traffic "${SERVICE_NAME}" \
    --to-latest \
    --region "${REGION}" \
    --quiet

# Final verification
log_info "Running final verification..."
sleep 60

HEALTH_RESPONSE=$(curl -s "${SERVICE_URL}/health/detailed")
HEALTH_STATUS=$(echo "${HEALTH_RESPONSE}" | jq -r '.status')

if [ "${HEALTH_STATUS}" != "healthy" ]; then
    log_error "Final health check failed!"
    rollback "${CURRENT_REVISION}"
fi

# Success!
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "🎉 Production deployment completed successfully!"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Service URL: ${SERVICE_URL}"
echo "API Docs: ${SERVICE_URL}/api/v1/docs"
echo "Health Check: ${SERVICE_URL}/health/detailed"
echo ""
echo "Deployed Revision: ${NEW_REVISION}"
echo "Previous Revision: ${CURRENT_REVISION}"
echo ""
log_info "Monitor the deployment:"
echo "  gcloud run services describe ${SERVICE_NAME} --region ${REGION}"
echo "  gcloud logging tail \"resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE_NAME}\""
echo ""
