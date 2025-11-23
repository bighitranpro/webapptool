# 🚀 HƯỚNG DẪN DEPLOY HOÀN CHỈNH

## 📋 MỤC LỤC

1. [Kiểm tra hệ thống](#kiểm-tra-hệ-thống)
2. [Cập nhật code mới nhất](#cập-nhật-code)
3. [Cài đặt dependencies](#cài-đặt-dependencies)
4. [Migration database](#migration-database)
5. [Khởi động service](#khởi-động-service)
6. [Test & Verify](#test-verify)
7. [Troubleshooting](#troubleshooting)

---

## ✅ KIỂM TRA HỆ THỐNG

### 1. Kiểm tra phiên bản Python
```bash
python3 --version
# Expected: Python 3.10 or higher
```

### 2. Kiểm tra disk space
```bash
df -h /home/root/webapp
# Cần ít nhất 1GB trống
```

### 3. Kiểm tra port
```bash
sudo lsof -i :5003
# Nếu có process đang chạy, kill nó:
# sudo kill -9 <PID>
```

---

## 📥 CẬP NHẬT CODE

### Option 1: Git Pull (Recommended)
```bash
cd /home/root/webapp
git status
git stash  # Nếu có thay đổi local
git pull origin main
git stash pop  # Nếu đã stash
```

### Option 2: Fresh Clone
```bash
cd /home/root
mv webapp webapp_backup_$(date +%Y%m%d)
git clone <repository-url> webapp
cd webapp
```

---

## 📦 CÀI ĐẶT DEPENDENCIES

### 1. Update pip
```bash
cd /home/root/webapp
python3 -m pip install --upgrade pip
```

### 2. Install requirements
```bash
pip3 install -r requirements.txt
```

### 3. Verify installation
```bash
pip3 list | grep -E "Flask|Werkzeug|dnspython|socketio"
```

Expected output:
```
Flask                3.1.2
Werkzeug             3.1.3
dnspython            2.4.2
flask-socketio       5.3.5
python-socketio      5.10.0
```

---

## 🗄️ MIGRATION DATABASE

### 1. Backup database hiện tại
```bash
cd /home/root/webapp
cp email_tool.db email_tool_backup_$(date +%Y%m%d_%H%M%S).db
```

### 2. Run migrations
```bash
# Migration settings (nếu chưa chạy)
python3 migrations/001_add_system_settings.py

# Verify migration
sqlite3 email_tool.db "PRAGMA table_info(system_settings);" | head -10
```

### 3. Check database integrity
```bash
sqlite3 email_tool.db "PRAGMA integrity_check;"
# Expected: ok
```

---

## 🚀 KHỞI ĐỘNG SERVICE

### Option 1: Manual Start (Development)
```bash
cd /home/root/webapp
python3 app.py
```

### Option 2: Background Process
```bash
cd /home/root/webapp
nohup python3 app.py > app.log 2>&1 &
echo $! > app.pid
```

### Option 3: Systemd Service (Production)
```bash
sudo systemctl start email-tool
sudo systemctl status email-tool
sudo systemctl enable email-tool  # Auto-start on boot
```

#### Create systemd service file (if not exists):
```bash
sudo nano /etc/systemd/system/email-tool.service
```

Content:
```ini
[Unit]
Description=BI GHI Tool MMO - Email Tool Suite
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/root/webapp
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /home/root/webapp/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl start email-tool
sudo systemctl enable email-tool
```

---

## ✅ TEST & VERIFY

### 1. Check if app is running
```bash
ps aux | grep "python3 app.py"
```

### 2. Test health endpoint
```bash
curl http://localhost:5003/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "2.2.0",
  "database": {
    "healthy": true,
    "stats": {...}
  },
  "modules": {...}
}
```

### 3. Test homepage
```bash
curl -I http://localhost:5003/
# Expected: HTTP/1.1 200 OK
```

### 4. Test dashboard
```bash
curl -I http://localhost:5003/dashboard
# Expected: HTTP/1.1 200 OK or 302 (redirect)
```

### 5. Check logs
```bash
# If using nohup
tail -f /home/root/webapp/app.log

# If using systemd
sudo journalctl -u email-tool -f

# If manual
# Check terminal output
```

---

## 🌐 EXTERNAL ACCESS

### Get service URL (if using sandbox)
```bash
# For port 5003
curl https://api.e2b.dev/ports/5003
```

### Configure reverse proxy (if needed)
```bash
# Nginx example
sudo nano /etc/nginx/sites-available/email-tool

# Add:
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5003;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/email-tool /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔧 TROUBLESHOOTING

### Issue 1: Port already in use
```bash
# Find process
sudo lsof -i :5003

# Kill process
sudo kill -9 <PID>

# Or change port in app.py
# Edit line: port = 5003
```

### Issue 2: Module not found
```bash
# Reinstall dependencies
pip3 install -r requirements.txt --force-reinstall

# Check Python path
python3 -c "import sys; print('\n'.join(sys.path))"
```

### Issue 3: Database locked
```bash
# Stop all processes accessing DB
pkill -f "python3 app.py"

# Check for locks
fuser email_tool.db

# If stuck, restart
sqlite3 email_tool.db "PRAGMA wal_checkpoint(TRUNCATE);"
```

### Issue 4: Permission denied
```bash
# Fix ownership
sudo chown -R root:root /home/root/webapp

# Fix permissions
chmod +x app.py
chmod -R 755 /home/root/webapp
```

### Issue 5: Import errors
```bash
# Check if all modules exist
python3 -c "
from routes import auth_bp, api_bp, dashboard_bp
from app_admin_routes import admin_bp
from routes.settings_routes import settings_bp
print('All imports successful')
"
```

### Issue 6: Static files not loading
```bash
# Check static directory
ls -la static/css/
ls -la static/js/

# Verify Flask can access
python3 -c "
from flask import Flask
app = Flask(__name__)
print(app.static_folder)
"
```

---

## 📊 MONITORING

### Check app status
```bash
# CPU & Memory usage
ps aux | grep python3

# Detailed stats
top -p $(pgrep -f "python3 app.py")
```

### View logs in real-time
```bash
# Systemd
sudo journalctl -u email-tool -f

# Manual/nohup
tail -f app.log

# Last 100 lines
tail -100 app.log
```

### Check database size
```bash
du -h email_tool.db
sqlite3 email_tool.db "SELECT COUNT(*) FROM validation_results;"
```

---

## 🔄 UPDATE WORKFLOW

### Regular updates:
```bash
# 1. Pull latest code
cd /home/root/webapp
git pull origin main

# 2. Install new dependencies (if any)
pip3 install -r requirements.txt

# 3. Run migrations (if any)
python3 migrations/*.py

# 4. Restart service
sudo systemctl restart email-tool

# 5. Verify
curl http://localhost:5003/api/health
```

### Rollback (if needed):
```bash
# 1. Stop service
sudo systemctl stop email-tool

# 2. Restore backup
cd /home/root/webapp
git checkout <previous-commit-hash>

# 3. Restore database
cp email_tool_backup_YYYYMMDD.db email_tool.db

# 4. Restart
sudo systemctl start email-tool
```

---

## ✅ CHECKLIST DEPLOY

- [ ] Code updated (git pull)
- [ ] Dependencies installed
- [ ] Database migrated
- [ ] Database backed up
- [ ] Service started
- [ ] Health check passed
- [ ] Homepage accessible
- [ ] Dashboard accessible
- [ ] All APIs working
- [ ] Mobile responsive tested
- [ ] Logs monitoring set up
- [ ] Backup scheduled

---

## 📞 SUPPORT

### Logs location:
- App logs: `/home/root/webapp/app.log`
- System logs: `journalctl -u email-tool`
- Error logs: Check terminal/systemd

### Common commands:
```bash
# Start
sudo systemctl start email-tool

# Stop
sudo systemctl stop email-tool

# Restart
sudo systemctl restart email-tool

# Status
sudo systemctl status email-tool

# Logs
sudo journalctl -u email-tool -n 100

# Enable auto-start
sudo systemctl enable email-tool
```

---

## 🎉 SUCCESS INDICATORS

✅ App running on port 5003  
✅ Health endpoint returns {"status": "healthy"}  
✅ Homepage loads without errors  
✅ Dashboard accessible  
✅ All tools functional  
✅ Mobile responsive  
✅ No errors in logs  
✅ Database queries fast (<100ms)  

---

**Deploy completed successfully! 🚀**

*Last updated: 2024-11-23*  
*Version: 2.2.0*
