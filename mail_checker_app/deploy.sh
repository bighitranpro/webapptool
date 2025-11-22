#!/bin/bash

###############################################################################
# Deploy Script for Email Checker Flask App
# For Ubuntu 20.04 VPS
###############################################################################

set -e  # Exit on error

echo "========================================="
echo "Email Checker Deployment Script"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
APP_DIR="/root/mail_checker_app"
SERVICE_NAME="mailchecker"
APP_USER="root"  # Change if running as different user
PYTHON_VERSION="python3"

echo -e "${GREEN}Step 1: Updating system packages...${NC}"
apt-get update -y

echo -e "${GREEN}Step 2: Installing required system packages...${NC}"
apt-get install -y python3 python3-pip python3-venv nginx ufw

echo -e "${GREEN}Step 3: Setting up Python virtual environment...${NC}"
cd $APP_DIR

if [ -d "venv" ]; then
    echo "Virtual environment already exists, removing..."
    rm -rf venv
fi

$PYTHON_VERSION -m venv venv
source venv/bin/activate

echo -e "${GREEN}Step 4: Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}Step 5: Creating results directory...${NC}"
mkdir -p $APP_DIR/results
chmod 755 $APP_DIR/results

echo -e "${GREEN}Step 6: Setting up Gunicorn systemd service...${NC}"
cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=Gunicorn instance for Email Checker Flask App
After=network.target

[Service]
User=$APP_USER
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 --timeout 120 app:app

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}Step 7: Setting up Nginx configuration...${NC}"
cat > /etc/nginx/sites-available/${SERVICE_NAME} << 'EOF'
server {
    listen 80;
    server_name _;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    location /static {
        alias /root/mail_checker_app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable nginx site
if [ -L "/etc/nginx/sites-enabled/${SERVICE_NAME}" ]; then
    rm /etc/nginx/sites-enabled/${SERVICE_NAME}
fi
ln -s /etc/nginx/sites-available/${SERVICE_NAME} /etc/nginx/sites-enabled/

# Remove default nginx site if exists
if [ -L "/etc/nginx/sites-enabled/default" ]; then
    rm /etc/nginx/sites-enabled/default
fi

echo -e "${GREEN}Step 8: Testing Nginx configuration...${NC}"
nginx -t

echo -e "${GREEN}Step 9: Configuring firewall (UFW)...${NC}"
ufw --force enable
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw status

echo -e "${GREEN}Step 10: Starting services...${NC}"
systemctl daemon-reload
systemctl restart ${SERVICE_NAME}
systemctl enable ${SERVICE_NAME}
systemctl restart nginx
systemctl enable nginx

echo ""
echo -e "${GREEN}Step 11: Checking service status...${NC}"
systemctl status ${SERVICE_NAME} --no-pager -l

echo ""
echo "========================================="
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo "========================================="
echo ""
echo "Service Status:"
echo "  - Gunicorn service: systemctl status ${SERVICE_NAME}"
echo "  - Nginx service: systemctl status nginx"
echo ""
echo "Useful Commands:"
echo "  - View logs: journalctl -u ${SERVICE_NAME} -f"
echo "  - Restart app: systemctl restart ${SERVICE_NAME}"
echo "  - Restart nginx: systemctl restart nginx"
echo ""
echo "Access your application:"
echo "  - HTTP: http://$(hostname -I | awk '{print $1}')"
echo ""
echo "To setup SSL with Let's Encrypt (if you have a domain):"
echo "  1. Install certbot: apt-get install certbot python3-certbot-nginx"
echo "  2. Get certificate: certbot --nginx -d your-domain.com"
echo ""

# Check if services are running
if systemctl is-active --quiet ${SERVICE_NAME}; then
    echo -e "${GREEN}✓ Gunicorn service is running${NC}"
else
    echo -e "${RED}✗ Gunicorn service failed to start${NC}"
    echo "Check logs with: journalctl -u ${SERVICE_NAME} -n 50"
fi

if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx service is running${NC}"
else
    echo -e "${RED}✗ Nginx service failed to start${NC}"
    echo "Check logs with: journalctl -u nginx -n 50"
fi

echo ""
echo -e "${YELLOW}Note: This deployment script assumes you're running as root on Ubuntu 20.04${NC}"
echo -e "${YELLOW}For production, consider:${NC}"
echo "  - Running app as non-root user"
echo "  - Setting up proper environment variables"
echo "  - Configuring log rotation"
echo "  - Setting up monitoring"
echo ""
