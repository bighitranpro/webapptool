#!/bin/bash

# BI GHI TOOL MMO - Deploy to Ubuntu Server với Password
# Tự động login với password Bg190597@

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
SSH_USER="biproduction"
SSH_PORT="22"
SSH_PASSWORD="Bg190597@"
APP_DIR="/home/bitool/webapp"
APP_NAME="bighi-tool-mmo"

echo -e "${BLUE}📝 Server Information:${NC}"
echo "  IP: $NEW_SERVER"
echo "  User: $SSH_USER"
echo "  Port: $SSH_PORT"
echo "  Directory: $APP_DIR"
echo ""

# Check sshpass
if ! command -v sshpass &> /dev/null; then
    echo -e "${YELLOW}⚠️  Installing sshpass...${NC}"
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get install -y sshpass 2>/dev/null || sudo yum install -y sshpass 2>/dev/null
    fi
fi

echo -e "${BLUE}🔐 Testing SSH connection...${NC}"

# Test SSH connection
if sshpass -p "$SSH_PASSWORD" ssh -p $SSH_PORT -o StrictHostKeyChecking=no -o ConnectTimeout=5 $SSH_USER@$NEW_SERVER "echo 'OK'" &>/dev/null; then
    echo -e "${GREEN}✅ SSH connection successful!${NC}"
else
    echo -e "${YELLOW}❌ SSH connection failed. Checking...${NC}"
    echo ""
    echo "Please verify:"
    echo "  1. Server IP: $NEW_SERVER"
    echo "  2. Username: $SSH_USER"
    echo "  3. Password: $SSH_PASSWORD"
    echo ""
    read -p "Continue anyway? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        exit 1
    fi
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
    --exclude='.cleanup_backup' \
    . 2>/dev/null

BACKUP_SIZE=$(du -h webapp-deploy.tar.gz | cut -f1)
echo -e "${GREEN}✅ Backup created: webapp-deploy.tar.gz ($BACKUP_SIZE)${NC}"

echo ""
echo -e "${BLUE}🚀 Step 2: Uploading to server...${NC}"

# Upload backup using sshpass
sshpass -p "$SSH_PASSWORD" scp -P $SSH_PORT -o StrictHostKeyChecking=no webapp-deploy.tar.gz $SSH_USER@$NEW_SERVER:~/ 2>&1 | while read line; do
    echo "  $line"
done

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Upload completed!${NC}"
else
    echo -e "${YELLOW}❌ Upload failed${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}⚙️  Step 3: Setting up on server...${NC}"

# Deploy on server using sshpass
sshpass -p "$SSH_PASSWORD" ssh -p $SSH_PORT -o StrictHostKeyChecking=no $SSH_USER@$NEW_SERVER bash << 'ENDSSH'
set -e

echo "📦 Installing system dependencies..."
echo "Bg190597@" | sudo -S apt update
echo "Bg190597@" | sudo -S apt install -y python3 python3-pip python3-venv nginx sqlite3

echo "📁 Creating directory structure..."
sudo mkdir -p /home/bitool/webapp/logs
sudo chown -R biproduction:biproduction /home/bitool
cd /home/bitool

echo "📦 Extracting files..."
tar -xzf ~/webapp-deploy.tar.gz -C /home/bitool/webapp/

echo "🐍 Setting up Python environment..."
cd /home/bitool/webapp
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install gunicorn -q

echo "🔧 Updating Gunicorn config paths..."
sed -i 's|/home/user/webapp|/home/bitool/webapp|g' gunicorn_config.py

echo "📝 Creating systemd service..."
sudo tee /etc/systemd/system/bighi-tool.service > /dev/null << 'EOF'
[Unit]
Description=BI GHI TOOL MMO - Gunicorn
After=network.target

[Service]
Type=notify
User=biproduction
Group=biproduction
WorkingDirectory=/home/bitool/webapp
Environment="PATH=/home/bitool/webapp/venv/bin"
ExecStart=/home/bitool/webapp/venv/bin/gunicorn --config gunicorn_config.py wsgi:app
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
sudo tee /etc/nginx/sites-available/bighi-tool > /dev/null << 'EOF'
server {
    listen 80;
    server_name 14.225.210.195;

    location / {
        proxy_pass http://127.0.0.1:5003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /static {
        alias /home/bitool/webapp/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/bighi-tool /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx config
sudo nginx -t

echo "🔄 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable bighi-tool
sudo systemctl start bighi-tool
sudo systemctl restart nginx

echo "✅ Setup complete!"
echo ""
echo "📊 Service Status:"
sudo systemctl status bighi-tool --no-pager | head -10

ENDSSH

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Remote setup completed successfully!${NC}"
else
    echo -e "${YELLOW}❌ Remote setup failed${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}🧹 Cleaning up local backup...${NC}"
rm -f webapp-deploy.tar.gz
echo -e "${GREEN}✅ Cleanup complete${NC}"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║      🎉 Deployment Success! 🎉          ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "📊 Summary:"
echo "  • Server: $NEW_SERVER"
echo "  • User: $SSH_USER"
echo "  • Directory: $APP_DIR"
echo "  • Status: ✅ Complete"
echo ""
echo "🌐 Access your application:"
echo "  • HTTP:  http://14.225.210.195"
echo "  • Port:  80 (Nginx reverse proxy)"
echo ""
echo "🔧 Useful commands:"
echo "  • SSH:     sshpass -p 'Bg190597@' ssh biproduction@14.225.210.195"
echo "  • Status:  sudo systemctl status bighi-tool"
echo "  • Logs:    sudo journalctl -u bighi-tool -f"
echo "  • Restart: sudo systemctl restart bighi-tool"
echo ""

echo ""
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
echo -e "${GREEN}🎉 All done! Your app is running at http://14.225.210.195${NC}"
