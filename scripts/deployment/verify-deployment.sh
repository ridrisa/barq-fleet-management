#!/bin/bash

# Verify Deployment Health and Performance
# Usage: ./verify-deployment.sh [staging|production]

set -euo pipefail

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-barq-fleet}"
REGION="${GCP_REGION:-us-central1}"

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

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

run_test() {
    local test_name=$1
    local test_command=$2

    echo -n "Testing ${test_name}... "

    if eval "${test_command}" > /dev/null 2>&1; then
        log_pass "✅"
        return 0
    else
        log_fail "❌"
        return 1
    fi
}

# Determine environment
ENVIRONMENT="${1:-staging}"
SERVICE_NAME="barq-api-${ENVIRONMENT}"

log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "Verifying ${ENVIRONMENT} deployment"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Set project
gcloud config set project "${PROJECT_ID}" --quiet

# Get service URL
log_info "Getting service URL..."
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
    --region "${REGION}" \
    --format 'value(status.url)' 2>/dev/null || echo "")

if [ -z "${SERVICE_URL}" ]; then
    log_error "Service ${SERVICE_NAME} not found!"
    exit 1
fi

log_info "Service URL: ${SERVICE_URL}"

# Initialize test results
TOTAL_TESTS=0
PASSED_TESTS=0

# Test 1: Liveness Check
TOTAL_TESTS=$((TOTAL_TESTS + 1))
if run_test "Liveness (/health/live)" "curl -f -s ${SERVICE_URL}/health/live"; then
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

# Test 2: Readiness Check
TOTAL_TESTS=$((TOTAL_TESTS + 1))
if run_test "Readiness (/health/ready)" "curl -f -s ${SERVICE_URL}/health/ready"; then
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

# Test 3: Detailed Health Check
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "Testing Detailed Health (/health/detailed)... "
HEALTH_RESPONSE=$(curl -s "${SERVICE_URL}/health/detailed")
HEALTH_STATUS=$(echo "${HEALTH_RESPONSE}" | jq -r '.status')

if [ "${HEALTH_STATUS}" == "healthy" ]; then
    log_pass "✅"
    PASSED_TESTS=$((PASSED_TESTS + 1))

    # Display health details
    echo ""
    echo "Health Details:"
    echo "${HEALTH_RESPONSE}" | jq '{
        status: .status,
        version: .version,
        environment: .environment,
        database: .checks.database.status,
        db_latency_ms: .checks.database.latency_ms,
        cpu_percent: .system.cpu_percent,
        memory_percent: .system.memory.percent_used
    }'
    echo ""
else
    log_fail "❌ (Status: ${HEALTH_STATUS})"
fi

# Test 4: API Documentation
TOTAL_TESTS=$((TOTAL_TESTS + 1))
if run_test "API Docs (/api/v1/docs)" "curl -f -s ${SERVICE_URL}/api/v1/docs"; then
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

# Test 5: OpenAPI Spec
TOTAL_TESTS=$((TOTAL_TESTS + 1))
if run_test "OpenAPI Spec (/api/v1/openapi.json)" "curl -f -s ${SERVICE_URL}/api/v1/openapi.json"; then
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

# Test 6: Response Time
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "Testing Response Time... "
RESPONSE_TIME=$(curl -s -w '%{time_total}' -o /dev/null "${SERVICE_URL}/health/live")
RESPONSE_TIME_MS=$(echo "${RESPONSE_TIME} * 1000" | bc)

if (( $(echo "${RESPONSE_TIME} < 1.0" | bc -l) )); then
    log_pass "✅ (${RESPONSE_TIME_MS%.*}ms)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    log_fail "❌ (${RESPONSE_TIME_MS%.*}ms - Too slow!)"
fi

# Get service details
echo ""
log_info "Service Configuration:"

SERVICE_INFO=$(gcloud run services describe "${SERVICE_NAME}" \
    --region "${REGION}" \
    --format json)

echo "${SERVICE_INFO}" | jq '{
    service: .metadata.name,
    revision: .status.latestReadyRevisionName,
    url: .status.url,
    cpu: .spec.template.spec.containers[0].resources.limits.cpu,
    memory: .spec.template.spec.containers[0].resources.limits.memory,
    minInstances: .spec.template.metadata.annotations."autoscaling.knative.dev/minScale",
    maxInstances: .spec.template.metadata.annotations."autoscaling.knative.dev/maxScale",
    concurrency: .spec.template.spec.containerConcurrency
}'

# Check recent errors
echo ""
log_info "Checking recent errors (last 10 minutes)..."

ERROR_COUNT=$(gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE_NAME} AND severity>=ERROR" \
    --limit 100 \
    --format json \
    --freshness=10m 2>/dev/null | jq '. | length')

if [ "${ERROR_COUNT}" -eq 0 ]; then
    log_pass "No recent errors found"
elif [ "${ERROR_COUNT}" -lt 5 ]; then
    log_warn "Found ${ERROR_COUNT} errors (acceptable)"
else
    log_fail "Found ${ERROR_COUNT} errors (concerning!)"
    echo ""
    log_info "Recent error samples:"
    gcloud logging read \
        "resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE_NAME} AND severity>=ERROR" \
        --limit 5 \
        --format "table(timestamp,textPayload)" \
        --freshness=10m
fi

# Display traffic distribution
echo ""
log_info "Traffic Distribution:"
gcloud run services describe "${SERVICE_NAME}" \
    --region "${REGION}" \
    --format 'table(status.traffic.revisionName,status.traffic.percent,status.traffic.tag)'

# Summary
echo ""
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "Verification Summary"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Tests Passed: ${PASSED_TESTS}/${TOTAL_TESTS}"
echo "Environment: ${ENVIRONMENT}"
echo "Service: ${SERVICE_NAME}"
echo "Region: ${REGION}"
echo ""

if [ "${PASSED_TESTS}" -eq "${TOTAL_TESTS}" ]; then
    log_info "✅ All tests passed! Deployment is healthy."
    exit 0
else
    FAILED_TESTS=$((TOTAL_TESTS - PASSED_TESTS))
    log_error "❌ ${FAILED_TESTS} test(s) failed. Please investigate."
    exit 1
fi
