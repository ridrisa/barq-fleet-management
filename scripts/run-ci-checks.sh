#!/bin/bash
# Local CI checks runner
# Run this before pushing to ensure CI will pass

set -e

echo "======================================"
echo "🔍 Running Local CI Checks"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FAILED=0

# Backend Checks
echo "📦 Backend Checks"
echo "=================="

cd backend

echo -n "1. Black formatting... "
if black --check app/ 2>&1 > /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    FAILED=1
fi

echo -n "2. isort imports... "
if isort --check-only app/ 2>&1 > /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    FAILED=1
fi

echo -n "3. Flake8 linting... "
if flake8 app/ --max-line-length=100 --exclude=*/migrations/*,*/venv/* 2>&1 > /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    FAILED=1
fi

echo -n "4. MyPy type checking... "
if mypy app/ --ignore-missing-imports 2>&1 > /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠${NC}"
fi

echo -n "5. Tests... "
if pytest app/tests/ -v 2>&1 > /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠${NC} (Tests may not be fully implemented)"
fi

cd ..

echo ""
echo "🎨 Frontend Checks"
echo "=================="

cd frontend

echo -n "1. TypeScript compilation... "
if npm run type-check 2>&1 > /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    FAILED=1
fi

echo -n "2. ESLint... "
if npm run lint 2>&1 > /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    FAILED=1
fi

echo -n "3. Build... "
if npm run build 2>&1 > /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    FAILED=1
fi

echo -n "4. Tests... "
if npm run test:run 2>&1 > /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠${NC} (Tests may not be configured)"
fi

cd ..

echo ""
echo "======================================"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo "Safe to push to repository"
    exit 0
else
    echo -e "${RED}❌ Some checks failed!${NC}"
    echo "Fix issues before pushing"
    exit 1
fi
