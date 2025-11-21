# 🚀 Hướng Dẫn Di Chuyển Code Sang Server Mới

## 📦 **CHUẨN BỊ**

### Bước 1: Tạo file backup hoàn chỉnh
```bash
cd /home/bighitran1905/webapp
tar -czf bighi-tool-backup-$(date +%Y%m%d-%H%M%S).tar.gz \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.git' \
  --exclude='node_modules' \
  --exclude='*.log' \
  .
```

### Bước 2: Backup database riêng
```bash
cp email_tool.db email_tool.db.backup-$(date +%Y%m%d-%H%M%S)
```

---

## 🔄 **PHƯƠNG PHÁP 1: SCP (Recommended)**

### Trên Server Hiện Tại:
```bash
# Tạo backup
cd /home/bighitran1905
tar -czf webapp-full.tar.gz webapp/

# Copy sang server mới
scp -P <PORT> webapp-full.tar.gz <USERNAME>@<NEW_SERVER_IP>:/home/<USERNAME>/
```

### Trên Server Mới:
```bash
# Giải nén
cd /home/<USERNAME>
tar -xzf webapp-full.tar.gz

# Setup
cd webapp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
python3 app.py
```

---

## 🔄 **PHƯƠNG PHÁP 2: RSYNC (Faster)**

### Sync trực tiếp:
```bash
rsync -avz -e "ssh -p <PORT>" \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.git' \
  /home/bighitran1905/webapp/ \
  <USERNAME>@<NEW_SERVER_IP>:/home/<USERNAME>/webapp/
```

---

## 🔄 **PHƯƠNG PHÁP 3: GIT (Clean)**

### Push code lên GitHub:
```bash
cd /home/bighitran1905/webapp
git add .
git commit -m "Prepare for migration"
git push origin main
```

### Pull trên server mới:
```bash
# Trên server mới
git clone https://github.com/bighitranpro/webapptool.git webapp
cd webapp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy database từ server cũ
scp <OLD_SERVER>:/home/bighitran1905/webapp/email_tool.db .
```

---

## 🔄 **PHƯƠNG PHÁP 4: DOCKER (Production)**

### Tạo Dockerfile:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5003

CMD ["python3", "app.py"]
```

### Build và deploy:
```bash
# Build image
docker build -t bighi-tool-mmo .

# Run container
docker run -d -p 5003:5003 \
  -v $(pwd)/email_tool.db:/app/email_tool.db \
  --name bighi-tool \
  bighi-tool-mmo
```

---

## 📊 **CHECKLIST DI CHUYỂN**

### ✅ Trước khi di chuyển:
- [ ] Backup toàn bộ code
- [ ] Backup database riêng
- [ ] Note lại các environment variables
- [ ] Note lại port đang dùng (5003)
- [ ] Export danh sách packages: `pip freeze > requirements.txt`

### ✅ Trên server mới:
- [ ] Install Python 3.9+
- [ ] Install pip
- [ ] Install git (nếu dùng phương pháp 3)
- [ ] Install rsync (nếu dùng phương pháp 2)
- [ ] Mở port 5003 trên firewall

### ✅ Sau khi di chuyển:
- [ ] Kiểm tra file permissions
- [ ] Tạo virtual environment
- [ ] Install dependencies
- [ ] Test database connection
- [ ] Run migration script nếu cần
- [ ] Start server
- [ ] Test các API endpoints
- [ ] Kiểm tra public URL

---

## 🛠️ **SETUP TRÊN SERVER MỚI**

### 1. Install Dependencies:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git rsync

# CentOS/RHEL
sudo yum install -y python3 python3-pip git rsync
```

### 2. Setup Virtual Environment:
```bash
cd /path/to/webapp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Firewall:
```bash
# Ubuntu/Debian
sudo ufw allow 5003/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=5003/tcp
sudo firewall-cmd --reload
```

### 4. Setup Systemd Service (Production):
```bash
sudo nano /etc/systemd/system/bighi-tool.service
```

**Content**:
```ini
[Unit]
Description=BI GHI TOOL MMO Flask Application
After=network.target

[Service]
Type=simple
User=<USERNAME>
WorkingDirectory=/home/<USERNAME>/webapp
Environment="PATH=/home/<USERNAME>/webapp/venv/bin"
ExecStart=/home/<USERNAME>/webapp/venv/bin/python /home/<USERNAME>/webapp/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable service**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable bighi-tool
sudo systemctl start bighi-tool
sudo systemctl status bighi-tool
```

---

## 🔍 **VERIFICATION**

### Check API Health:
```bash
curl http://localhost:5003/api/health | python3 -m json.tool
```

### Check Landing Page:
```bash
curl http://localhost:5003/ | grep "<title>"
```

### Check Dashboard Stats:
```bash
curl http://localhost:5003/api/dashboard/stats | python3 -m json.tool
```

### Check Database:
```bash
sqlite3 email_tool.db "SELECT COUNT(*) FROM validation_results;"
```

---

## 🚨 **TROUBLESHOOTING**

### Port Already in Use:
```bash
# Find process using port 5003
lsof -i :5003
# Or
netstat -tuln | grep 5003

# Kill process
kill -9 <PID>
```

### Permission Denied:
```bash
# Fix file permissions
chmod +x app.py
chmod 644 email_tool.db
chmod -R 755 templates/ static/
```

### Database Locked:
```bash
# Stop all processes using database
pkill -f "python.*app.py"

# Check database integrity
sqlite3 email_tool.db "PRAGMA integrity_check;"
```

### Module Not Found:
```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

---

## 📝 **MIGRATION SCRIPT**

Tạo file `migrate.sh`:
```bash
#!/bin/bash

# Configuration
NEW_SERVER="<USERNAME>@<SERVER_IP>"
NEW_PATH="/home/<USERNAME>/webapp"
PORT="22"

echo "🚀 Starting migration..."

# 1. Create backup
echo "📦 Creating backup..."
tar -czf webapp-backup.tar.gz \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  webapp/

# 2. Copy to new server
echo "🔄 Copying to new server..."
scp -P $PORT webapp-backup.tar.gz $NEW_SERVER:~/

# 3. Setup on new server
echo "⚙️ Setting up on new server..."
ssh -p $PORT $NEW_SERVER << 'EOF'
  cd ~
  tar -xzf webapp-backup.tar.gz
  cd webapp
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  echo "✅ Setup complete!"
EOF

echo "✅ Migration complete!"
echo "Next steps:"
echo "1. SSH to new server: ssh -p $PORT $NEW_SERVER"
echo "2. Start app: cd webapp && source venv/bin/activate && python3 app.py"
```

**Run**:
```bash
chmod +x migrate.sh
./migrate.sh
```

---

## 🔐 **SECURITY CHECKLIST**

### ✅ Sau khi di chuyển:
- [ ] Đổi password database (nếu có)
- [ ] Regenerate API keys
- [ ] Update admin password
- [ ] Setup SSL certificate (HTTPS)
- [ ] Configure firewall rules
- [ ] Enable fail2ban
- [ ] Setup log rotation
- [ ] Enable automatic backups

---

## 📊 **ESTIMATED TIME**

| Method | Size | Time | Complexity |
|--------|------|------|------------|
| SCP | ~5MB | 1-2 min | Easy |
| Rsync | ~5MB | 30 sec | Easy |
| Git | ~5MB | 2-3 min | Medium |
| Docker | ~200MB | 5-10 min | Advanced |

---

## 💡 **RECOMMENDED APPROACH**

**For Quick Migration**: Use **Rsync** (Phương pháp 2)
**For Clean Setup**: Use **Git** (Phương pháp 3)
**For Production**: Use **Docker** + **Systemd** (Phương pháp 4)

---

## 📞 **NEED HELP?**

Provide these details:
1. New server IP/hostname
2. SSH username
3. SSH port (default: 22)
4. Target directory path
5. Python version on new server

I'll create a custom migration script for you!
