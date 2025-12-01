#!/bin/bash

##############################################
# BARQ Fleet Management - Comprehensive Test Runner
# Runs all test suites and generates reports
##############################################

set -e  # Exit on error

echo "=========================================="
echo "BARQ Fleet Management - Test Suite Runner"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results tracking
UNIT_TESTS_PASSED=0
E2E_TESTS_PASSED=0
LOAD_TESTS_PASSED=0

##############################################
# 1. Unit Tests
##############################################

echo -e "${YELLOW}[1/4] Running Unit Tests...${NC}"
echo "=========================================="
echo ""

# Frontend unit tests
echo "Running Frontend Unit Tests..."
cd frontend
if npm run test:coverage; then
    echo -e "${GREEN}✓ Frontend unit tests passed${NC}"
    UNIT_TESTS_PASSED=$((UNIT_TESTS_PASSED + 1))
else
    echo -e "${RED}✗ Frontend unit tests failed${NC}"
fi
cd ..

echo ""

# Backend unit tests
echo "Running Backend Unit Tests..."
cd backend
if npm run test:coverage; then
    echo -e "${GREEN}✓ Backend unit tests passed${NC}"
    UNIT_TESTS_PASSED=$((UNIT_TESTS_PASSED + 1))
else
    echo -e "${RED}✗ Backend unit tests failed${NC}"
fi
cd ..

echo ""
echo -e "${GREEN}Unit Tests Summary: ${UNIT_TESTS_PASSED}/2 suites passed${NC}"
echo ""

##############################################
# 2. E2E Tests
##############################################

echo -e "${YELLOW}[2/4] Running E2E Tests...${NC}"
echo "=========================================="
echo ""

cd frontend

echo "Starting backend server for E2E tests..."
cd ../backend
npm start &
BACKEND_PID=$!
sleep 10  # Wait for backend to start

cd ../frontend

echo "Running Playwright E2E Tests..."
if npm run test:e2e; then
    echo -e "${GREEN}✓ E2E tests passed${NC}"
    E2E_TESTS_PASSED=1
else
    echo -e "${RED}✗ E2E tests failed${NC}"
fi

# Stop backend server
echo "Stopping backend server..."
kill $BACKEND_PID 2>/dev/null || true

cd ..

echo ""
echo -e "${GREEN}E2E Tests Summary: ${E2E_TESTS_PASSED}/1 suite passed${NC}"
echo ""

##############################################
# 3. Load Tests (Optional - only if k6 installed)
##############################################

echo -e "${YELLOW}[3/4] Running Load Tests...${NC}"
echo "=========================================="
echo ""

# Check if k6 is installed
if command -v k6 &> /dev/null; then
    echo "k6 found. Running load tests..."

    # Start backend server
    cd backend
    npm start &
    BACKEND_PID=$!
    sleep 10
    cd ..

    # Run API load test
    echo "Running API Load Test..."
    if k6 run tests/load/api-load-test.js; then
        echo -e "${GREEN}✓ API load test passed${NC}"
        LOAD_TESTS_PASSED=$((LOAD_TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ API load test failed${NC}"
    fi

    # Run workflow load test
    echo "Running Workflow Load Test..."
    if k6 run tests/load/workflow-load-test.js; then
        echo -e "${GREEN}✓ Workflow load test passed${NC}"
        LOAD_TESTS_PASSED=$((LOAD_TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ Workflow load test failed${NC}"
    fi

    # Stop backend server
    kill $BACKEND_PID 2>/dev/null || true

    echo ""
    echo -e "${GREEN}Load Tests Summary: ${LOAD_TESTS_PASSED}/2 tests passed${NC}"
else
    echo -e "${YELLOW}⚠ k6 not installed. Skipping load tests.${NC}"
    echo "Install k6: https://k6.io/docs/get-started/installation/"
    LOAD_TESTS_PASSED=-1  # Mark as skipped
fi

echo ""

##############################################
# 4. Visual Regression Tests
##############################################

echo -e "${YELLOW}[4/4] Running Visual Regression Tests...${NC}"
echo "=========================================="
echo ""

cd frontend

echo "Running Visual Regression Tests..."
if npx playwright test e2e/visual/; then
    echo -e "${GREEN}✓ Visual regression tests passed${NC}"
else
    echo -e "${RED}✗ Visual regression tests failed${NC}"
fi

cd ..

##############################################
# Test Summary
##############################################

echo ""
echo "=========================================="
echo -e "${YELLOW}Test Execution Complete${NC}"
echo "=========================================="
echo ""

echo "Test Results Summary:"
echo "--------------------"
echo "Unit Tests:       ${UNIT_TESTS_PASSED}/2 suites passed"
echo "E2E Tests:        ${E2E_TESTS_PASSED}/1 suite passed"

if [ $LOAD_TESTS_PASSED -eq -1 ]; then
    echo "Load Tests:       Skipped (k6 not installed)"
else
    echo "Load Tests:       ${LOAD_TESTS_PASSED}/2 tests passed"
fi

echo ""

# Calculate overall pass rate
TOTAL_TESTS=3
TOTAL_PASSED=$((UNIT_TESTS_PASSED + E2E_TESTS_PASSED))

if [ $LOAD_TESTS_PASSED -ge 0 ]; then
    TOTAL_TESTS=$((TOTAL_TESTS + 2))
    TOTAL_PASSED=$((TOTAL_PASSED + LOAD_TESTS_PASSED))
fi

PASS_RATE=$((TOTAL_PASSED * 100 / TOTAL_TESTS))

echo "Overall: ${TOTAL_PASSED}/${TOTAL_TESTS} test suites passed (${PASS_RATE}%)"
echo ""

# Report locations
echo "Test Reports Available:"
echo "----------------------"
echo "Frontend Coverage:  frontend/coverage/index.html"
echo "Backend Coverage:   backend/coverage/index.html"
echo "E2E Report:         frontend/playwright-report/index.html"

if [ $LOAD_TESTS_PASSED -ge 0 ]; then
    echo "Load Test Results:  load-test-summary.json"
fi

echo ""

# Exit code based on results
if [ $TOTAL_PASSED -eq $TOTAL_TESTS ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please review the output above.${NC}"
    exit 1
fi
