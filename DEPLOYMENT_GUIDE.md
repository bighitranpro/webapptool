# 🚀 Hướng Dẫn Triển Khai Lên VPS Mới

## 📋 Thông Tin VPS

- **IP Address**: 14.225.210.195
- **Operating System**: Ubuntu 22.04 x64
- **SSH Username**: biproduction
- **SSH Password**: Bg190597@
- **SSH Port**: 22
- **Application Directory**: /home/bitool/webapp

---

## ✅ Trạng Thái Hiện Tại

### Đã Hoàn Thành
1. ✅ **Cập nhật credentials** - Tất cả scripts đã được cập nhật với thông tin VPS mới
2. ✅ **Tạo deployment scripts** - 3 scripts mới đã được tạo và kiểm tra
3. ✅ **Commit changes** - Tất cả thay đổi đã được commit vào Git
4. ✅ **Merge remote changes** - Đã merge GitHub Actions workflows (CodeQL, API Security)

### Scripts Đã Sẵn Sàng
- `deploy_to_ubuntu.sh` - Deployment script với SSH key (đã cập nhật user)
- `deploy_with_password.sh` - **RECOMMENDED** - Deployment script với password authentication
- `setup_vps_security.sh` - Script đổi password VPS (nếu cần)

---

## 🎯 Phương Án Triển Khai

### Phương Án 1: Tự Động Hoàn Toàn (KHUYẾN NGHỊ)

Sử dụng script `deploy_with_password.sh` - script này sẽ tự động:

1. ✅ Install sshpass (để SSH với password)
2. ✅ Tạo backup của source code
3. ✅ Upload lên VPS mới
4. ✅ Install Python 3, pip, venv
5. ✅ Install Nginx reverse proxy
6. ✅ Install Gunicorn WSGI server
7. ✅ Setup systemd service (auto-restart)
8. ✅ Configure Nginx (port 80 → 5003)
9. ✅ Start application
10. ✅ Test tất cả endpoints

#### Cách Chạy:

```bash
cd /home/bighitran1905/webapp
./deploy_with_password.sh
```

**Thời gian ước tính**: 5-10 phút

**Kết quả**: Website sẽ chạy tại `http://14.225.210.195`

---

### Phương Án 2: Thủ Công (Nếu Script Gặp Vấn Đề)

#### Bước 1: Cài đặt sshpass
```bash
# Trên máy local (sandbox)
cd /home/bighitran1905/webapp
sudo apt-get update
sudo apt-get install -y sshpass
```

#### Bước 2: Tạo backup
```bash
tar -czf webapp-deploy.tar.gz \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='logs/*.log' \
    --exclude='*.db-journal' \
    .
```

#### Bước 3: Upload lên VPS
```bash
sshpass -p "Bg190597@" scp -P 22 \
    webapp-deploy.tar.gz \
    biproduction@14.225.210.195:~/
```

#### Bước 4: SSH vào VPS và deploy
```bash
sshpass -p "Bg190597@" ssh -p 22 biproduction@14.225.210.195
```

Sau khi vào VPS, chạy các lệnh sau:

```bash
# Extract source code
cd ~
tar -xzf webapp-deploy.tar.gz -C /home/bitool/
cd /home/bitool/webapp

# Install dependencies
echo "Bg190597@" | sudo -S apt-get update
echo "Bg190597@" | sudo -S apt-get install -y python3 python3-pip python3-venv nginx

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create logs directory
mkdir -p logs
touch logs/access.log logs/error.log

# Create systemd service
echo "Bg190597@" | sudo -S tee /etc/systemd/system/bighi-tool.service > /dev/null << 'EOF'
[Unit]
Description=BI GHI TOOL MMO - Professional Email & Facebook Tools
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

# Configure Nginx
echo "Bg190597@" | sudo -S tee /etc/nginx/sites-available/bighi-tool > /dev/null << 'EOF'
server {
    listen 80;
    server_name 14.225.210.195;

    access_log /var/log/nginx/bighi-tool-access.log;
    error_log /var/log/nginx/bighi-tool-error.log;

    location / {
        proxy_pass http://127.0.0.1:5003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }

    location /static {
        alias /home/bitool/webapp/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable site and restart services
echo "Bg190597@" | sudo -S ln -sf /etc/nginx/sites-available/bighi-tool /etc/nginx/sites-enabled/
echo "Bg190597@" | sudo -S rm -f /etc/nginx/sites-enabled/default
echo "Bg190597@" | sudo -S nginx -t
echo "Bg190597@" | sudo -S systemctl daemon-reload
echo "Bg190597@" | sudo -S systemctl enable bighi-tool
echo "Bg190597@" | sudo -S systemctl start bighi-tool
echo "Bg190597@" | sudo -S systemctl restart nginx

# Check status
echo "Bg190597@" | sudo -S systemctl status bighi-tool --no-pager
echo "Bg190597@" | sudo -S systemctl status nginx --no-pager
```

---

## 🧪 Kiểm Tra Sau Khi Deploy

### 1. Kiểm tra services đang chạy
```bash
# Trên VPS
echo "Bg190597@" | sudo -S systemctl status bighi-tool
echo "Bg190597@" | sudo -S systemctl status nginx
```

### 2. Kiểm tra ports
```bash
# Trên VPS
sudo netstat -tulpn | grep -E ':(80|5003)'
```

Output mong đợi:
```
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      1234/nginx
tcp        0      0 0.0.0.0:5003            0.0.0.0:*               LISTEN      5678/gunicorn
```

### 3. Test endpoints từ trình duyệt
- **Landing Page**: http://14.225.210.195/
- **Login**: http://14.225.210.195/login
- **Register**: http://14.225.210.195/register
- **Dashboard** (sau khi login): http://14.225.210.195/dashboard

### 4. Test endpoints từ command line
```bash
# Test landing page
curl -I http://14.225.210.195/

# Test API health
curl http://14.225.210.195/api/health

# Test dashboard stats API
curl http://14.225.210.195/api/dashboard/stats
```

---

## 🔍 Troubleshooting

### Lỗi: "Connection refused"
```bash
# Kiểm tra firewall
echo "Bg190597@" | sudo -S ufw status
echo "Bg190597@" | sudo -S ufw allow 80/tcp
echo "Bg190597@" | sudo -S ufw allow 22/tcp

# Restart services
echo "Bg190597@" | sudo -S systemctl restart bighi-tool
echo "Bg190597@" | sudo -S systemctl restart nginx
```

### Lỗi: "502 Bad Gateway"
```bash
# Kiểm tra Gunicorn đang chạy
echo "Bg190597@" | sudo -S systemctl status bighi-tool

# Xem logs
tail -f /home/bitool/webapp/logs/error.log
echo "Bg190597@" | sudo -S tail -f /var/log/nginx/bighi-tool-error.log
```

### Lỗi: "Permission denied"
```bash
# Fix ownership
echo "Bg190597@" | sudo -S chown -R biproduction:biproduction /home/bitool/webapp
echo "Bg190597@" | sudo -S chmod +x /home/bitool/webapp/*.sh
```

### Restart toàn bộ application
```bash
echo "Bg190597@" | sudo -S systemctl restart bighi-tool
echo "Bg190597@" | sudo -S systemctl restart nginx
```

---

## 📊 Thông Số Hiệu Năng

### Gunicorn Configuration
- **Workers**: 9 (CPU cores * 2 + 1)
- **Worker Class**: sync
- **Timeout**: 30 seconds
- **Max Requests**: 1000 (auto-restart worker sau 1000 requests)
- **Keepalive**: 2 seconds

### Nginx Configuration
- **Client Max Body Size**: 10M (mặc định)
- **Proxy Timeout**: 300 seconds
- **Static Files Caching**: 30 days

### Performance Expected
- **Concurrent Requests**: 500+ req/s
- **Response Time**: < 100ms (static), < 500ms (API)
- **Uptime**: 99.9% (với systemd auto-restart)

---

## 🔐 Bảo Mật

### Đã Áp Dụng
- ✅ Non-root user (biproduction)
- ✅ Nginx reverse proxy (hiding Gunicorn)
- ✅ Process isolation (systemd)
- ✅ PrivateTmp (systemd security)

### Khuyến Nghị Thêm (Tùy Chọn)
- 🔒 Setup SSH key authentication (thay vì password)
- 🔒 Install fail2ban (chống brute-force)
- 🔒 Setup UFW firewall (chỉ allow port 80, 443, 22)
- 🔒 Install SSL certificate (Let's Encrypt)
- 🔒 Setup log rotation (logrotate)

---

## 📝 Logs

### Application Logs
```bash
# Gunicorn logs
tail -f /home/bitool/webapp/logs/access.log
tail -f /home/bitool/webapp/logs/error.log

# Systemd logs
echo "Bg190597@" | sudo -S journalctl -u bighi-tool -f
```

### Nginx Logs
```bash
echo "Bg190597@" | sudo -S tail -f /var/log/nginx/bighi-tool-access.log
echo "Bg190597@" | sudo -S tail -f /var/log/nginx/bighi-tool-error.log
```

---

## 🎉 Hoàn Thành

Sau khi deploy thành công:

1. ✅ Website accessible tại: **http://14.225.210.195**
2. ✅ Auto-restart khi crash hoặc reboot VPS
3. ✅ Production-ready với Gunicorn (9 workers)
4. ✅ Nginx reverse proxy (performance + security)
5. ✅ All features working:
   - Landing page cho khách chưa đăng nhập
   - Login/Register system
   - Dashboard với real-time stats
   - Collapsible sidebar
   - Notifications panel
   - Settings modal
   - Email validation tools
   - Facebook tools
   - Recent activity với real data

---

## 📞 Hỗ Trợ

Nếu gặp vấn đề, kiểm tra:
1. Service status: `sudo systemctl status bighi-tool`
2. Nginx status: `sudo systemctl status nginx`
3. Application logs: `/home/bitool/webapp/logs/`
4. Nginx logs: `/var/log/nginx/`
5. System logs: `sudo journalctl -u bighi-tool -n 100`

---

**Lưu ý**: Tất cả changes đã được commit locally. Do GitHub authentication issue, cần push manually sau khi fix credentials hoặc deploy trực tiếp từ local backup.

**Created**: 2025-11-21
**Version**: 1.0
**Status**: Ready for Deployment
