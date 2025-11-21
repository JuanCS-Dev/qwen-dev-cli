#!/bin/bash
# Archive Cleanup Script
# Removes files older than 90 days from .archive/

set -euo pipefail

ARCHIVE_DIR=".archive"
DAYS_TO_KEEP=90
DRY_RUN=${1:-"--dry-run"}

echo "🗑️  Archive Cleanup Script"
echo "=========================="
echo "Directory: $ARCHIVE_DIR"
echo "Retention: $DAYS_TO_KEEP days"
echo "Mode: $DRY_RUN"
echo ""

if [[ "$DRY_RUN" == "--dry-run" ]]; then
    echo "🔍 DRY RUN - Files that would be deleted:"
    find "$ARCHIVE_DIR" -type f -mtime +$DAYS_TO_KEEP -ls
else
    echo "🔥 DELETING old files..."
    find "$ARCHIVE_DIR" -type f -mtime +$DAYS_TO_KEEP -delete
    echo "✅ Cleanup complete"
fi

echo ""
echo "📊 Current archive size:"
du -sh "$ARCHIVE_DIR"
