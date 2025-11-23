#!/bin/bash
###############################################################################
# Setup Cron Jobs for BiTool
###############################################################################

echo "Setting up cron jobs for BiTool..."

# Backup cron job - Daily at 2 AM
BACKUP_CRON="0 2 * * * /home/root/webapp/scripts/backup_database.sh >> /home/root/webapp/logs/backup.log 2>&1"

# Check if cron job already exists
crontab -l 2>/dev/null | grep -q "backup_database.sh"
if [ $? -eq 0 ]; then
    echo "Backup cron job already exists"
else
    # Add cron job
    (crontab -l 2>/dev/null; echo "$BACKUP_CRON") | crontab -
    echo "✓ Backup cron job added (Daily at 2 AM)"
fi

# List current cron jobs
echo ""
echo "Current cron jobs:"
crontab -l

echo ""
echo "✓ Cron jobs setup completed!"
