# 🌐 HƯỚNG DẪN TRUY CẬP SERVER TỪ MÁY KHÁC

## ✅ SERVER ĐANG CHẠY

### 📊 Thông tin Server:

```
🖥️  Server IP Public: 35.247.153.179
🔌 Port: 5000
🌐 URL Truy cập: http://35.247.153.179:5000
📁 Log file: /home/bighitran1905/webapp/flask_server.log
```

---

## 🚀 TRẠNG THÁI HIỆN TẠI

✅ **Flask Server đang chạy với nohup**
- Server sẽ KHÔNG TẮT khi đóng SSH
- Server chạy background process
- Log được ghi vào flask_server.log

✅ **Systemd Service đã được cài đặt**
- Tự động start khi server restart
- Service name: email-tool.service
- Auto-restart nếu crash

---

## 💻 TRUY CẬP TỪ MÁY KHÁC

### Cách 1: Truy cập trực tiếp qua IP Public
```
Mở browser trên máy bất kỳ (Windows, Mac, Linux, Mobile)
Vào: http://35.247.153.179:5000

✅ Sẽ thấy Email Tool với 10 chức năng
✅ Hoạt động trên mọi thiết bị có internet
✅ Không cần VPN hay config gì thêm
```

### Cách 2: Truy cập trong cùng mạng LAN
```
Từ máy trong cùng mạng:
http://10.148.0.2:5000
```

---

## 🔧 QUẢN LÝ SERVER

### Kiểm tra Server có đang chạy không:
```bash
# SSH vào server
ssh bighitran1905@35.247.153.179

# Kiểm tra process
ps aux | grep "python app.py"

# Kiểm tra service
sudo systemctl status email-tool.service

# Xem log real-time
tail -f /home/bighitran1905/webapp/flask_server.log

# Test từ server
curl http://localhost:5000
```

### Quản lý bằng Systemd Service:
```bash
# Start service
sudo systemctl start email-tool.service

# Stop service
sudo systemctl stop email-tool.service

# Restart service
sudo systemctl restart email-tool.service

# Check status
sudo systemctl status email-tool.service

# View logs
sudo journalctl -u email-tool.service -f
```

### Quản lý Process hiện tại (nohup):
```bash
# Xem process
ps aux | grep "python app.py"

# Kill process (nếu cần)
pkill -f "python app.py"

# Start lại với nohup
cd /home/bighitran1905/webapp
nohup venv/bin/python app.py > flask_server.log 2>&1 &

# Xem log
tail -f /home/bighitran1905/webapp/flask_server.log
```

---

## 🔄 SAU KHI RESTART SERVER

Server sẽ tự động start Flask app nhờ systemd service!

**Không cần làm gì cả!** Service đã được enable.

Nếu muốn chắc chắn:
```bash
# SSH vào server
ssh bighitran1905@35.247.153.179

# Kiểm tra service
sudo systemctl status email-tool.service

# Nếu chưa chạy, start manual:
sudo systemctl start email-tool.service
```

---

## 📱 TEST TRÊN CÁC THIẾT BỊ

### Desktop (Windows/Mac/Linux):
```
1. Mở Chrome/Firefox/Edge
2. Vào: http://35.247.153.179:5000
3. Test tất cả 10 tools
```

### Mobile (iPhone/Android):
```
1. Mở Safari/Chrome
2. Vào: http://35.247.153.179:5000
3. Giao diện responsive, dùng tốt trên mobile
```

### Tablet (iPad/Android):
```
1. Mở browser
2. Vào: http://35.247.153.179:5000
3. Perfect cho tablet
```

---

## 🔒 BẢO MẬT

### Firewall:
```
✅ UFW: inactive (không chặn port 5000)
✅ Port 5000 mở cho public access
✅ No authentication required
```

### Nếu muốn thêm firewall:
```bash
# Enable UFW
sudo ufw enable

# Allow SSH (QUAN TRỌNG - làm trước!)
sudo ufw allow 22/tcp

# Allow port 5000
sudo ufw allow 5000/tcp

# Check status
sudo ufw status
```

### Nếu muốn hạn chế IP:
```bash
# Chỉ cho phép IP cụ thể
sudo ufw allow from YOUR_IP_ADDRESS to any port 5000

# Ví dụ:
sudo ufw allow from 192.168.1.100 to any port 5000
```

---

## 🐛 TROUBLESHOOTING

### Không truy cập được từ máy khác?

**1. Kiểm tra server có chạy không:**
```bash
curl http://localhost:5000
# Nếu trả về HTML → Server OK
# Nếu lỗi → Server không chạy
```

**2. Kiểm tra process:**
```bash
ps aux | grep "python app.py"
# Nếu thấy process → OK
# Nếu không → Start lại
```

**3. Kiểm tra port:**
```bash
sudo netstat -tulpn | grep 5000
# Phải thấy Python listening trên 0.0.0.0:5000
```

**4. Kiểm tra firewall:**
```bash
sudo ufw status
# Nếu active, phải allow port 5000
```

**5. Kiểm tra logs:**
```bash
tail -50 /home/bighitran1905/webapp/flask_server.log
# Xem có lỗi gì không
```

### Server bị crash?

**Restart bằng systemd:**
```bash
sudo systemctl restart email-tool.service
sudo systemctl status email-tool.service
```

**Hoặc start manual:**
```bash
cd /home/bighitran1905/webapp
pkill -f "python app.py"
nohup venv/bin/python app.py > flask_server.log 2>&1 &
```

### Server chậm?

**Clear cache và restart:**
```bash
# Clear system cache
sync && sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'

# Restart SSH
sudo systemctl restart ssh

# Restart Flask
sudo systemctl restart email-tool.service
```

---

## 📊 MONITORING

### Xem Server Load:
```bash
# CPU và Memory
top

# Hoặc htop (nếu có)
htop

# Quick check
free -h
uptime
```

### Xem Flask Requests:
```bash
# Real-time log
tail -f /home/bighitran1905/webapp/flask_server.log

# Last 100 lines
tail -100 /home/bighitran1905/webapp/flask_server.log

# Search trong log
grep "GET" /home/bighitran1905/webapp/flask_server.log
grep "POST" /home/bighitran1905/webapp/flask_server.log
grep "ERROR" /home/bighitran1905/webapp/flask_server.log
```

---

## 🎯 QUICK COMMANDS

### Một số lệnh hay dùng:

```bash
# Check nhanh server có chạy không
curl -s http://localhost:5000 | grep "Email Tool" && echo "✅ Server OK"

# Restart nhanh
sudo systemctl restart email-tool.service

# Xem log 
tail -f /home/bighitran1905/webapp/flask_server.log

# Kill và restart
pkill -f "python app.py" && cd /home/bighitran1905/webapp && nohup venv/bin/python app.py > flask_server.log 2>&1 &

# Check port
sudo lsof -i :5000
```

---

## 📞 THÔNG TIN LIÊN HỆ

### Server Details:
```
IP Public: 35.247.153.179
IP Private: 10.148.0.2
Port: 5000
URL: http://35.247.153.179:5000
Project: /home/bighitran1905/webapp
Logfile: /home/bighitran1905/webapp/flask_server.log
Service: email-tool.service
```

### SSH Access:
```bash
ssh bighitran1905@35.247.153.179
```

---

## ✅ CHECKLIST

Trước khi truy cập từ máy khác:

- [x] Server đang chạy (ps aux | grep python)
- [x] Port 5000 listening (netstat -tulpn | grep 5000)
- [x] Firewall allow port 5000 (hoặc disabled)
- [x] IP public: 35.247.153.179
- [x] URL: http://35.247.153.179:5000
- [x] Systemd service enabled
- [x] Auto-restart on crash
- [x] Auto-start on boot

---

## 🎉 TẤT CẢ ĐÃ SẴN SÀNG!

**Bạn có thể truy cập ngay:**

🌐 **http://35.247.153.179:5000**

Từ bất kỳ máy tính, điện thoại, tablet nào có internet!

✅ Server sẽ chạy liên tục
✅ Không tắt khi đóng SSH
✅ Tự động restart nếu crash
✅ Tự động start khi server reboot

---

**Happy using! 🚀**
