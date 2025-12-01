#!/bin/bash
# CI/CD Setup Verification Script
# Verifies that all CI/CD components are properly configured

set -e

echo "======================================"
echo "🔍 CI/CD Setup Verification"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARN=0

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}✗${NC} $2 - Missing: $1"
        ((CHECKS_FAILED++))
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}✗${NC} $2 - Missing: $1"
        ((CHECKS_FAILED++))
    fi
}

check_executable() {
    if [ -x "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((CHECKS_PASSED++))
    else
        echo -e "${YELLOW}⚠${NC} $2 - Not executable: $1"
        ((CHECKS_WARN++))
    fi
}

echo -e "${BLUE}📁 Directory Structure${NC}"
echo "===================="
check_dir ".github/workflows" "GitHub workflows directory"
check_dir "scripts" "Scripts directory"
check_dir "docs" "Documentation directory"
check_dir "frontend" "Frontend directory"
check_dir "backend" "Backend directory"
echo ""

echo -e "${BLUE}🔧 GitHub Actions Workflows${NC}"
echo "==========================="
check_file ".github/workflows/ci.yml" "Main CI pipeline"
check_file ".github/workflows/pr-checks.yml" "PR validation workflow"
check_file ".github/workflows/deploy-production.yml" "Production deployment"
check_file ".github/labeler.yml" "Auto-labeler configuration"
echo ""

echo -e "${BLUE}☁️  Cloud Build Configuration${NC}"
echo "============================="
check_file "cloudbuild.yaml" "Cloud Build config"
echo ""

echo -e "${BLUE}🐳 Docker Configurations${NC}"
echo "========================"
check_file "backend/Dockerfile" "Backend Dockerfile"
check_file "frontend/Dockerfile.prod" "Frontend production Dockerfile"
check_file "frontend/nginx.conf" "Nginx configuration"
check_file "docker-compose.yml" "Docker Compose"
echo ""

echo -e "${BLUE}📜 Scripts${NC}"
echo "=========="
check_file "scripts/run-ci-checks.sh" "CI checks script"
check_executable "scripts/run-ci-checks.sh" "CI checks executable"
check_file "scripts/fix-code-quality.sh" "Code quality fixer"
check_executable "scripts/fix-code-quality.sh" "Fixer executable"
check_file "scripts/verify-ci-setup.sh" "Verification script"
echo ""

echo -e "${BLUE}📚 Documentation${NC}"
echo "================"
check_file "docs/CI_CD_GUIDE.md" "Comprehensive CI/CD guide"
check_file "docs/CI_CD_QUICK_REFERENCE.md" "Quick reference guide"
check_file "CI_CD_IMPLEMENTATION_REPORT.md" "Implementation report"
check_file "README.md" "Project README"
echo ""

echo -e "${BLUE}⚙️  Backend Configurations${NC}"
echo "=========================="
check_file "backend/pytest.ini" "Pytest configuration"
check_file "backend/pyproject.toml" "Python tools config"
check_file "backend/requirements.txt" "Python dependencies"
check_file "backend/requirements-dev.txt" "Python dev dependencies"
echo ""

echo -e "${BLUE}⚙️  Frontend Configurations${NC}"
echo "==========================="
check_file "frontend/package.json" "Package.json"
check_file "frontend/tsconfig.json" "TypeScript config"
check_file "frontend/vite.config.ts" "Vite config"
echo ""

echo -e "${BLUE}🔍 Testing Configuration${NC}"
echo "========================"

# Check if pytest.ini has correct settings
if [ -f "backend/pytest.ini" ]; then
    if grep -q "testpaths = app/tests" backend/pytest.ini; then
        echo -e "${GREEN}✓${NC} Pytest test paths configured"
        ((CHECKS_PASSED++))
    else
        echo -e "${YELLOW}⚠${NC} Pytest test paths may need review"
        ((CHECKS_WARN++))
    fi
fi

# Check if pyproject.toml has coverage settings
if [ -f "backend/pyproject.toml" ]; then
    if grep -q "pytest.ini_options" backend/pyproject.toml; then
        echo -e "${GREEN}✓${NC} Pytest coverage configured"
        ((CHECKS_PASSED++))
    else
        echo -e "${YELLOW}⚠${NC} Coverage settings may need review"
        ((CHECKS_WARN++))
    fi
fi

# Check if frontend has test scripts
if [ -f "frontend/package.json" ]; then
    if grep -q "\"test\"" frontend/package.json; then
        echo -e "${GREEN}✓${NC} Frontend test scripts configured"
        ((CHECKS_PASSED++))
    else
        echo -e "${YELLOW}⚠${NC} Frontend test scripts may need review"
        ((CHECKS_WARN++))
    fi
fi

echo ""

echo -e "${BLUE}🔐 Security Configuration${NC}"
echo "========================="

# Check if workflows include security scanning
if [ -f ".github/workflows/ci.yml" ]; then
    if grep -q "trivy" .github/workflows/ci.yml; then
        echo -e "${GREEN}✓${NC} Security scanning configured (Trivy)"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}✗${NC} Security scanning not found"
        ((CHECKS_FAILED++))
    fi
fi

# Check Cloud Build for security scan
if [ -f "cloudbuild.yaml" ]; then
    if grep -q "trivy" cloudbuild.yaml; then
        echo -e "${GREEN}✓${NC} Cloud Build security scanning configured"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}✗${NC} Cloud Build security scanning not found"
        ((CHECKS_FAILED++))
    fi
fi

echo ""

echo -e "${BLUE}📊 Quality Gates${NC}"
echo "================"

# Check for linting tools
if [ -f "backend/requirements-dev.txt" ]; then
    if grep -q "black" backend/requirements-dev.txt; then
        echo -e "${GREEN}✓${NC} Black formatter configured"
        ((CHECKS_PASSED++))
    fi
    if grep -q "flake8" backend/requirements-dev.txt; then
        echo -e "${GREEN}✓${NC} Flake8 linter configured"
        ((CHECKS_PASSED++))
    fi
    if grep -q "mypy" backend/requirements-dev.txt; then
        echo -e "${GREEN}✓${NC} MyPy type checker configured"
        ((CHECKS_PASSED++))
    fi
fi

# Check frontend linting
if [ -f "frontend/package.json" ]; then
    if grep -q "eslint" frontend/package.json; then
        echo -e "${GREEN}✓${NC} ESLint configured"
        ((CHECKS_PASSED++))
    fi
    if grep -q "typescript" frontend/package.json; then
        echo -e "${GREEN}✓${NC} TypeScript configured"
        ((CHECKS_PASSED++))
    fi
fi

echo ""

echo "======================================"
echo -e "${BLUE}📈 Summary${NC}"
echo "======================================"
echo -e "${GREEN}Passed:${NC}  $CHECKS_PASSED"
echo -e "${YELLOW}Warnings:${NC} $CHECKS_WARN"
echo -e "${RED}Failed:${NC}  $CHECKS_FAILED"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ CI/CD setup is complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Configure GitHub secrets (GCP_PROJECT_ID, GCP_SA_KEY)"
    echo "2. Set up GCP project and enable required APIs"
    echo "3. Create Cloud Build trigger"
    echo "4. Configure branch protection rules"
    echo "5. Push code and test the pipeline!"
    echo ""
    echo "📚 Read docs/CI_CD_GUIDE.md for detailed instructions"
    exit 0
else
    echo -e "${RED}❌ Some checks failed!${NC}"
    echo "Please review the missing components above"
    exit 1
fi
