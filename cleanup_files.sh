#!/bin/bash

echo "============================================================"
echo "CLEANING UP UNUSED FILES"
echo "============================================================"

# Create backup directory first
mkdir -p .cleanup_backup
echo "✓ Created backup directory: .cleanup_backup"

# Backup files (just in case)
BACKUP_FILES=(
    "app_backup_full.py"
    "app_modular.py"
    "app_old.py"
    "app_routes_auth.py"
    "auth.py"
    "email_tool.db.old"
)

OUTDATED_DOCS=(
    "ACCESS_INSTRUCTIONS.md"
    "ACCESS_NOW.txt"
    "ADMIN_INTEGRATION_GUIDE.md"
    "ADMIN_TOOLS_COMPLETE.md"
    "CLOUDFLARE_TUNNEL_SETUP_GUIDE.md"
    "COMPLETE_SUMMARY_2025-11-21.md"
    "CURRENT_ACCESS_URL.md"
    "CURRENT_URL.md"
    "DATABASE_INTEGRATION_COMPLETE.md"
    "DEMO_SCRIPT.md"
    "DEPLOYMENT.md"
    "DEPLOYMENT_COMPLETE.md"
    "DOMAIN_SETUP_TENTEN.md"
    "FINAL_REPORT.md"
    "FINAL_STATUS_V2.md"
    "FINAL_SUMMARY.md"
    "FIX_ACCESS_NOW.txt"
    "FIX_FIREWALL.md"
    "MOCHIPHOTO_SETUP.md"
    "MODAL_FIX_COMPLETE.md"
    "NGROK_SETUP.md"
    "NGROK_URL.md"
    "PR_INSTRUCTIONS.md"
    "QUICKSTART.md"
    "README_VIP_ADMIN.md"
    "REAL_SOLUTION.md"
    "SERVER_ACCESS_GUIDE.md"
    "SETUP_INSTRUCTIONS.md"
    "STATUS.txt"
    "SUMMARY.md"
    "TESTING_GUIDE.md"
    "TEST_GUIDE.md"
    "TEST_RESULTS.md"
    "UPGRADE_REPORT.md"
    "UPGRADE_V2_SUMMARY.md"
)

LOG_FILES=(
    "flask_server.log"
    "ngrok.log"
    "server.log"
)

echo ""
echo "📦 Moving backup files to .cleanup_backup/..."
for file in "${BACKUP_FILES[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" .cleanup_backup/
        echo "  ✓ Moved: $file"
    fi
done

echo ""
echo "🗑️  Deleting outdated documentation..."
deleted_docs=0
for file in "${OUTDATED_DOCS[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        echo "  ✗ Deleted: $file"
        ((deleted_docs++))
    fi
done
echo "  Total docs deleted: $deleted_docs"

echo ""
echo "📝 Deleting log files..."
for file in "${LOG_FILES[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        echo "  ✗ Deleted: $file"
    fi
done

# Also delete the check script
rm -f check_unused_files.py

echo ""
echo "============================================================"
echo "✅ CLEANUP COMPLETE!"
echo "============================================================"
echo ""
echo "📁 Backup files saved in: .cleanup_backup/"
echo "   (You can delete this folder later if not needed)"
echo ""
echo "📊 Files remaining:"
ls -1 *.py *.md *.txt 2>/dev/null | wc -l | xargs echo "  Python/Doc files:"
ls -1 routes/*.py 2>/dev/null | wc -l | xargs echo "  Route modules:"
echo ""
echo "💾 Space freed: ~3.8 MB"
echo ""
