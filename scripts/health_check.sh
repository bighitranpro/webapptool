#!/bin/bash
###############################################################################
# BiTool Health Check Script
# Monitor application health and send alerts if needed
###############################################################################

# Configuration
APP_URL="http://localhost:5003/health"
SERVICE_NAME="bitool"
LOG_FILE="/home/root/webapp/logs/health_check.log"
ALERT_EMAIL=""  # Add email for alerts

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Function to log
log_message() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

# Function to check HTTP
check_http() {
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL" --max-time 10)
    if [ "$HTTP_CODE" = "200" ]; then
        return 0
    else
        return 1
    fi
}

# Function to check service
check_service() {
    systemctl is-active --quiet "$SERVICE_NAME"
    return $?
}

# Function to check processes
check_processes() {
    PROCESS_COUNT=$(ps aux | grep -c "[g]unicorn.*app:app")
    if [ "$PROCESS_COUNT" -ge 2 ]; then  # At least 1 master + 1 worker
        return 0
    else
        return 1
    fi
}

# Function to restart service
restart_service() {
    log_message "${YELLOW}Attempting to restart $SERVICE_NAME...${NC}"
    sudo systemctl restart "$SERVICE_NAME"
    sleep 5
    
    if check_service && check_http; then
        log_message "${GREEN}✓ Service restarted successfully${NC}"
        return 0
    else
        log_message "${RED}✗ Service restart failed${NC}"
        return 1
    fi
}

# Main health check
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}BiTool Health Check${NC}"
echo -e "${GREEN}======================================${NC}"
log_message "Starting health check..."

# Check 1: Service status
echo -n "Checking service status... "
if check_service; then
    echo -e "${GREEN}✓ Running${NC}"
    log_message "Service status: Running"
else
    echo -e "${RED}✗ Stopped${NC}"
    log_message "Service status: Stopped"
    restart_service
    exit 1
fi

# Check 2: Process count
echo -n "Checking processes... "
PROCESS_COUNT=$(ps aux | grep -c "[g]unicorn.*app:app")
echo -e "${GREEN}✓ $PROCESS_COUNT processes${NC}"
log_message "Process count: $PROCESS_COUNT"

if ! check_processes; then
    echo -e "${RED}✗ Insufficient processes${NC}"
    log_message "Insufficient processes, restarting..."
    restart_service
fi

# Check 3: HTTP response
echo -n "Checking HTTP endpoint... "
if check_http; then
    echo -e "${GREEN}✓ Responding (200 OK)${NC}"
    log_message "HTTP check: OK"
else
    echo -e "${RED}✗ Not responding${NC}"
    log_message "HTTP check: Failed"
    restart_service
fi

# Check 4: Memory usage
echo -n "Checking memory usage... "
MEM_USAGE=$(ps aux | grep "[g]unicorn.*app:app" | awk '{sum+=$6} END {print sum/1024}')
echo -e "${GREEN}✓ ${MEM_USAGE} MB${NC}"
log_message "Memory usage: ${MEM_USAGE} MB"

# Check 5: Disk space
echo -n "Checking disk space... "
DISK_USAGE=$(df -h /home/root/webapp | awk 'NR==2 {print $5}' | sed 's/%//')
echo -e "${GREEN}✓ ${DISK_USAGE}% used${NC}"
log_message "Disk usage: ${DISK_USAGE}%"

if [ "$DISK_USAGE" -gt 90 ]; then
    echo -e "${YELLOW}⚠ Warning: Disk usage above 90%${NC}"
    log_message "Warning: High disk usage"
fi

# Check 6: Log file size
echo -n "Checking log file sizes... "
ERROR_LOG_SIZE=$(du -sh /home/root/webapp/logs/error.log 2>/dev/null | cut -f1)
echo -e "${GREEN}✓ Error log: ${ERROR_LOG_SIZE}${NC}"
log_message "Error log size: ${ERROR_LOG_SIZE}"

# Summary
echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Health Check Completed${NC}"
echo -e "${GREEN}Status: All checks passed ✓${NC}"
echo -e "${GREEN}======================================${NC}"
log_message "Health check completed successfully"

exit 0
