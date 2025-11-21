#!/bin/bash
# Auto setup script for mochiphoto.click Cloudflare Tunnel

set -e

DOMAIN="mochiphoto.click"
TUNNEL_NAME="mochiphoto"
LOCAL_PORT="5001"
USER="bighitran1905"

echo "=========================================="
echo "  Cloudflare Tunnel Setup"
echo "  Domain: $DOMAIN"
echo "=========================================="
echo ""

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "❌ cloudflared not found! Installing..."
    wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    sudo dpkg -i cloudflared-linux-amd64.deb
    echo "✅ cloudflared installed"
else
    echo "✅ cloudflared already installed: $(cloudflared --version)"
fi

echo ""
echo "=========================================="
echo "STEP 1: Login to Cloudflare"
echo "=========================================="
echo ""
echo "⚠️  A browser window will open."
echo "   Please login and authorize the domain."
echo ""
read -p "Press Enter to continue..."

cloudflared tunnel login

if [ ! -f ~/.cloudflared/cert.pem ]; then
    echo "❌ Login failed! cert.pem not found."
    exit 1
fi

echo "✅ Cloudflare login successful!"

echo ""
echo "=========================================="
echo "STEP 2: Create Tunnel"
echo "=========================================="
echo ""

# Check if tunnel already exists
if cloudflared tunnel list | grep -q "$TUNNEL_NAME"; then
    echo "⚠️  Tunnel '$TUNNEL_NAME' already exists!"
    read -p "Delete and recreate? (y/n): " RECREATE
    if [ "$RECREATE" = "y" ]; then
        echo "Deleting old tunnel..."
        cloudflared tunnel delete -f "$TUNNEL_NAME"
        echo "Creating new tunnel..."
        cloudflared tunnel create "$TUNNEL_NAME"
    else
        echo "Using existing tunnel..."
    fi
else
    echo "Creating tunnel: $TUNNEL_NAME"
    cloudflared tunnel create "$TUNNEL_NAME"
fi

# Get tunnel ID
TUNNEL_ID=$(cloudflared tunnel list | grep "$TUNNEL_NAME" | awk '{print $1}')

if [ -z "$TUNNEL_ID" ]; then
    echo "❌ Failed to get tunnel ID!"
    exit 1
fi

echo "✅ Tunnel created!"
echo "   Tunnel ID: $TUNNEL_ID"

echo ""
echo "=========================================="
echo "STEP 3: Configure Tunnel"
echo "=========================================="
echo ""

# Create config directory
mkdir -p ~/.cloudflared

# Create config file
cat > ~/.cloudflared/config.yml << EOF
url: http://localhost:$LOCAL_PORT
tunnel: $TUNNEL_ID
credentials-file: /home/$USER/.cloudflared/$TUNNEL_ID.json
loglevel: info
EOF

echo "✅ Config file created: ~/.cloudflared/config.yml"
cat ~/.cloudflared/config.yml

echo ""
echo "=========================================="
echo "STEP 4: Route DNS"
echo "=========================================="
echo ""

echo "Creating DNS routes..."

# Route main domain
cloudflared tunnel route dns "$TUNNEL_NAME" "$DOMAIN"
echo "✅ Routed: $DOMAIN"

# Route www subdomain
read -p "Also route www.$DOMAIN? (y/n): " ROUTE_WWW
if [ "$ROUTE_WWW" = "y" ]; then
    cloudflared tunnel route dns "$TUNNEL_NAME" "www.$DOMAIN"
    echo "✅ Routed: www.$DOMAIN"
fi

echo ""
echo "=========================================="
echo "STEP 5: Test Tunnel (Manual)"
echo "=========================================="
echo ""

echo "⚠️  Before starting tunnel, make sure Flask is running on port $LOCAL_PORT"
echo ""
read -p "Is Flask running? (y/n): " FLASK_RUNNING

if [ "$FLASK_RUNNING" != "y" ]; then
    echo ""
    echo "Starting Flask app..."
    cd /home/$USER/webapp
    source venv/bin/activate
    nohup python app.py > /tmp/flask_mochiphoto.log 2>&1 &
    echo "✅ Flask started in background"
    sleep 3
fi

echo ""
echo "Testing tunnel manually (press Ctrl+C to stop)..."
echo "After testing, we'll setup systemd service."
echo ""
read -p "Press Enter to start test..."

cloudflared tunnel run "$TUNNEL_NAME" &
TUNNEL_PID=$!

echo ""
echo "🔄 Tunnel is running (PID: $TUNNEL_PID)"
echo ""
echo "Test in browser: https://$DOMAIN"
echo ""
read -p "Press Enter after testing to continue with systemd setup..."

# Stop test tunnel
kill $TUNNEL_PID 2>/dev/null || true
sleep 2

echo ""
echo "=========================================="
echo "STEP 6: Setup Systemd Service"
echo "=========================================="
echo ""

# Create systemd service
sudo tee /etc/systemd/system/cloudflared-$TUNNEL_NAME.service > /dev/null << EOF
[Unit]
Description=Cloudflare Tunnel for $DOMAIN
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=/usr/bin/cloudflared tunnel run $TUNNEL_NAME
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Systemd service created"

# Reload, enable, and start service
sudo systemctl daemon-reload
sudo systemctl enable cloudflared-$TUNNEL_NAME
sudo systemctl start cloudflared-$TUNNEL_NAME

echo ""
echo "✅ Service started!"
echo ""

# Show status
sudo systemctl status cloudflared-$TUNNEL_NAME --no-pager

echo ""
echo "=========================================="
echo "  SETUP COMPLETE! 🎉"
echo "=========================================="
echo ""
echo "📋 Summary:"
echo "   Domain:      $DOMAIN"
echo "   Tunnel:      $TUNNEL_NAME"
echo "   Tunnel ID:   $TUNNEL_ID"
echo "   Local Port:  $LOCAL_PORT"
echo ""
echo "🌐 Your website will be available at:"
echo "   https://$DOMAIN"
echo ""
echo "⚠️  IMPORTANT: Update nameservers at TenTen.vn"
echo ""
echo "   1. Login to TenTen.vn"
echo "   2. Go to Domain Management"
echo "   3. Select: $DOMAIN"
echo "   4. Update nameservers to Cloudflare's nameservers"
echo "   5. Wait 1-24 hours for DNS propagation"
echo ""
echo "📊 Check Cloudflare Dashboard for nameservers:"
echo "   https://dash.cloudflare.com"
echo ""
echo "🔧 Useful commands:"
echo "   sudo systemctl status cloudflared-$TUNNEL_NAME"
echo "   sudo systemctl restart cloudflared-$TUNNEL_NAME"
echo "   sudo journalctl -u cloudflared-$TUNNEL_NAME -f"
echo "   cloudflared tunnel list"
echo "   cloudflared tunnel info $TUNNEL_NAME"
echo ""
echo "=========================================="
