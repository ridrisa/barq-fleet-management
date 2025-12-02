#!/bin/bash

################################################################################
# BARQ Fleet Management - Health Check Script
# Usage: ./scripts/health-check.sh [environment]
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
REGION="${GCP_REGION:-us-central1}"

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

check_service() {
    local SERVICE_NAME=$1
    local HEALTH_PATH=$2

    log_info "Checking ${SERVICE_NAME}..."

    # Get service URL
    local SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}-${ENVIRONMENT}" \
        --platform=managed \
        --region="${REGION}" \
        --project="${PROJECT_ID}" \
        --format='value(status.url)' 2>/dev/null)

    if [ -z "$SERVICE_URL" ]; then
        log_error "${SERVICE_NAME} service not found"
        return 1
    fi

    # Check health endpoint
    local HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${SERVICE_URL}${HEALTH_PATH}" --max-time 10)

    if [ "$HTTP_CODE" = "200" ]; then
        log_success "${SERVICE_NAME} is healthy (${SERVICE_URL})"
        return 0
    else
        log_error "${SERVICE_NAME} is unhealthy (HTTP ${HTTP_CODE})"
        return 1
    fi
}

check_database() {
    log_info "Checking database..."

    local INSTANCE_NAME="barq-postgres-${ENVIRONMENT}"

    # Check if instance is running
    local STATE=$(gcloud sql instances describe "${INSTANCE_NAME}" \
        --project="${PROJECT_ID}" \
        --format='value(state)' 2>/dev/null)

    if [ "$STATE" = "RUNNABLE" ]; then
        log_success "Database is running"
        return 0
    else
        log_error "Database is not running (state: ${STATE})"
        return 1
    fi
}

check_redis() {
    log_info "Checking Redis..."

    local INSTANCE_NAME="barq-redis-${ENVIRONMENT}"

    # Check if instance is running
    local STATE=$(gcloud redis instances describe "${INSTANCE_NAME}" \
        --region="${REGION}" \
        --project="${PROJECT_ID}" \
        --format='value(state)' 2>/dev/null)

    if [ "$STATE" = "READY" ]; then
        log_success "Redis is ready"
        return 0
    else
        log_error "Redis is not ready (state: ${STATE})"
        return 1
    fi
}

check_monitoring() {
    log_info "Checking monitoring..."

    # Check if monitoring workspace exists
    local WORKSPACE=$(gcloud monitoring dashboards list \
        --project="${PROJECT_ID}" \
        --filter="displayName:BARQ" \
        --format='value(name)' 2>/dev/null | head -1)

    if [ -n "$WORKSPACE" ]; then
        log_success "Monitoring is configured"
        return 0
    else
        log_warning "No monitoring dashboards found"
        return 0
    fi
}

get_metrics() {
    log_info "Fetching metrics..."

    # Backend metrics
    local BACKEND_INSTANCES=$(gcloud run services describe "barq-api-${ENVIRONMENT}" \
        --platform=managed \
        --region="${REGION}" \
        --project="${PROJECT_ID}" \
        --format='value(status.traffic[0].revisionName)' 2>/dev/null)

    if [ -n "$BACKEND_INSTANCES" ]; then
        echo "  Backend revision: ${BACKEND_INSTANCES}"
    fi

    # Database connections
    local DB_CONNECTIONS=$(gcloud sql operations list \
        --instance="barq-postgres-${ENVIRONMENT}" \
        --project="${PROJECT_ID}" \
        --limit=1 \
        --format='value(status)' 2>/dev/null)

    if [ -n "$DB_CONNECTIONS" ]; then
        echo "  Last DB operation: ${DB_CONNECTIONS}"
    fi
}

main() {
    echo "========================================="
    echo "  BARQ Fleet Health Check"
    echo "========================================="
    echo "Environment: ${ENVIRONMENT}"
    echo "Project: ${PROJECT_ID}"
    echo "Region: ${REGION}"
    echo "========================================="
    echo ""

    local FAILED=0

    # Check all services
    check_service "barq-api" "/api/v1/health" || ((FAILED++))
    check_service "barq-web" "/health" || ((FAILED++))
    check_database || ((FAILED++))
    check_redis || ((FAILED++))
    check_monitoring

    echo ""
    echo "========================================="
    get_metrics
    echo "========================================="
    echo ""

    if [ $FAILED -eq 0 ]; then
        log_success "All health checks passed! ✨"
        exit 0
    else
        log_error "${FAILED} health check(s) failed"
        exit 1
    fi
}

main "$@"
