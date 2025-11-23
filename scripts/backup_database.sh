#!/bin/bash
###############################################################################
# BiTool Database Backup Script
# Automatically backup database with rotation
###############################################################################

# Configuration
BACKUP_DIR="/home/root/webapp/backups"
DB_PATH="/home/root/webapp/email_tool.db"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="bitool_db_${TIMESTAMP}.db"
KEEP_DAYS=7

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create backup directory if not exists
mkdir -p "$BACKUP_DIR"

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}BiTool Database Backup${NC}"
echo -e "${GREEN}======================================${NC}"
echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Database: $DB_PATH"
echo "Backup Dir: $BACKUP_DIR"
echo ""

# Check if database exists
if [ ! -f "$DB_PATH" ]; then
    echo -e "${RED}Error: Database file not found!${NC}"
    exit 1
fi

# Get database size
DB_SIZE=$(du -h "$DB_PATH" | cut -f1)
echo "Database Size: $DB_SIZE"

# Create backup
echo -e "${YELLOW}Creating backup...${NC}"
cp "$DB_PATH" "$BACKUP_DIR/$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backup created successfully!${NC}"
    echo "Backup file: $BACKUP_FILE"
    
    # Compress backup
    echo -e "${YELLOW}Compressing backup...${NC}"
    gzip "$BACKUP_DIR/$BACKUP_FILE"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Backup compressed successfully!${NC}"
        BACKUP_FILE="${BACKUP_FILE}.gz"
        COMPRESSED_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
        echo "Compressed size: $COMPRESSED_SIZE"
    fi
else
    echo -e "${RED}✗ Backup failed!${NC}"
    exit 1
fi

# Clean old backups
echo ""
echo -e "${YELLOW}Cleaning old backups (older than $KEEP_DAYS days)...${NC}"
find "$BACKUP_DIR" -name "bitool_db_*.gz" -type f -mtime +$KEEP_DAYS -delete

# Count remaining backups
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/bitool_db_*.gz 2>/dev/null | wc -l)
echo "Remaining backups: $BACKUP_COUNT"

# List recent backups
echo ""
echo "Recent backups:"
ls -lh "$BACKUP_DIR"/bitool_db_*.gz 2>/dev/null | tail -5

echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Backup completed successfully!${NC}"
echo -e "${GREEN}======================================${NC}"

exit 0
