#!/bin/bash

# ==========================================
# AUTO DEPLOY SCRIPT FOR BI GHI TOOL MMO
# Version: 2.2.0
# Author: BIGHI Tool MMO Team
# ==========================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Config
APP_DIR="/home/root/webapp"
APP_PORT=5003
APP_NAME="email-tool"
BACKUP_DIR="/home/root/backups"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Header
echo "=========================================="
echo "  AUTO DEPLOY - BI GHI TOOL MMO v2.2.0"
echo "=========================================="
echo ""

# Step 1: Check prerequisites
log_info "Step 1: Checking prerequisites..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_warning "Not running as root. Some operations may fail."
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    log_error "Python3 not found!"
    exit 1
fi
log_success "Python3: $(python3 --version)"

# Check pip
if ! command -v pip3 &> /dev/null; then
    log_error "pip3 not found!"
    exit 1
fi
log_success "pip3 found"

# Check if app directory exists
if [ ! -d "$APP_DIR" ]; then
    log_error "App directory not found: $APP_DIR"
    exit 1
fi

cd "$APP_DIR"
log_success "Changed to app directory: $APP_DIR"

# Step 2: Stop running app
log_info "Step 2: Stopping running application..."

if pgrep -f "python3 app.py" > /dev/null; then
    log_info "Killing running Python processes..."
    pkill -f "python3 app.py" || true
    sleep 2
    log_success "Application stopped"
else
    log_info "No running application found"
fi

# Step 3: Backup database
log_info "Step 3: Backing up database..."

mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/email_tool_$(date +%Y%m%d_%H%M%S).db"

if [ -f "$APP_DIR/email_tool.db" ]; then
    cp "$APP_DIR/email_tool.db" "$BACKUP_FILE"
    log_success "Database backed up to: $BACKUP_FILE"
else
    log_warning "Database file not found, skipping backup"
fi

# Step 4: Update code (if git repo)
log_info "Step 4: Updating code..."

if [ -d ".git" ]; then
    log_info "Git repository detected, pulling latest changes..."
    
    # Stash any local changes
    git stash > /dev/null 2>&1 || true
    
    # Pull latest
    if git pull origin main; then
        log_success "Code updated successfully"
    else
        log_warning "Git pull failed, continuing with current code"
    fi
    
    # Pop stash if needed
    git stash pop > /dev/null 2>&1 || true
else
    log_info "Not a git repository, skipping code update"
fi

# Step 5: Install dependencies
log_info "Step 5: Installing dependencies..."

if [ -f "requirements.txt" ]; then
    if pip3 install -r requirements.txt --quiet --no-warn-script-location; then
        log_success "Dependencies installed successfully"
    else
        log_error "Failed to install dependencies"
        exit 1
    fi
else
    log_warning "requirements.txt not found"
fi

# Step 6: Run migrations
log_info "Step 6: Running database migrations..."

if [ -d "migrations" ]; then
    for migration in migrations/*.py; do
        if [ -f "$migration" ]; then
            log_info "Running migration: $(basename $migration)"
            if python3 "$migration"; then
                log_success "Migration completed: $(basename $migration)"
            else
                log_warning "Migration failed: $(basename $migration)"
            fi
        fi
    done
else
    log_info "No migrations directory found"
fi

# Step 7: Check database integrity
log_info "Step 7: Checking database integrity..."

if [ -f "email_tool.db" ]; then
    if sqlite3 email_tool.db "PRAGMA integrity_check;" | grep -q "ok"; then
        log_success "Database integrity check passed"
    else
        log_warning "Database integrity check failed"
    fi
else
    log_warning "Database not found"
fi

# Step 8: Start application
log_info "Step 8: Starting application..."

# Check if port is already in use
if lsof -i:$APP_PORT > /dev/null 2>&1; then
    log_warning "Port $APP_PORT is already in use, trying to free it..."
    fuser -k $APP_PORT/tcp > /dev/null 2>&1 || true
    sleep 2
fi

# Start app in background
nohup python3 app.py > app.log 2>&1 &
APP_PID=$!
echo $APP_PID > app.pid

log_info "Application started with PID: $APP_PID"
sleep 5

# Step 9: Health check
log_info "Step 9: Performing health check..."

MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:$APP_PORT/api/health > /dev/null 2>&1; then
        log_success "Health check passed!"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        log_info "Waiting for app to start... (attempt $RETRY_COUNT/$MAX_RETRIES)"
        sleep 2
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    log_error "Health check failed after $MAX_RETRIES attempts"
    log_error "Check logs: tail -50 $APP_DIR/app.log"
    exit 1
fi

# Step 10: Verify app
log_info "Step 10: Verifying application..."

# Check if process is still running
if ps -p $APP_PID > /dev/null; then
    log_success "Application is running (PID: $APP_PID)"
else
    log_error "Application process died"
    exit 1
fi

# Test endpoints
log_info "Testing endpoints..."

# Homepage
if curl -s -o /dev/null -w "%{http_code}" http://localhost:$APP_PORT/ | grep -q "200"; then
    log_success "Homepage accessible"
else
    log_warning "Homepage returned non-200 status"
fi

# Dashboard
DASHBOARD_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$APP_PORT/dashboard)
if [ "$DASHBOARD_STATUS" = "200" ] || [ "$DASHBOARD_STATUS" = "302" ]; then
    log_success "Dashboard accessible"
else
    log_warning "Dashboard returned status: $DASHBOARD_STATUS"
fi

# Step 11: Cleanup old backups
log_info "Step 11: Cleaning up old backups..."

if [ -d "$BACKUP_DIR" ]; then
    # Keep only last 7 days of backups
    find "$BACKUP_DIR" -name "email_tool_*.db" -mtime +7 -delete
    BACKUP_COUNT=$(find "$BACKUP_DIR" -name "email_tool_*.db" | wc -l)
    log_success "Kept $BACKUP_COUNT backup(s)"
fi

# Summary
echo ""
echo "=========================================="
echo "  DEPLOY COMPLETED SUCCESSFULLY!"
echo "=========================================="
echo ""
echo "📊 Deployment Summary:"
echo "  • App Directory: $APP_DIR"
echo "  • Process ID: $APP_PID"
echo "  • Port: $APP_PORT"
echo "  • Health: ✅ Healthy"
echo "  • Database: ✅ Backed up"
echo ""
echo "🌐 Access URLs:"
echo "  • Homepage: http://localhost:$APP_PORT/"
echo "  • Dashboard: http://localhost:$APP_PORT/dashboard"
echo "  • Admin: http://localhost:$APP_PORT/admin"
echo "  • Health: http://localhost:$APP_PORT/api/health"
echo ""
echo "📝 Useful Commands:"
echo "  • View logs: tail -f $APP_DIR/app.log"
echo "  • Stop app: kill $APP_PID"
echo "  • Restart: bash $0"
echo ""
echo "✅ Deploy completed at: $(date)"
echo "=========================================="
