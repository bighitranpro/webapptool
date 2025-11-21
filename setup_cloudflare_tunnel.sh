#!/bin/bash

# ============================================
# BI GHI TOOL - CLOUDFLARE TUNNEL SETUP SCRIPT
# Automated setup for Cloudflare Tunnel
# ============================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "============================================"
echo "   BI GHI TOOL - CLOUDFLARE TUNNEL SETUP"
echo "============================================"
echo -e "${NC}"

# Function to print colored messages
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Check if cloudflared is installed
echo ""
print_info "Checking cloudflared installation..."
if ! command -v cloudflared &> /dev/null; then
    print_error "cloudflared is not installed!"
    echo "Please install it first:"
    echo "  wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb"
    echo "  sudo dpkg -i cloudflared-linux-amd64.deb"
    exit 1
fi

CLOUDFLARED_VERSION=$(cloudflared --version | head -1)
print_success "cloudflared is installed: $CLOUDFLARED_VERSION"

# Check if cert.pem exists
echo ""
print_info "Checking Cloudflare authentication..."
if [ ! -f ~/.cloudflared/cert.pem ]; then
    print_warning "Not logged in to Cloudflare yet!"
    echo ""
    echo "Please run: cloudflared tunnel login"
    echo ""
    echo "This will:"
    echo "  1. Open a URL in your browser"
    echo "  2. Ask you to login to Cloudflare"
    echo "  3. Select your domain to authorize"
    echo "  4. Create cert.pem file"
    echo ""
    read -p "Press Enter after you've completed the login..."
    
    if [ ! -f ~/.cloudflared/cert.pem ]; then
        print_error "cert.pem still not found. Please complete cloudflared login first."
        exit 1
    fi
fi

print_success "Cloudflare authentication found (cert.pem exists)"

# Get domain name
echo ""
echo -e "${YELLOW}======================================"
echo "DOMAIN CONFIGURATION"
echo -e "======================================${NC}"
echo ""
read -p "Enter your domain name (e.g., bighitool.com): " DOMAIN

if [ -z "$DOMAIN" ]; then
    print_error "Domain name is required!"
    exit 1
fi

print_info "Domain: $DOMAIN"

# Tunnel name
TUNNEL_NAME="bighitool"

# Check if tunnel already exists
echo ""
print_info "Checking if tunnel '$TUNNEL_NAME' exists..."

if cloudflared tunnel list | grep -q "$TUNNEL_NAME"; then
    print_warning "Tunnel '$TUNNEL_NAME' already exists!"
    read -p "Do you want to use the existing tunnel? (y/n): " USE_EXISTING
    
    if [ "$USE_EXISTING" != "y" ]; then
        echo "Please delete the existing tunnel first:"
        echo "  cloudflared tunnel delete $TUNNEL_NAME"
        exit 1
    fi
    
    # Get existing tunnel ID
    TUNNEL_ID=$(cloudflared tunnel list | grep "$TUNNEL_NAME" | awk '{print $1}')
    print_info "Using existing tunnel ID: $TUNNEL_ID"
else
    # Create new tunnel
    print_info "Creating new tunnel '$TUNNEL_NAME'..."
    OUTPUT=$(cloudflared tunnel create $TUNNEL_NAME 2>&1)
    
    if [ $? -eq 0 ]; then
        print_success "Tunnel created successfully!"
        
        # Extract tunnel ID from output
        TUNNEL_ID=$(echo "$OUTPUT" | grep -oP 'Tunnel credentials written to.*?/\K[^.]+(?=\.json)')
        
        if [ -z "$TUNNEL_ID" ]; then
            # Try alternative method
            TUNNEL_ID=$(cloudflared tunnel list | grep "$TUNNEL_NAME" | awk '{print $1}')
        fi
        
        print_info "Tunnel ID: $TUNNEL_ID"
    else
        print_error "Failed to create tunnel!"
        echo "$OUTPUT"
        exit 1
    fi
fi

# Create config file
echo ""
print_info "Creating tunnel configuration..."

mkdir -p ~/.cloudflared

CONFIG_FILE=~/.cloudflared/config.yml

cat > $CONFIG_FILE << EOF
url: http://localhost:5003
tunnel: $TUNNEL_ID
credentials-file: /home/$USER/.cloudflared/$TUNNEL_ID.json
loglevel: info
EOF

print_success "Config file created: $CONFIG_FILE"

echo ""
print_info "Config contents:"
cat $CONFIG_FILE

# Verify credentials file exists
CREDS_FILE=~/.cloudflared/$TUNNEL_ID.json
if [ ! -f "$CREDS_FILE" ]; then
    print_error "Credentials file not found: $CREDS_FILE"
    echo "Expected location: $CREDS_FILE"
    echo "Available files:"
    ls -la ~/.cloudflared/
    exit 1
fi

print_success "Credentials file found: $CREDS_FILE"

# Route DNS
echo ""
print_info "Routing DNS for domain: $DOMAIN"
read -p "Do you want to route DNS now? This will create a CNAME record in Cloudflare (y/n): " ROUTE_DNS

if [ "$ROUTE_DNS" = "y" ]; then
    OUTPUT=$(cloudflared tunnel route dns $TUNNEL_NAME $DOMAIN 2>&1)
    
    if echo "$OUTPUT" | grep -q "Created CNAME"; then
        print_success "DNS routed successfully!"
        print_info "CNAME record created: $DOMAIN → $TUNNEL_ID.cfargotunnel.com"
    elif echo "$OUTPUT" | grep -q "already exists"; then
        print_warning "DNS record already exists for $DOMAIN"
    else
        print_error "Failed to route DNS!"
        echo "$OUTPUT"
    fi
fi

# Test tunnel
echo ""
echo -e "${YELLOW}======================================"
echo "TESTING TUNNEL"
echo -e "======================================${NC}"
print_info "Starting tunnel in test mode..."
print_warning "Press Ctrl+C to stop after testing"

echo ""
read -p "Press Enter to start tunnel test..."

cloudflared tunnel run $TUNNEL_NAME &
TUNNEL_PID=$!

sleep 5

echo ""
print_success "Tunnel is running! (PID: $TUNNEL_PID)"
print_info "Test your domain: https://$DOMAIN"
echo ""
read -p "Press Enter after testing to continue..."

# Kill test tunnel
kill $TUNNEL_PID 2>/dev/null || true
print_info "Test tunnel stopped"

# Setup systemd service
echo ""
echo -e "${YELLOW}======================================"
echo "SYSTEMD SERVICE SETUP"
echo -e "======================================${NC}"
read -p "Do you want to setup systemd service for auto-start? (y/n): " SETUP_SYSTEMD

if [ "$SETUP_SYSTEMD" = "y" ]; then
    print_info "Creating systemd service..."
    
    SERVICE_FILE=/etc/systemd/system/cloudflared.service
    
    sudo tee $SERVICE_FILE > /dev/null << EOF
[Unit]
Description=Cloudflare Tunnel for BI GHI TOOL
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=/usr/local/bin/cloudflared tunnel run $TUNNEL_NAME
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    
    print_success "Service file created: $SERVICE_FILE"
    
    # Reload systemd
    print_info "Reloading systemd daemon..."
    sudo systemctl daemon-reload
    
    # Enable service
    print_info "Enabling cloudflared service..."
    sudo systemctl enable cloudflared
    
    # Start service
    print_info "Starting cloudflared service..."
    sudo systemctl start cloudflared
    
    sleep 3
    
    # Check status
    if sudo systemctl is-active --quiet cloudflared; then
        print_success "Cloudflared service is running!"
        
        echo ""
        print_info "Service commands:"
        echo "  sudo systemctl status cloudflared   - Check status"
        echo "  sudo systemctl stop cloudflared     - Stop service"
        echo "  sudo systemctl restart cloudflared  - Restart service"
        echo "  sudo journalctl -u cloudflared -f  - View logs"
    else
        print_error "Failed to start cloudflared service!"
        echo "Check status with: sudo systemctl status cloudflared"
        echo "Check logs with: sudo journalctl -u cloudflared -n 50"
    fi
fi

# Summary
echo ""
echo -e "${GREEN}"
echo "============================================"
echo "   SETUP COMPLETE! 🎉"
echo "============================================"
echo -e "${NC}"

echo ""
echo -e "${BLUE}📊 CONFIGURATION SUMMARY:${NC}"
echo "  Domain:      https://$DOMAIN"
echo "  Tunnel Name: $TUNNEL_NAME"
echo "  Tunnel ID:   $TUNNEL_ID"
echo "  Local Port:  5003"
echo "  Config File: ~/.cloudflared/config.yml"
echo ""

echo -e "${BLUE}🔗 ACCESS POINTS:${NC}"
echo "  Main:        https://$DOMAIN"
echo "  Login:       https://$DOMAIN/login"
echo "  Register:    https://$DOMAIN/register"
echo "  Dashboard:   https://$DOMAIN/dashboard"
echo "  Admin:       https://$DOMAIN/admin"
echo ""

echo -e "${BLUE}👤 ADMIN ACCOUNTS:${NC}"
echo "  Username: admin      | Password: admin123  | VIP: 3"
echo "  Username: biadmin    | Password: 190597    | VIP: 3"
echo ""

echo -e "${BLUE}✅ NEXT STEPS:${NC}"
echo "  1. Test your domain: https://$DOMAIN"
echo "  2. Login with biadmin account"
echo "  3. Configure your application"
echo "  4. Share with users!"
echo ""

print_success "All done! Your Cloudflare Tunnel is ready! 🚀"
echo ""
