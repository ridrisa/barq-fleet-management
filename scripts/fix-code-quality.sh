#!/bin/bash
# Auto-fix code quality issues

set -e

echo "======================================"
echo "🔧 Auto-fixing Code Quality Issues"
echo "======================================"
echo ""

# Backend fixes
echo "📦 Backend Auto-fixes"
echo "===================="

cd backend

echo "Running Black formatter..."
black app/

echo "Running isort..."
isort app/

echo "✓ Backend formatting complete"

cd ..

# Frontend fixes
echo ""
echo "🎨 Frontend Auto-fixes"
echo "===================="

cd frontend

echo "Running ESLint with --fix..."
npm run lint -- --fix || echo "Some issues may need manual fixing"

echo "✓ Frontend formatting complete"

cd ..

echo ""
echo "======================================"
echo "✅ Auto-fixes complete!"
echo ""
echo "Run ./scripts/run-ci-checks.sh to verify"
echo "======================================"
