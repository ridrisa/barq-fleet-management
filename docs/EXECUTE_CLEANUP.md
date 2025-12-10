# Quick Execution Guide - Documentation Cleanup

**Last Updated:** December 10, 2025

---

## TL;DR

Run this to clean up phase documentation:

```bash
cd /Users/ramiz_new/Desktop/Projects/barq-fleet-clean/docs
chmod +x reorganize_docs.sh
./reorganize_docs.sh
```

Then commit the changes:

```bash
git add .
git commit -m "docs: reorganize phase documentation into archive"
git push
```

**Done!** ✅

---

## What This Does

1. Creates `docs/archive/project-phases/` folder structure
2. Copies 4 still-relevant documents to active folders
3. Moves 15 historical documents to archive
4. Removes 7 empty phase folders
5. Preserves all project history

---

## Before You Run

**Check current structure:**
```bash
ls -la /Users/ramiz_new/Desktop/Projects/barq-fleet-clean/docs/ | grep phase
```

You should see:
```
phase1/
phase2/
phase3/
phase4/
phase5/
phase6/
phase7/
```

---

## Execute Cleanup

**Step 1: Navigate to docs**
```bash
cd /Users/ramiz_new/Desktop/Projects/barq-fleet-clean/docs
```

**Step 2: Make script executable**
```bash
chmod +x reorganize_docs.sh
```

**Step 3: Run the script**
```bash
./reorganize_docs.sh
```

**Expected output:**
```
=========================================
BARQ Documentation Reorganization
=========================================

Step 1: Creating archive directory structure...
✓ Archive directories created

Step 2: Moving still-relevant documents to active folders...
✓ Copied security_checklist.md to docs/deployment/
✓ Copied personas.md to docs/ux/
✓ Copied accessibility_report.md to docs/ux/
✓ Copied responsive_checklist.md to docs/ux/

Step 3: Moving phase documents to archive...
✓ Archived Phase 1 documents
✓ Archived Phase 2 documents
✓ Archived Phase 3 documents
✓ Archived Phase 4 documents
✓ Archived Phase 5 documents
✓ Archived Phase 6 documents
✓ Archived Phase 7 documents

Step 4: Removing empty phase directories...
✓ Removed phase1/
✓ Removed phase2/
✓ Removed phase3/
✓ Removed phase4/
✓ Removed phase5/
✓ Removed phase6/
✓ Removed phase7/

=========================================
Reorganization Complete!
=========================================
```

---

## Verify Success

**Check archive created:**
```bash
ls -la archive/project-phases/
```

**Check moved documents:**
```bash
ls deployment/security_checklist.md
ls ux/personas.md
ls ux/accessibility_report.md
ls ux/responsive_checklist.md
```

**Confirm phase folders gone:**
```bash
ls -la | grep phase
# Should return nothing (no phase folders)
```

**All green?** ✅ Proceed to commit!

---

## Commit Changes

**Step 1: Review changes**
```bash
git status
```

**Step 2: Add all changes**
```bash
git add .
```

**Step 3: Commit with descriptive message**
```bash
git commit -m "docs: reorganize phase documentation into archive

- Created docs/archive/project-phases/ for historical documents
- Moved still-relevant docs to appropriate folders:
  - security_checklist.md → deployment/
  - personas.md → ux/
  - accessibility_report.md → ux/
  - responsive_checklist.md → ux/
- Added comprehensive archive README with context
- Updated main docs README with UX and archive sections
- Removed empty phase folders (phase1-phase7)

Preserves project history while improving documentation organization."
```

**Step 4: Push to remote**
```bash
git push origin main
```

---

## If Something Goes Wrong

**Undo the cleanup (before commit):**
```bash
git reset --hard HEAD
git clean -fd
```

**Or manually rollback (after commit):**
```bash
# Restore phase folders from archive
for i in {1..7}; do
    mkdir -p phase$i
    cp -r archive/project-phases/phase$i/* phase$i/
done

# Remove copied files
rm deployment/security_checklist.md
rm ux/personas.md
rm ux/accessibility_report.md
rm ux/responsive_checklist.md

# Remove archive
rm -rf archive

# Revert README
git checkout HEAD~1 README.md
```

---

## After Cleanup

**Optional: Clean up this execution guide**
```bash
# Remove temporary execution files
rm EXECUTE_CLEANUP.md
rm CLEANUP_SUMMARY.md
rm reorganize_docs.sh

git add .
git commit -m "docs: remove temporary cleanup files"
git push
```

---

## Need Help?

**Read full context:**
- `CLEANUP_SUMMARY.md` - Complete details
- `archive/README.md` - Archive documentation

**Contact:**
- Create GitHub issue
- Email: dev@barq.com

---

**Ready?** Go ahead and run the script! 🚀
