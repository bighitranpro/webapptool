# 🚀 Di Chuyển Code Sang Server Mới - Hướng Dẫn Nhanh

## ⚡ **CÁCH NHANH NHẤT (Tự Động)**

### Bước 1: Chạy script tự động
```bash
cd /home/bighitran1905/webapp
./auto_migrate.sh
```

Script sẽ hỏi:
- 🖥️  IP/Hostname server mới
- 👤 Username SSH
- 🔢 Port SSH (mặc định 22)
- 📁 Đường dẫn deploy

Script sẽ tự động:
- ✅ Tạo backup
- ✅ Upload lên server mới
- ✅ Giải nén
- ✅ Setup Python venv
- ✅ Install dependencies
- ✅ Tạo systemd service (optional)

---

## 📝 **CÁCH THỦ CÔNG (3 Phút)**

### **Phương pháp 1: SCP (Đơn giản nhất)**

#### Trên server hiện tại:
```bash
# 1. Tạo backup
cd /home/bighitran1905
tar -czf webapp.tar.gz webapp/

# 2. Copy sang server mới
scp -P <PORT> webapp.tar.gz <USER>@<NEW_IP>:~/
```

#### Trên server mới:
```bash
# 1. Giải nén
tar -xzf webapp.tar.gz
cd webapp

# 2. Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Run
python3 app.py
```

---

### **Phương pháp 2: Git (Sạch nhất)**

#### Trên server hiện tại:
```bash
cd /home/bighitran1905/webapp

# Push code lên GitHub
git add .
git commit -m "Ready for migration"
git push origin main

# Backup database riêng
scp email_tool.db <USER>@<NEW_IP>:/path/to/webapp/
```

#### Trên server mới:
```bash
# Clone repository
git clone https://github.com/bighitranpro/webapptool.git webapp
cd webapp

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy database đã backup
# (email_tool.db đã copy ở trên)

# Run
python3 app.py
```

---

### **Phương pháp 3: Rsync (Nhanh nhất)**

```bash
rsync -avz -e "ssh -p <PORT>" \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.git' \
  /home/bighitran1905/webapp/ \
  <USER>@<NEW_IP>:/path/to/webapp/
```

Sau đó SSH vào server mới và setup như phương pháp 1.

---

## 🔧 **SETUP TRÊN SERVER MỚI**

### 1. Install Python & Dependencies:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

# CentOS/RHEL
sudo yum install -y python3 python3-pip git
```

### 2. Mở Port:
```bash
# Ubuntu/Debian
sudo ufw allow 5003/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=5003/tcp
sudo firewall-cmd --reload
```

### 3. Setup Virtual Environment:
```bash
cd /path/to/webapp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Test:
```bash
python3 app.py
```

Mở trình duyệt: `http://<NEW_SERVER_IP>:5003`

---

## 🎯 **SETUP PRODUCTION (Systemd Service)**

### Tạo file service:
```bash
sudo nano /etc/systemd/system/bighi-tool.service
```

### Content:
```ini
[Unit]
Description=BI GHI TOOL MMO
After=network.target

[Service]
Type=simple
User=<YOUR_USERNAME>
WorkingDirectory=/path/to/webapp
Environment="PATH=/path/to/webapp/venv/bin"
ExecStart=/path/to/webapp/venv/bin/python /path/to/webapp/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Enable & Start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable bighi-tool
sudo systemctl start bighi-tool
sudo systemctl status bighi-tool
```

---

## ✅ **VERIFICATION CHECKLIST**

Sau khi di chuyển, kiểm tra:

```bash
# 1. API Health
curl http://localhost:5003/api/health

# 2. Landing Page
curl http://localhost:5003/ | grep "<title>"

# 3. Dashboard Stats
curl http://localhost:5003/api/dashboard/stats

# 4. Database
cd /path/to/webapp
sqlite3 email_tool.db "SELECT COUNT(*) FROM validation_results;"
```

Kết quả mong đợi:
- ✅ API health: `"status": "healthy"`
- ✅ Landing page title: `BI GHI TOOL MMO`
- ✅ Stats: `"live_emails": 4360`
- ✅ Database: `4364`

---

## 🔍 **TROUBLESHOOTING**

### Port bị chiếm:
```bash
sudo lsof -i :5003
sudo kill -9 <PID>
```

### Permission denied:
```bash
chmod +x app.py
chmod -R 755 templates/ static/
```

### Module not found:
```bash
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

### Database locked:
```bash
pkill -f "python.*app.py"
sqlite3 email_tool.db "PRAGMA integrity_check;"
```

---

## 📊 **THÔNG TIN DỰ KIẾN**

| Item | Size | Note |
|------|------|------|
| Code (no venv) | ~5 MB | Nén ~2 MB |
| Database | 2.9 MB | email_tool.db |
| Total backup | ~8 MB | Compressed ~3-4 MB |

**Thời gian**:
- Backup: ~10 giây
- Upload (1 Mbps): ~30 giây
- Setup: ~1-2 phút
- **Total**: ~3-4 phút

---

## 💡 **KHUYẾN NGHỊ**

**Cho người mới**: Dùng **Auto Script** (`./auto_migrate.sh`)

**Cho người quen Linux**: Dùng **Rsync** (nhanh nhất)

**Cho production**: Dùng **Git + Systemd**

**Cho Docker**: Xem `MIGRATION_GUIDE.md` phần Docker

---

## 📞 **CẦN HELP?**

Nếu gặp vấn đề, cung cấp:
1. ✅ Server mới: IP, username, port
2. ✅ Output lỗi (nếu có)
3. ✅ Phương pháp đang dùng
4. ✅ OS server mới (Ubuntu/CentOS/etc)

---

## 🎉 **SAU KHI DI CHUYỂN XONG**

Website sẽ accessible tại:
```
http://<NEW_SERVER_IP>:5003
```

Tất cả features sẽ hoạt động:
- ✅ Landing page
- ✅ Login/Register
- ✅ Dashboard với real-time stats
- ✅ Collapsible sidebar
- ✅ Notifications panel
- ✅ Settings modal
- ✅ All 13 tools

---

**Good luck with migration!** 🚀
