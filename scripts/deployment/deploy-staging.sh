#!/bin/bash

# Deploy to Staging Environment
# Usage: ./deploy-staging.sh [IMAGE_TAG]

set -euo pipefail

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-barq-fleet}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="barq-api-staging"
ARTIFACT_REGISTRY="us-central1-docker.pkg.dev"

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

# Get image tag (use argument or latest)
IMAGE_TAG="${1:-latest}"
IMAGE_URL="${ARTIFACT_REGISTRY}/${PROJECT_ID}/barq-artifacts/barq-api:${IMAGE_TAG}"

log_info "Starting deployment to staging environment..."
log_info "Image: ${IMAGE_URL}"

# Verify gcloud authentication
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    log_error "Not authenticated with gcloud. Run: gcloud auth login"
    exit 1
fi

# Set project
log_info "Setting GCP project: ${PROJECT_ID}"
gcloud config set project "${PROJECT_ID}"

# Deploy to Cloud Run
log_info "Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
    --image "${IMAGE_URL}" \
    --region "${REGION}" \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "ENVIRONMENT=staging,DEPLOYED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --set-secrets "DATABASE_URL=staging-database-url:latest,SECRET_KEY=staging-secret-key:latest" \
    --cpu 2 \
    --memory 2Gi \
    --min-instances 1 \
    --max-instances 10 \
    --concurrency 80 \
    --timeout 300 \
    --quiet

# Get service URL
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
    --region "${REGION}" \
    --format 'value(status.url)')

log_info "Service deployed at: ${SERVICE_URL}"

# Run health checks
log_info "Running health checks..."

# Liveness check
if curl -f -s "${SERVICE_URL}/health/live" > /dev/null; then
    log_info "✅ Liveness check passed"
else
    log_error "❌ Liveness check failed"
    exit 1
fi

# Readiness check
if curl -f -s "${SERVICE_URL}/health/ready" > /dev/null; then
    log_info "✅ Readiness check passed"
else
    log_error "❌ Readiness check failed"
    exit 1
fi

# Detailed health check
HEALTH_RESPONSE=$(curl -s "${SERVICE_URL}/health/detailed")
HEALTH_STATUS=$(echo "${HEALTH_RESPONSE}" | jq -r '.status')

if [ "${HEALTH_STATUS}" == "healthy" ]; then
    log_info "✅ Detailed health check passed"
    echo "${HEALTH_RESPONSE}" | jq '.'
else
    log_error "❌ Detailed health check failed"
    echo "${HEALTH_RESPONSE}" | jq '.'
    exit 1
fi

# Display deployment info
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "🎉 Deployment to staging completed successfully!"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Service URL: ${SERVICE_URL}"
echo "API Docs: ${SERVICE_URL}/api/v1/docs"
echo "Health Check: ${SERVICE_URL}/health/detailed"
echo ""
log_info "Next steps:"
echo "  1. Test the staging environment thoroughly"
echo "  2. Run integration tests"
echo "  3. Deploy to production: ./deploy-production.sh ${IMAGE_TAG}"
echo ""
