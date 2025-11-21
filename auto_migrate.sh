#!/bin/bash

# BI GHI TOOL MMO - Auto Migration Script
# This script helps migrate the application to a new server

set -e  # Exit on error

echo "╔══════════════════════════════════════════╗"
echo "║  BI GHI TOOL MMO - Migration Tool       ║"
echo "║  Automated Server Migration             ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if running in correct directory
if [ ! -f "app.py" ]; then
    print_error "Error: app.py not found. Please run this script from the webapp directory."
    exit 1
fi

print_info "Current directory: $(pwd)"
echo ""

# Get new server information
echo "📝 Please provide new server information:"
echo ""

read -p "🖥️  New Server IP/Hostname: " NEW_SERVER_IP
read -p "👤 SSH Username: " SSH_USER
read -p "🔢 SSH Port (default 22): " SSH_PORT
SSH_PORT=${SSH_PORT:-22}
read -p "📁 Target Directory (e.g., /home/user/webapp): " TARGET_DIR

echo ""
print_info "Testing SSH connection..."

# Test SSH connection
if ssh -p $SSH_PORT -o ConnectTimeout=5 -o BatchMode=yes $SSH_USER@$NEW_SERVER_IP exit 2>/dev/null; then
    print_success "SSH connection successful!"
else
    print_error "SSH connection failed. Please check:"
    echo "  1. Server IP/hostname is correct"
    echo "  2. SSH port is correct"
    echo "  3. You have SSH key setup or can login"
    echo ""
    read -p "Do you want to continue anyway? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        exit 1
    fi
fi

echo ""
print_info "Creating backup package..."

# Create backup filename with timestamp
BACKUP_FILE="bighi-tool-backup-$(date +%Y%m%d-%H%M%S).tar.gz"

# Create backup excluding unnecessary files
tar -czf $BACKUP_FILE \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='*.log' \
    --exclude='server.log' \
    --exclude='*.tar.gz' \
    --exclude='.cleanup_backup' \
    . 2>/dev/null

if [ -f "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h $BACKUP_FILE | cut -f1)
    print_success "Backup created: $BACKUP_FILE ($BACKUP_SIZE)"
else
    print_error "Failed to create backup"
    exit 1
fi

echo ""
print_info "Uploading to new server..."

# Upload backup to new server
scp -P $SSH_PORT $BACKUP_FILE $SSH_USER@$NEW_SERVER_IP:~/ 2>&1 | while read line; do
    echo "  $line"
done

if [ $? -eq 0 ]; then
    print_success "Upload completed!"
else
    print_error "Upload failed"
    exit 1
fi

echo ""
print_info "Setting up on new server..."

# Setup on new server
ssh -p $SSH_PORT $SSH_USER@$NEW_SERVER_IP bash << EOF
set -e

echo "📁 Creating directory..."
mkdir -p $TARGET_DIR
cd ~

echo "📦 Extracting files..."
tar -xzf $BACKUP_FILE -C $TARGET_DIR

echo "🐍 Setting up Python environment..."
cd $TARGET_DIR

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=\$(python3 --version | cut -d' ' -f2)
    echo "  Python version: \$PYTHON_VERSION"
else
    echo "  ❌ Python3 not found. Please install Python 3.9+"
    exit 1
fi

# Create virtual environment
echo "  Creating virtual environment..."
python3 -m venv venv

# Activate and install dependencies
echo "  Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo "✅ Setup complete!"

# Display next steps
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║         Setup Complete!                  ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "📝 Next steps:"
echo "1. SSH to new server: ssh -p $SSH_PORT $SSH_USER@$NEW_SERVER_IP"
echo "2. Navigate to: cd $TARGET_DIR"
echo "3. Activate venv: source venv/bin/activate"
echo "4. Start server: python3 app.py"
echo ""
echo "🔧 Optional: Setup as systemd service"
echo "   Run: sudo systemctl enable bighi-tool"
echo ""
EOF

if [ $? -eq 0 ]; then
    print_success "Remote setup completed successfully!"
else
    print_error "Remote setup failed"
    exit 1
fi

echo ""
print_info "Cleaning up local backup file..."
rm -f $BACKUP_FILE
print_success "Cleanup complete"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║      🎉 Migration Successful! 🎉        ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "📊 Summary:"
echo "  • Source: $(hostname)"
echo "  • Target: $SSH_USER@$NEW_SERVER_IP:$SSH_PORT"
echo "  • Directory: $TARGET_DIR"
echo "  • Status: ✅ Complete"
echo ""
echo "🚀 To start the server on new host:"
echo "   ssh -p $SSH_PORT $SSH_USER@$NEW_SERVER_IP"
echo "   cd $TARGET_DIR"
echo "   source venv/bin/activate"
echo "   python3 app.py"
echo ""
echo "📝 Documentation: $TARGET_DIR/MIGRATION_GUIDE.md"
echo ""

# Ask if user wants to create systemd service
read -p "Would you like to create a systemd service file? (y/n): " CREATE_SERVICE

if [ "$CREATE_SERVICE" = "y" ]; then
    SERVICE_FILE="bighi-tool.service"
    
    cat > $SERVICE_FILE << SERVICEEOF
[Unit]
Description=BI GHI TOOL MMO Flask Application
After=network.target

[Service]
Type=simple
User=$SSH_USER
WorkingDirectory=$TARGET_DIR
Environment="PATH=$TARGET_DIR/venv/bin"
ExecStart=$TARGET_DIR/venv/bin/python $TARGET_DIR/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICEEOF

    print_success "Service file created: $SERVICE_FILE"
    echo ""
    echo "To install on new server:"
    echo "  1. Copy file: scp -P $SSH_PORT $SERVICE_FILE $SSH_USER@$NEW_SERVER_IP:~/"
    echo "  2. SSH to server: ssh -p $SSH_PORT $SSH_USER@$NEW_SERVER_IP"
    echo "  3. Install: sudo mv ~/$SERVICE_FILE /etc/systemd/system/"
    echo "  4. Enable: sudo systemctl daemon-reload"
    echo "  5. Start: sudo systemctl enable --now bighi-tool"
fi

echo ""
print_success "Migration script completed!"
