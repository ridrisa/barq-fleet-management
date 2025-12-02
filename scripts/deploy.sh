#!/bin/bash

################################################################################
# BARQ Fleet Management - Deployment Script
# Usage: ./scripts/deploy.sh [environment] [component]
# Example: ./scripts/deploy.sh production backend
################################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT="${1:-staging}"
COMPONENT="${2:-all}"
PROJECT_ID="${GCP_PROJECT_ID:-}"
REGION="${GCP_REGION:-us-central1}"
REPOSITORY="barq-fleet"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check gcloud
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI not found. Please install Google Cloud SDK."
        exit 1
    fi

    # Check docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found. Please install Docker."
        exit 1
    fi

    # Check project ID
    if [ -z "$PROJECT_ID" ]; then
        log_error "GCP_PROJECT_ID environment variable not set."
        exit 1
    fi

    # Verify gcloud authentication
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
        log_error "Not authenticated with gcloud. Run: gcloud auth login"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

build_and_push_backend() {
    log_info "Building and pushing backend image..."

    local IMAGE_TAG="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/barq-api:${ENVIRONMENT}-$(git rev-parse --short HEAD)"
    local IMAGE_LATEST="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/barq-api:${ENVIRONMENT}-latest"

    # Build image
    docker build \
        -f backend/Dockerfile.prod \
        -t "${IMAGE_TAG}" \
        -t "${IMAGE_LATEST}" \
        backend/

    # Push images
    docker push "${IMAGE_TAG}"
    docker push "${IMAGE_LATEST}"

    log_success "Backend image built and pushed: ${IMAGE_TAG}"
}

build_and_push_frontend() {
    log_info "Building and pushing frontend image..."

    local IMAGE_TAG="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/barq-web:${ENVIRONMENT}-$(git rev-parse --short HEAD)"
    local IMAGE_LATEST="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/barq-web:${ENVIRONMENT}-latest"

    # Build image
    docker build \
        -f frontend/Dockerfile.prod \
        --build-arg VITE_API_URL="https://api-${ENVIRONMENT}.barq-fleet.com/api/v1" \
        -t "${IMAGE_TAG}" \
        -t "${IMAGE_LATEST}" \
        frontend/

    # Push images
    docker push "${IMAGE_TAG}"
    docker push "${IMAGE_LATEST}"

    log_success "Frontend image built and pushed: ${IMAGE_TAG}"
}

deploy_backend() {
    log_info "Deploying backend to Cloud Run..."

    local SERVICE_NAME="barq-api-${ENVIRONMENT}"
    local IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/barq-api:${ENVIRONMENT}-latest"

    gcloud run deploy "${SERVICE_NAME}" \
        --image="${IMAGE}" \
        --platform=managed \
        --region="${REGION}" \
        --allow-unauthenticated \
        --min-instances=2 \
        --max-instances=100 \
        --cpu=2 \
        --memory=2Gi \
        --timeout=300s \
        --set-env-vars="ENVIRONMENT=${ENVIRONMENT}" \
        --project="${PROJECT_ID}"

    log_success "Backend deployed successfully"

    # Get service URL
    local SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
        --platform=managed \
        --region="${REGION}" \
        --project="${PROJECT_ID}" \
        --format='value(status.url)')

    log_info "Backend URL: ${SERVICE_URL}"
}

deploy_frontend() {
    log_info "Deploying frontend to Cloud Run..."

    local SERVICE_NAME="barq-web-${ENVIRONMENT}"
    local IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/barq-web:${ENVIRONMENT}-latest"

    gcloud run deploy "${SERVICE_NAME}" \
        --image="${IMAGE}" \
        --platform=managed \
        --region="${REGION}" \
        --allow-unauthenticated \
        --min-instances=1 \
        --max-instances=50 \
        --cpu=1 \
        --memory=512Mi \
        --timeout=60s \
        --project="${PROJECT_ID}"

    log_success "Frontend deployed successfully"

    # Get service URL
    local SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
        --platform=managed \
        --region="${REGION}" \
        --project="${PROJECT_ID}" \
        --format='value(status.url)')

    log_info "Frontend URL: ${SERVICE_URL}"
}

run_migrations() {
    log_info "Running database migrations..."

    # TODO: Implement migration runner
    log_warning "Migration step not implemented yet"
}

health_check() {
    log_info "Performing health checks..."

    local BACKEND_URL=$(gcloud run services describe "barq-api-${ENVIRONMENT}" \
        --platform=managed \
        --region="${REGION}" \
        --project="${PROJECT_ID}" \
        --format='value(status.url)')

    # Check backend health
    if curl -f "${BACKEND_URL}/api/v1/health" &> /dev/null; then
        log_success "Backend health check passed"
    else
        log_error "Backend health check failed"
        exit 1
    fi

    # Check frontend health
    local FRONTEND_URL=$(gcloud run services describe "barq-web-${ENVIRONMENT}" \
        --platform=managed \
        --region="${REGION}" \
        --project="${PROJECT_ID}" \
        --format='value(status.url)')

    if curl -f "${FRONTEND_URL}/health" &> /dev/null; then
        log_success "Frontend health check passed"
    else
        log_error "Frontend health check failed"
        exit 1
    fi
}

main() {
    echo "========================================="
    echo "  BARQ Fleet Deployment"
    echo "========================================="
    echo "Environment: ${ENVIRONMENT}"
    echo "Component: ${COMPONENT}"
    echo "Project: ${PROJECT_ID}"
    echo "Region: ${REGION}"
    echo "========================================="

    check_prerequisites

    case "${COMPONENT}" in
        backend)
            build_and_push_backend
            deploy_backend
            health_check
            ;;
        frontend)
            build_and_push_frontend
            deploy_frontend
            health_check
            ;;
        all)
            build_and_push_backend
            build_and_push_frontend
            run_migrations
            deploy_backend
            deploy_frontend
            health_check
            ;;
        *)
            log_error "Invalid component: ${COMPONENT}. Choose: backend, frontend, or all"
            exit 1
            ;;
    esac

    log_success "Deployment completed successfully! 🚀"
}

main "$@"
