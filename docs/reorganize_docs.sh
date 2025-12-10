#!/bin/bash

# BARQ Fleet Management - Documentation Reorganization Script
# Created: December 10, 2025
# Purpose: Clean up phase folders and archive historical documentation

set -e  # Exit on error

PROJECT_ROOT="/Users/ramiz_new/Desktop/Projects/barq-fleet-clean"
DOCS_DIR="$PROJECT_ROOT/docs"
ARCHIVE_DIR="$DOCS_DIR/archive/project-phases"

echo "========================================="
echo "BARQ Documentation Reorganization"
echo "========================================="
echo ""

# 1. Create archive structure
echo "Step 1: Creating archive directory structure..."
mkdir -p "$ARCHIVE_DIR"/{phase1,phase2,phase3,phase4,phase5,phase6,phase7}
echo "✓ Archive directories created"
echo ""

# 2. Copy still-relevant documents to appropriate folders
echo "Step 2: Moving still-relevant documents to active folders..."

# Security checklist to deployment
if [ -f "$DOCS_DIR/phase1/security_checklist.md" ]; then
    cp "$DOCS_DIR/phase1/security_checklist.md" "$DOCS_DIR/deployment/security_checklist.md"
    echo "✓ Copied security_checklist.md to docs/deployment/"
fi

# Personas to UX
if [ -f "$DOCS_DIR/phase2/personas.md" ]; then
    cp "$DOCS_DIR/phase2/personas.md" "$DOCS_DIR/ux/personas.md"
    echo "✓ Copied personas.md to docs/ux/"
fi

# Accessibility report to UX
if [ -f "$DOCS_DIR/phase3/accessibility_report.md" ]; then
    cp "$DOCS_DIR/phase3/accessibility_report.md" "$DOCS_DIR/ux/accessibility_report.md"
    echo "✓ Copied accessibility_report.md to docs/ux/"
fi

# Responsive checklist to UX
if [ -f "$DOCS_DIR/phase3/responsive_checklist.md" ]; then
    cp "$DOCS_DIR/phase3/responsive_checklist.md" "$DOCS_DIR/ux/responsive_checklist.md"
    echo "✓ Copied responsive_checklist.md to docs/ux/"
fi

echo ""

# 3. Move all phase documents to archive
echo "Step 3: Moving phase documents to archive..."

# Phase 1
if [ -d "$DOCS_DIR/phase1" ]; then
    mv "$DOCS_DIR/phase1"/* "$ARCHIVE_DIR/phase1/" 2>/dev/null || true
    echo "✓ Archived Phase 1 documents"
fi

# Phase 2
if [ -d "$DOCS_DIR/phase2" ]; then
    mv "$DOCS_DIR/phase2"/* "$ARCHIVE_DIR/phase2/" 2>/dev/null || true
    echo "✓ Archived Phase 2 documents"
fi

# Phase 3
if [ -d "$DOCS_DIR/phase3" ]; then
    mv "$DOCS_DIR/phase3"/* "$ARCHIVE_DIR/phase3/" 2>/dev/null || true
    echo "✓ Archived Phase 3 documents"
fi

# Phase 4
if [ -d "$DOCS_DIR/phase4" ]; then
    mv "$DOCS_DIR/phase4"/* "$ARCHIVE_DIR/phase4/" 2>/dev/null || true
    echo "✓ Archived Phase 4 documents"
fi

# Phase 5
if [ -d "$DOCS_DIR/phase5" ]; then
    mv "$DOCS_DIR/phase5"/* "$ARCHIVE_DIR/phase5/" 2>/dev/null || true
    echo "✓ Archived Phase 5 documents"
fi

# Phase 6
if [ -d "$DOCS_DIR/phase6" ]; then
    mv "$DOCS_DIR/phase6"/* "$ARCHIVE_DIR/phase6/" 2>/dev/null || true
    echo "✓ Archived Phase 6 documents"
fi

# Phase 7
if [ -d "$DOCS_DIR/phase7" ]; then
    mv "$DOCS_DIR/phase7"/* "$ARCHIVE_DIR/phase7/" 2>/dev/null || true
    echo "✓ Archived Phase 7 documents"
fi

echo ""

# 4. Remove empty phase folders
echo "Step 4: Removing empty phase directories..."
for i in {1..7}; do
    if [ -d "$DOCS_DIR/phase$i" ]; then
        rmdir "$DOCS_DIR/phase$i" 2>/dev/null && echo "✓ Removed phase$i/" || echo "⚠ Could not remove phase$i/ (may not be empty)"
    fi
done

echo ""

# 5. Summary
echo "========================================="
echo "Reorganization Complete!"
echo "========================================="
echo ""
echo "Summary:"
echo "  • Archive created: docs/archive/project-phases/"
echo "  • Still-relevant docs moved to active folders:"
echo "    - security_checklist.md → docs/deployment/"
echo "    - personas.md → docs/ux/"
echo "    - accessibility_report.md → docs/ux/"
echo "    - responsive_checklist.md → docs/ux/"
echo "  • Historical docs archived in docs/archive/project-phases/"
echo "  • Phase directories cleaned up"
echo ""
echo "Next steps:"
echo "  1. Review the archive README: docs/archive/README.md"
echo "  2. Verify moved documents in their new locations"
echo "  3. Update any links in other documentation"
echo "  4. Commit changes to git"
echo ""
echo "To verify the new structure:"
echo "  ls -la $DOCS_DIR"
echo "  ls -la $ARCHIVE_DIR"
echo ""
