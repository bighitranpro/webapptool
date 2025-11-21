# 🚀 Deploy BI GHI TOOL MMO lên Ubuntu Server

## 📊 **THÔNG TIN SERVER MỚI**

```
Server:    bitool-lpti
IP:        14.225.210.195
OS:        Ubuntu Server 22.04 x64
Username:  root (hoặc user khác)
```

---

## 🎯 **KIẾN TRÚC MỚI (NÂNG CẤP)**

### **Từ**: Flask Development Server
```
Flask (port 5003) → Chậm, không production-ready
```

### **Sang**: Production Stack (Miễn phí 100%)
```
Internet → Nginx (port 80) → Gunicorn → Flask App
          ↑                    ↑
      Reverse Proxy      Production WSGI Server
```

### **Lợi ích**:
- ✅ **Nhanh hơn 10x**: Gunicorn với multi-workers
- ✅ **Ổn định**: Auto-restart khi crash
- ✅ **An toàn**: Nginx handle security, static files
- ✅ **Production-ready**: Systemd service management
- ✅ **Miễn phí**: Không tốn chi phí

---

## ⚡ **DEPLOY TỰ ĐỘNG (1 LỆNH)**

### **Bước 1: Chỉnh sửa thông tin (nếu cần)**

Mở file `deploy_to_ubuntu.sh` và kiểm tra:
```bash
nano deploy_to_ubuntu.sh
```

Đảm bảo thông tin đúng:
```bash
NEW_SERVER="14.225.210.195"
SSH_USER="root"          # Đổi nếu dùng user khác
SSH_PORT="22"
APP_DIR="/home/bitool/webapp"
```

### **Bước 2: Chạy script**

```bash
cd /home/bighitran1905/webapp
./deploy_to_ubuntu.sh
```

Script sẽ tự động:
1. ✅ Tạo backup
2. ✅ Upload lên server
3. ✅ Install: Python, Nginx, Gunicorn
4. ✅ Setup virtual environment
5. ✅ Install dependencies
6. ✅ Configure Nginx reverse proxy
7. ✅ Create systemd service
8. ✅ Start services
9. ✅ Test endpoints

**Thời gian**: ~5 phút

---

## 🔧 **SAU KHI DEPLOY**

### **Truy cập ứng dụng**:
```
http://14.225.210.195
```

**Không cần thêm :5003 nữa!** Nginx đã proxy port 80 → 5003

### **Kiểm tra status**:
```bash
ssh root@14.225.210.195

# Check app
sudo systemctl status bighi-tool

# Check nginx
sudo systemctl status nginx

# View logs
sudo journalctl -u bighi-tool -f
```

### **Quản lý service**:
```bash
# Restart
sudo systemctl restart bighi-tool

# Stop
sudo systemctl stop bighi-tool

# Start
sudo systemctl start bighi-tool

# Enable auto-start
sudo systemctl enable bighi-tool
```

---

## 📊 **SO SÁNH HIỆU SUẤT**

| Metric | Flask Dev | Gunicorn + Nginx |
|--------|-----------|------------------|
| Workers | 1 | 9 (CPU * 2 + 1) |
| Requests/sec | ~50 | ~500+ |
| Concurrent | 1 | 1000+ |
| Auto-restart | ❌ | ✅ |
| Production | ❌ | ✅ |
| Static files | Slow | Fast (Nginx) |
| Security | Basic | Advanced |

---

## 🔍 **KIỂM TRA HOẠT ĐỘNG**

### **1. Test API Health**:
```bash
curl http://14.225.210.195/api/health
```

Expected:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "database": {
    "healthy": true
  }
}
```

### **2. Test Landing Page**:
```bash
curl http://14.225.210.195/ | grep "<title>"
```

Expected:
```html
<title>BI GHI TOOL MMO - Professional Email & Facebook Tools Suite</title>
```

### **3. Test Dashboard Stats**:
```bash
curl http://14.225.210.195/api/dashboard/stats
```

Expected:
```json
{
  "success": true,
  "stats": {
    "live_emails": 4360,
    "die_emails": 4
  }
}
```

---

## 🛠️ **CẤU HÌNH CHI TIẾT**

### **Gunicorn Configuration**:
File: `/home/bitool/webapp/gunicorn_config.py`

```python
bind = "0.0.0.0:5003"
workers = 9  # CPU * 2 + 1
worker_class = "sync"
timeout = 30
```

### **Nginx Configuration**:
File: `/etc/nginx/sites-available/bighi-tool`

```nginx
server {
    listen 80;
    server_name 14.225.210.195;
    
    location / {
        proxy_pass http://127.0.0.1:5003;
        # ... headers
    }
    
    location /static {
        alias /home/bitool/webapp/static;
        expires 30d;
    }
}
```

### **Systemd Service**:
File: `/etc/systemd/system/bighi-tool.service`

```ini
[Service]
ExecStart=/home/bitool/webapp/venv/bin/gunicorn \
    --config gunicorn_config.py \
    wsgi:app
Restart=always
```

---

## 📁 **CẤU TRÚC THỦ MỤC**

```
/home/bitool/webapp/
├── app.py                 # Main Flask app
├── wsgi.py               # Gunicorn entry point (NEW)
├── gunicorn_config.py    # Gunicorn config (NEW)
├── requirements.txt      # Dependencies
├── email_tool.db         # Database
├── routes/               # Modular routes
│   ├── auth_routes.py
│   ├── api_routes.py
│   └── dashboard_routes.py
├── templates/            # HTML templates
├── static/              # CSS, JS
├── modules/             # Email tools
├── logs/                # Application logs (NEW)
│   ├── access.log
│   └── error.log
└── venv/                # Virtual environment
```

---

## 🚨 **TROUBLESHOOTING**

### **Service không start**:
```bash
# Check logs
sudo journalctl -u bighi-tool -n 50

# Check Gunicorn directly
cd /home/bitool/webapp
source venv/bin/activate
gunicorn --config gunicorn_config.py wsgi:app
```

### **Nginx error**:
```bash
# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Test config
sudo nginx -t

# Restart
sudo systemctl restart nginx
```

### **Port 80 bị chiếm**:
```bash
# Check what's using port 80
sudo lsof -i :80
sudo netstat -tuln | grep :80

# Kill if needed
sudo systemctl stop apache2  # If Apache running
```

### **Database locked**:
```bash
# Kill old processes
sudo pkill -f "python.*app.py"
sudo pkill -f gunicorn

# Restart service
sudo systemctl restart bighi-tool
```

### **Permission denied**:
```bash
# Fix permissions
cd /home/bitool/webapp
sudo chown -R root:root .
sudo chmod -R 755 .
sudo chmod 644 email_tool.db
```

---

## 🔐 **BẢO MẬT (KHUYẾN NGHỊ)**

### **1. Setup SSL/HTTPS (Let's Encrypt - Miễn phí)**:
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate (cần domain name)
sudo certbot --nginx -d yourdomain.com

# Auto-renew
sudo certbot renew --dry-run
```

### **2. Setup Firewall**:
```bash
# Enable UFW
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS (if SSL)
sudo ufw enable
```

### **3. Disable SSH Password** (dùng SSH key):
```bash
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart sshd
```

---

## 📊 **MONITORING (Optional)**

### **Setup log rotation**:
```bash
sudo nano /etc/logrotate.d/bighi-tool
```

```
/home/bitool/webapp/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### **Monitor resources**:
```bash
# CPU, Memory usage
htop

# Disk usage
df -h

# Check processes
ps aux | grep gunicorn
```

---

## 🎯 **PERFORMANCE TUNING**

### **Tăng số workers** (nếu server mạnh):
```bash
nano /home/bitool/webapp/gunicorn_config.py
# Tăng: workers = 16
sudo systemctl restart bighi-tool
```

### **Enable Nginx caching**:
```nginx
# Add to Nginx config
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m;
proxy_cache my_cache;
proxy_cache_valid 200 10m;
```

---

## ✅ **CHECKLIST HOÀN THÀNH**

Sau khi deploy, kiểm tra:

- [ ] ✅ Service running: `systemctl status bighi-tool`
- [ ] ✅ Nginx running: `systemctl status nginx`
- [ ] ✅ Landing page: http://14.225.210.195/
- [ ] ✅ API health: http://14.225.210.195/api/health
- [ ] ✅ Dashboard: http://14.225.210.195/dashboard
- [ ] ✅ Login works: admin/admin123
- [ ] ✅ Database connected: 4364 emails
- [ ] ✅ Real-time stats: 99.91% success
- [ ] ✅ All features working

---

## 📞 **HỖ TRỢ**

### **Logs quan trọng**:
```bash
# Application logs
sudo journalctl -u bighi-tool -f

# Nginx access
sudo tail -f /var/log/nginx/access.log

# Nginx error
sudo tail -f /var/log/nginx/error.log

# Gunicorn logs
sudo tail -f /home/bitool/webapp/logs/access.log
sudo tail -f /home/bitool/webapp/logs/error.log
```

### **Quick commands**:
```bash
# Restart everything
sudo systemctl restart bighi-tool nginx

# Check all services
sudo systemctl status bighi-tool nginx

# View resource usage
htop
df -h
```

---

## 🎉 **KẾT QUẢ MONG ĐỢI**

Sau khi deploy thành công:

**URL**: http://14.225.210.195

**Features**:
- ✅ Landing page với hero section
- ✅ Login/Register
- ✅ Dashboard real-time (99.91% success)
- ✅ Collapsible sidebar
- ✅ Notifications panel
- ✅ Settings modal
- ✅ All 13 tools
- ✅ Database: 4,360 LIVE emails

**Performance**:
- ✅ Gunicorn: 9 workers
- ✅ Nginx: Static file caching
- ✅ Auto-restart: Systemd
- ✅ Logs: Rotating daily

---

**Chúc deploy thành công!** 🚀
