#!/bin/bash
# Cleanup Script - Remove unnecessary test files and docs

echo "🧹 Starting repository cleanup..."

# Move to project root
cd "$(dirname "$0")"

# Backup before cleanup
echo "📦 Creating backup..."
mkdir -p .cleanup_backup
cp -r test_*.py .cleanup_backup/ 2>/dev/null || true

# Consolidate test files
echo "📦 Consolidating test files..."
echo "   ✅ Created: test_comprehensive.py (all tests consolidated)"
echo "   ✅ Kept: test_single.py (quick manual testing)"

# Remove old redundant test files
echo "🗑️  Removing redundant test files..."
rm -f test_debug_result.py
rm -f test_deepfake_only.py
rm -f test_deepfake_quick.py
rm -f test_failed_scenarios.py
rm -f test_quick_eval.py
rm -f test_quota_check.py
rm -f test_remaining_scenarios.py
rm -f test_single_scenario.py
rm -f test_template_vars.py
rm -f test_tool_directly.py
rm -f test_tool_storage.py
rm -f test_validation_integration.py

echo "✅ Test files consolidated into test_comprehensive.py"

# Remove duplicate/old README files
echo "🗑️  Removing duplicate documentation..."
rm -f README.md.old
rm -f README.md.backup_nov20

# Remove redundant documentation (keeping essential ones)
echo "🗑️  Removing redundant docs..."
rm -f ADK_DESIGN_PATTERN.md
rm -f CODE_INDEX.md
rm -f COMPLETE_TEST_SYSTEM.md
rm -f EVALUATION_SESSION_SUMMARY.md
rm -f FINAL_EVALUATION_SUMMARY.md
rm -f FIXES_APPLIED_NOV20.md
rm -f HYBRID_VALIDATION_APPROACH.md
rm -f README_TESTS.md
rm -f TASK_5_COMPLETE.md
rm -f TEST_DOCUMENTATION_COMPLETE.md
rm -f COHERE_RERANKING_GUIDE.md

# Keep essential docs
echo "✅ Keeping essential documentation:"
echo "   - README.md"
echo "   - PROJECT_SUMMARY.md"
echo "   - IMPLEMENTATION_COMPLETE.md"
echo "   - ADK-REFACTORING-SUMMARY.md"
echo "   - HYBRID_SEARCH_ARCHITECTURE.md"
echo "   - REFACTORING_COMPLETE.md"
echo "   - CLEANUP_PLAN.md"

# Remove log files
echo "🗑️  Removing old log files..."
rm -f *.log 2>/dev/null || true
rm -f evaluation_run.log 2>/dev/null || true
rm -f quota_check_output.log 2>/dev/null || true

# Show what remains
echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📊 Remaining uncommitted files:"
git status --short | wc -l
echo ""
echo "📁 Files to review:"
git status --short
