#!/bin/bash

# BI GHI TOOL MMO - Deploy to Ubuntu Server
# Optimized for Ubuntu 22.04 with Gunicorn + Nginx

set -e

echo "╔══════════════════════════════════════════╗"
echo "║  BI GHI TOOL MMO - Ubuntu Deploy        ║"
echo "║  Flask + Gunicorn + Nginx               ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Server configuration
NEW_SERVER="14.225.210.195"
SSH_USER="root"  # Change if different
SSH_PORT="22"
APP_DIR="/home/bitool/webapp"
APP_NAME="bighi-tool-mmo"

echo -e "${BLUE}📝 Server Information:${NC}"
echo "  IP: $NEW_SERVER"
echo "  User: $SSH_USER"
echo "  Port: $SSH_PORT"
echo "  Directory: $APP_DIR"
echo ""

read -p "Is this correct? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "Please edit the script with correct information"
    exit 1
fi

echo ""
echo -e "${BLUE}📦 Step 1: Creating backup...${NC}"

# Create backup
tar -czf webapp-deploy.tar.gz \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='*.log' \
    --exclude='*.tar.gz' \
    .

BACKUP_SIZE=$(du -h webapp-deploy.tar.gz | cut -f1)
echo -e "${GREEN}✅ Backup created: webapp-deploy.tar.gz ($BACKUP_SIZE)${NC}"

echo ""
echo -e "${BLUE}🚀 Step 2: Uploading to server...${NC}"

# Upload backup
scp -P $SSH_PORT webapp-deploy.tar.gz $SSH_USER@$NEW_SERVER:~/

echo -e "${GREEN}✅ Upload completed!${NC}"

echo ""
echo -e "${BLUE}⚙️  Step 3: Setting up on server...${NC}"

# Deploy on server
ssh -p $SSH_PORT $SSH_USER@$NEW_SERVER bash << 'ENDSSH'
set -e

echo "📦 Installing system dependencies..."
apt update
apt install -y python3 python3-pip python3-venv nginx sqlite3 supervisor

echo "📁 Creating directory structure..."
mkdir -p /home/bitool/webapp/logs
cd /home/bitool

echo "📦 Extracting files..."
tar -xzf ~/webapp-deploy.tar.gz -C /home/bitool/webapp/

echo "🐍 Setting up Python environment..."
cd /home/bitool/webapp
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

echo "🔧 Updating Gunicorn config paths..."
sed -i 's|/home/user/webapp|/home/bitool/webapp|g' gunicorn_config.py

echo "📝 Creating systemd service..."
cat > /etc/systemd/system/bighi-tool.service << 'EOF'
[Unit]
Description=BI GHI TOOL MMO - Gunicorn
After=network.target

[Service]
Type=notify
User=root
Group=root
WorkingDirectory=/home/bitool/webapp
Environment="PATH=/home/bitool/webapp/venv/bin"
ExecStart=/home/bitool/webapp/venv/bin/gunicorn \
    --config gunicorn_config.py \
    wsgi:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "🌐 Configuring Nginx..."
cat > /etc/nginx/sites-available/bighi-tool << 'EOF'
server {
    listen 80;
    server_name 14.225.210.195;

    location / {
        proxy_pass http://127.0.0.1:5003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files
    location /static {
        alias /home/bitool/webapp/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
EOF

# Enable Nginx site
ln -sf /etc/nginx/sites-available/bighi-tool /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx config
nginx -t

echo "🔄 Starting services..."
systemctl daemon-reload
systemctl enable bighi-tool
systemctl start bighi-tool
systemctl restart nginx

echo "✅ Setup complete!"
echo ""
echo "📊 Service Status:"
systemctl status bighi-tool --no-pager | head -10
echo ""
systemctl status nginx --no-pager | head -10

ENDSSH

echo ""
echo -e "${GREEN}✅ Deployment completed successfully!${NC}"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║          🎉 Deployment Success! 🎉      ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "📊 Access your application:"
echo "  • HTTP:  http://14.225.210.195"
echo "  • Port:  80 (Nginx reverse proxy)"
echo ""
echo "🔧 Useful commands on new server:"
echo "  • Status:  sudo systemctl status bighi-tool"
echo "  • Logs:    sudo journalctl -u bighi-tool -f"
echo "  • Restart: sudo systemctl restart bighi-tool"
echo "  • Nginx:   sudo systemctl status nginx"
echo ""
echo "📝 Configuration files:"
echo "  • App:     /home/bitool/webapp/"
echo "  • Service: /etc/systemd/system/bighi-tool.service"
echo "  • Nginx:   /etc/nginx/sites-available/bighi-tool"
echo "  • Logs:    /home/bitool/webapp/logs/"
echo ""

# Cleanup
rm -f webapp-deploy.tar.gz

echo -e "${BLUE}🧪 Testing endpoints...${NC}"
sleep 5

# Test HTTP
echo -n "Testing HTTP (port 80): "
if curl -s -o /dev/null -w "%{http_code}" http://$NEW_SERVER/ | grep -q "200"; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${YELLOW}⚠️  May need few seconds to start${NC}"
fi

echo ""
echo -e "${GREEN}🎉 All done! Your app is running!${NC}"
