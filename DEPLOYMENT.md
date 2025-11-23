# 🚀 BiTool Deployment Guide

## Hướng Dẫn Deploy Ứng Dụng BiTool lên Server Production

---

## 📋 Yêu Cầu Hệ Thống

### Server Requirements:
- **OS**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **Python**: 3.10 hoặc mới hơn
- **RAM**: Tối thiểu 2GB (Khuyến nghị 4GB+)
- **CPU**: 2 cores trở lên
- **Storage**: 10GB trở lên
- **Port**: 5003 (hoặc port tùy chỉnh)

### Software Requirements:
- Python 3.10+
- pip3
- git
- systemd
- gunicorn

---

## 🔧 Cài Đặt Bước 1: Chuẩn Bị Server

### 1.1. Update hệ thống
```bash
sudo apt update && sudo apt upgrade -y
```

### 1.2. Cài đặt Python và dependencies
```bash
sudo apt install -y python3 python3-pip python3-venv git
```

### 1.3. Tạo user cho application (khuyến nghị)
```bash
sudo useradd -m -s /bin/bash bitool
sudo usermod -aG sudo bitool
```

---

## 📦 Bước 2: Clone và Cài Đặt Application

### 2.1. Clone repository
```bash
cd /home/root  # hoặc /home/bitool
git clone https://github.com/bighitranpro/webapptool.git webapp
cd webapp
```

### 2.2. Tạo Python virtual environment (khuyến nghị)
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2.3. Cài đặt dependencies
```bash
pip3 install -r requirements.txt
```

### 2.4. Tạo file .env từ template
```bash
cp .env.example .env
nano .env  # Chỉnh sửa các biến môi trường
```

### Các biến quan trọng trong .env:
```env
SECRET_KEY=your-secret-key-here-change-this
PORT=5003
DEBUG=False
```

---

## ⚙️ Bước 3: Cấu Hình Gunicorn

File `gunicorn_config.py` đã được cấu hình sẵn với:
- **Workers**: Tự động = CPU cores * 2 + 1
- **Worker Class**: gevent (async)
- **Timeout**: 120 seconds
- **Logging**: Lưu vào `logs/` directory

Kiểm tra cấu hình:
```bash
cat gunicorn_config.py
```

---

## 🔄 Bước 4: Thiết Lập Systemd Service

### 4.1. Copy service file
```bash
sudo cp bitool.service /etc/systemd/system/
```

### 4.2. Reload systemd và enable service
```bash
sudo systemctl daemon-reload
sudo systemctl enable bitool
```

### 4.3. Khởi động service
```bash
sudo systemctl start bitool
```

### 4.4. Kiểm tra trạng thái
```bash
sudo systemctl status bitool
```

---

## 📊 Bước 5: Kiểm Tra và Monitor

### 5.1. Xem logs
```bash
# Xem error logs
tail -f logs/error.log

# Xem access logs
tail -f logs/access.log

# Xem systemd logs
sudo journalctl -u bitool -f
```

### 5.2. Test ứng dụng
```bash
curl http://localhost:5003/
```

### 5.3. Kiểm tra workers
```bash
ps aux | grep gunicorn
```

---

## 🛠️ Quản Lý Service

### Khởi động lại service
```bash
sudo systemctl restart bitool
```

### Dừng service
```bash
sudo systemctl stop bitool
```

### Reload configuration (không downtime)
```bash
sudo systemctl reload bitool
```

### Disable auto-start
```bash
sudo systemctl disable bitool
```

### Xem logs real-time
```bash
sudo journalctl -u bitool -f --no-pager
```

---

## 🔥 Troubleshooting

### Lỗi: Service không khởi động
```bash
# Kiểm tra logs
sudo journalctl -u bitool -n 50

# Kiểm tra file cấu hình
gunicorn --config gunicorn_config.py app:app --check-config
```

### Lỗi: Port đã được sử dụng
```bash
# Tìm process đang dùng port
sudo lsof -i :5003

# Kill process
sudo kill -9 <PID>
```

### Lỗi: Permission denied
```bash
# Chỉnh quyền
sudo chown -R root:root /home/root/webapp
sudo chmod -R 755 /home/root/webapp
```

### Lỗi: Module not found
```bash
# Cài lại dependencies
pip3 install -r requirements.txt --force-reinstall
```

---

## 🔐 Security Best Practices

### 1. Thay đổi SECRET_KEY
```bash
# Generate new secret key
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Firewall configuration
```bash
# Allow port 5003
sudo ufw allow 5003/tcp

# Enable firewall
sudo ufw enable
```

### 3. Không expose port ra internet trực tiếp
- Sử dụng Nginx reverse proxy
- Cài đặt SSL/HTTPS với Let's Encrypt

### 4. Regular updates
```bash
cd /home/root/webapp
git pull
pip3 install -r requirements.txt --upgrade
sudo systemctl restart bitool
```

---

## 📈 Performance Tuning

### 1. Tăng số workers
Edit `gunicorn_config.py`:
```python
workers = 16  # Tùy chỉnh số workers
```

### 2. Thay đổi worker class
```python
worker_class = "gevent"  # hoặc "sync", "eventlet"
```

### 3. Tăng timeout cho requests dài
```python
timeout = 300  # 5 phút
```

---

## 🌐 Nginx Reverse Proxy (Optional)

### Cài đặt Nginx
```bash
sudo apt install -y nginx
```

### Cấu hình
```bash
sudo nano /etc/nginx/sites-available/bitool
```

Nội dung:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/bitool /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔒 SSL/HTTPS với Let's Encrypt (Optional)

```bash
# Cài đặt certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal test
sudo certbot renew --dry-run
```

---

## 📊 Monitoring và Logging

### Setup logrotate
```bash
sudo nano /etc/logrotate.d/bitool
```

Nội dung:
```
/home/root/webapp/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        systemctl reload bitool > /dev/null 2>&1 || true
    endscript
}
```

---

## 🎯 Quick Commands Cheat Sheet

```bash
# Khởi động
sudo systemctl start bitool

# Dừng
sudo systemctl stop bitool

# Restart
sudo systemctl restart bitool

# Status
sudo systemctl status bitool

# Logs
tail -f logs/error.log

# Workers
ps aux | grep gunicorn

# Kill all
pkill -9 gunicorn
```

---

## 📝 Thông Tin Hỗ Trợ

- **GitHub**: https://github.com/bighitranpro/webapptool
- **Port**: 5003
- **Service Name**: bitool
- **Log Location**: `/home/root/webapp/logs/`
- **Config File**: `gunicorn_config.py`

---

## ✅ Checklist Deployment

- [ ] Server đã chuẩn bị (Python, pip, git)
- [ ] Code đã clone từ GitHub
- [ ] Dependencies đã cài đặt
- [ ] File .env đã cấu hình
- [ ] Logs directory đã tạo
- [ ] Systemd service đã enable
- [ ] Service đã khởi động
- [ ] Port 5003 đã mở
- [ ] Ứng dụng response OK
- [ ] Logs không có lỗi

---

**Deployment Date**: 2025-11-23  
**Version**: 2.0.0  
**Status**: Production Ready ✅
