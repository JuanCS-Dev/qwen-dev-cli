#!/bin/bash
# Directory Structure Audit
# Validates enterprise-grade organization

set -euo pipefail

echo "🔍 Directory Structure Audit"
echo "============================"
echo ""

ERRORS=0

# Check root is clean
echo "📁 Checking root directory..."
ROOT_MD_COUNT=$(find . -maxdepth 1 -type f -name "*.md" | grep -v -E "(README|CHANGELOG|GEMINI|RELEASE_NOTES|TEST_RESULTS)" | wc -l)
if [[ $ROOT_MD_COUNT -gt 0 ]]; then
    echo "❌ Found $ROOT_MD_COUNT unauthorized .md files in root"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ Root directory is clean"
fi

# Check test files not in root
echo ""
echo "🧪 Checking for misplaced test files..."
ROOT_TEST_COUNT=$(find . -maxdepth 1 -type f -name "test_*.py" | wc -l)
if [[ $ROOT_TEST_COUNT -gt 0 ]]; then
    echo "❌ Found $ROOT_TEST_COUNT test files in root"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ No test files in root"
fi

# Check backup files
echo ""
echo "💾 Checking for backup files..."
BACKUP_COUNT=$(find . -maxdepth 1 -name "*.backup*" -o -name "*.bak" | wc -l)
if [[ $BACKUP_COUNT -gt 0 ]]; then
    echo "❌ Found $BACKUP_COUNT backup files outside archive"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ No backup files outside archive"
fi

# Check essential directories exist
echo ""
echo "🏗️  Checking essential directories..."
REQUIRED_DIRS=("docs" "scripts" "tests" "config" ".archive" "gradio_ui" "qwen_dev_cli")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [[ -d "$dir" ]]; then
        echo "✅ $dir/ exists"
    else
        echo "❌ Missing directory: $dir/"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check docs organization
echo ""
echo "📚 Checking docs structure..."
DOCS_SUBDIRS=("reports" "guides" "architecture" "rfcs")
for dir in "${DOCS_SUBDIRS[@]}"; do
    if [[ -d "docs/$dir" ]]; then
        echo "✅ docs/$dir/ exists"
    else
        echo "❌ Missing: docs/$dir/"
        ERRORS=$((ERRORS + 1))
    fi
done

# Archive size check
echo ""
echo "🗄️  Checking archive size..."
ARCHIVE_SIZE=$(du -sm .archive 2>/dev/null | cut -f1)
if [[ $ARCHIVE_SIZE -gt 100 ]]; then
    echo "⚠️  Archive is ${ARCHIVE_SIZE}MB (threshold: 100MB) - consider cleanup"
else
    echo "✅ Archive size: ${ARCHIVE_SIZE}MB"
fi

# Summary
echo ""
echo "=========================="
if [[ $ERRORS -eq 0 ]]; then
    echo "✅ All checks passed! Directory structure is enterprise-grade."
    exit 0
else
    echo "❌ Found $ERRORS issue(s). Please fix before release."
    exit 1
fi
