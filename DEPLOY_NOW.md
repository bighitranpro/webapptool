# 🚀 TRIỂN KHAI NGAY - QUICK START

## ⚡ Lệnh Duy Nhất (KHUYẾN NGHỊ)

```bash
cd /home/bighitran1905/webapp && ./deploy_with_password.sh
```

**Thời gian**: 5-10 phút  
**Kết quả**: Website chạy tại http://14.225.210.195

---

## 📋 Thông Tin VPS

```
IP:       14.225.210.195
User:     biproduction
Password: Bg190597@
Port:     22
OS:       Ubuntu 22.04 x64
```

---

## ✅ Script Sẽ Tự Động:

1. ✅ Install sshpass
2. ✅ Create backup (tar.gz)
3. ✅ Upload to VPS
4. ✅ Install Python, Nginx, Gunicorn
5. ✅ Setup systemd service
6. ✅ Configure Nginx reverse proxy
7. ✅ Start application
8. ✅ Test all endpoints

---

## 🧪 Kiểm Tra Sau Deploy

### Từ Trình Duyệt:
- http://14.225.210.195/ (Landing page)
- http://14.225.210.195/login (Login)
- http://14.225.210.195/register (Register)
- http://14.225.210.195/dashboard (Dashboard - cần login)

### Từ Command Line:
```bash
# Test landing page
curl -I http://14.225.210.195/

# Test API
curl http://14.225.210.195/api/health

# Test dashboard stats
curl http://14.225.210.195/api/dashboard/stats
```

---

## 🔧 Quản Lý Services (Trên VPS)

```bash
# SSH vào VPS
sshpass -p "Bg190597@" ssh biproduction@14.225.210.195

# Kiểm tra status
echo "Bg190597@" | sudo -S systemctl status bighi-tool
echo "Bg190597@" | sudo -S systemctl status nginx

# Restart services
echo "Bg190597@" | sudo -S systemctl restart bighi-tool
echo "Bg190597@" | sudo -S systemctl restart nginx

# Xem logs
tail -f /home/bitool/webapp/logs/error.log
echo "Bg190597@" | sudo -S tail -f /var/log/nginx/bighi-tool-error.log
```

---

## 🚨 Nếu Lỗi

### Script Fail → Chạy Thủ Công

Xem chi tiết trong **DEPLOYMENT_GUIDE.md** (Phương Án 2)

### Connection Refused → Fix Firewall

```bash
# SSH vào VPS
sshpass -p "Bg190597@" ssh biproduction@14.225.210.195

# Allow port 80
echo "Bg190597@" | sudo -S ufw allow 80/tcp
echo "Bg190597@" | sudo -S ufw status
```

### 502 Bad Gateway → Restart Services

```bash
echo "Bg190597@" | sudo -S systemctl restart bighi-tool
echo "Bg190597@" | sudo -S systemctl restart nginx
```

---

## 📊 Hiệu Năng Mong Đợi

- **Workers**: 9 (Gunicorn multi-process)
- **Requests/sec**: 500+
- **Response Time**: < 100ms (static), < 500ms (API)
- **Uptime**: 99.9% (auto-restart)

---

## 🎯 Features Đã Deploy

✅ Landing page (khách chưa đăng nhập)  
✅ Login/Register system  
✅ Dashboard với real-time stats  
✅ Collapsible sidebar  
✅ Notifications panel  
✅ Settings modal (4 tabs)  
✅ Email validation tools  
✅ Facebook tools  
✅ Recent activity với real data  
✅ VIP packages info  
✅ Usage notes & quick guide  

---

## 🔗 Tài Liệu Chi Tiết

- **DEPLOYMENT_GUIDE.md** - Hướng dẫn đầy đủ
- **README.md** - Project overview
- **TESTING_GUIDE.md** - Testing instructions

---

**Ready to Deploy? Run:**
```bash
./deploy_with_password.sh
```

**Created**: 2025-11-21  
**Status**: ✅ Ready
