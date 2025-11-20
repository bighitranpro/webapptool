# 🚀 NGROK SETUP - TRUY CẬP NGAY (3 PHÚT)

## ✅ NGROK ĐÃ CÀI SẴN!

Ngrok đã được download và ready tại: `/home/bighitran1905/ngrok`

---

## 🎯 SETUP NHANH (2 BƯỚC)

### Bước 1: Lấy Authtoken (1 phút)

1. **Đăng ký Ngrok (MIỄN PHÍ):**
   - Vào: https://dashboard.ngrok.com/signup
   - Đăng ký với Google/GitHub/Email
   - Xác nhận email

2. **Lấy Authtoken:**
   - Sau khi login: https://dashboard.ngrok.com/get-started/your-authtoken
   - Copy token (dạng: `2abc...xyz`)
   - Lưu lại token này

3. **Config Ngrok:**
```bash
# SSH vào server
ssh bighitran1905@35.247.153.179

# Config token (QUAN TRỌNG - làm 1 lần duy nhất)
/home/bighitran1905/ngrok config add-authtoken YOUR_TOKEN_HERE

# Ví dụ:
/home/bighitran1905/ngrok config add-authtoken 2abc123def456ghi789
```

---

### Bước 2: Chạy Ngrok (30 giây)

```bash
# SSH vào server
ssh bighitran1905@35.247.153.179

# Chạy ngrok
/home/bighitran1905/ngrok http 5000
```

---

## 🌐 KẾT QUẢ

Ngrok sẽ hiển thị:

```
ngrok

Session Status                online
Account                       your_email@example.com
Version                       3.33.0
Region                        United States (us)
Latency                       50ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:5000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

---

## ✅ URL CÔNG KHAI CỦA BẠN

```
https://abc123.ngrok-free.app
```

**👉 Share URL này với mọi người!**

- ✅ Truy cập từ mọi thiết bị
- ✅ HTTPS tự động
- ✅ Không cần config firewall
- ✅ Public ngay lập tức

---

## 💻 CÁCH SỬ DỤNG ĐẦY ĐỦ

### Terminal 1: Flask Server (đã chạy sẵn)
```bash
# Kiểm tra Flask có chạy không
ps aux | grep "python app.py"

# Nếu chưa chạy:
cd /home/bighitran1905/webapp
venv/bin/python app.py
```

### Terminal 2: Ngrok
```bash
# SSH kết nối mới (Terminal 2)
ssh bighitran1905@35.247.153.179

# Chạy ngrok
/home/bighitran1905/ngrok http 5000
```

### Từ Browser (máy khác):
```
Mở: https://abc123.ngrok-free.app
→ Thấy Email Tool với 10 chức năng!
```

---

## 🎯 COMMANDS NHANH

### Config token (1 lần duy nhất):
```bash
/home/bighitran1905/ngrok config add-authtoken YOUR_TOKEN
```

### Start ngrok:
```bash
/home/bighitran1905/ngrok http 5000
```

### Start ngrok (background):
```bash
nohup /home/bighitran1905/ngrok http 5000 > /tmp/ngrok.log 2>&1 &
```

### Check ngrok status:
```bash
curl http://localhost:4040/api/tunnels
```

### Stop ngrok:
```bash
pkill ngrok
```

---

## 📊 NGROK FEATURES

### ✅ Ưu điểm:
- Miễn phí
- Không cần config firewall GCP
- HTTPS tự động
- Setup 3 phút
- Public URL ngay
- Stable connection

### ⚠️ Giới hạn (Free plan):
- URL thay đổi mỗi khi restart
- Session timeout 2 giờ (cần restart)
- 40 connections/phút
- 1 tunnel cùng lúc

### 💎 Upgrade ($8/month):
- URL cố định (subdomain.ngrok.io)
- Không timeout
- Nhiều tunnels
- Custom domains

---

## 🔄 NGROK PERSISTENT (Chạy 24/7)

### Cách 1: Dùng systemd

Tạo file service:
```bash
sudo nano /etc/systemd/system/ngrok.service
```

Nội dung:
```ini
[Unit]
Description=Ngrok Tunnel
After=network.target

[Service]
Type=simple
User=bighitran1905
ExecStart=/home/bighitran1905/ngrok http 5000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable và start:
```bash
sudo systemctl enable ngrok.service
sudo systemctl start ngrok.service
sudo systemctl status ngrok.service
```

### Cách 2: Dùng screen

```bash
# Install screen
sudo apt install screen -y

# Tạo screen session
screen -S ngrok

# Chạy ngrok
/home/bighitran1905/ngrok http 5000

# Detach: Ctrl+A, D
# Reattach: screen -r ngrok
```

---

## 🎬 VIDEO TUTORIAL

### Bước 1: Đăng ký (1 phút)
```
1. Vào https://dashboard.ngrok.com/signup
2. Sign up with Google
3. Confirm email
4. Copy authtoken
```

### Bước 2: Config (30 giây)
```bash
ssh bighitran1905@35.247.153.179
/home/bighitran1905/ngrok config add-authtoken YOUR_TOKEN
```

### Bước 3: Run (30 giây)
```bash
/home/bighitran1905/ngrok http 5000
# Copy URL: https://abc123.ngrok-free.app
```

### Bước 4: Share! (10 giây)
```
Send URL to friends/colleagues
They open in browser
✅ Access Email Tool!
```

---

## 🔍 TROUBLESHOOTING

### Lỗi: "Authtoken not found"
```bash
# Config lại token
/home/bighitran1905/ngrok config add-authtoken YOUR_TOKEN

# Check config
cat ~/.ngrok2/ngrok.yml
```

### Lỗi: "Failed to connect"
```bash
# Check Flask có chạy không
curl http://localhost:5000

# Nếu không chạy, start Flask:
cd /home/bighitran1905/webapp
venv/bin/python app.py
```

### Lỗi: "Tunnel not found"
```bash
# Restart ngrok
pkill ngrok
/home/bighitran1905/ngrok http 5000
```

### Ngrok timeout sau 2 giờ?
```bash
# Restart ngrok để có URL mới
pkill ngrok
/home/bighitran1905/ngrok http 5000
```

---

## 💡 TIPS

### 1. Bookmark URL
Khi ngrok chạy, bookmark URL ngay để dễ truy cập

### 2. Use Ngrok Dashboard
Vào http://localhost:4040 (từ server) để xem:
- Requests
- Response times
- Replays
- Inspect traffic

### 3. Custom Subdomain (Paid)
```bash
/home/bighitran1905/ngrok http 5000 --subdomain=myemail-tool
# URL: https://myemail-tool.ngrok.io
```

### 4. Multiple Ports
```bash
# Port 5000
/home/bighitran1905/ngrok http 5000

# Port 8080
/home/bighitran1905/ngrok http 8080
```

---

## 🆚 SO SÁNH

### Ngrok vs GCP Firewall

| Feature | Ngrok | GCP Firewall |
|---------|-------|--------------|
| Setup time | 3 phút | 5 phút |
| Cần quyền admin | ❌ No | ✅ Yes |
| URL stable | ⚠️ Changes | ✅ Fixed |
| HTTPS | ✅ Auto | ⚠️ Manual |
| Cost | Free/Paid | Free |
| Best for | Testing, Demo | Production |

---

## 📞 SUPPORT

### Ngrok Links:
- Signup: https://dashboard.ngrok.com/signup
- Dashboard: https://dashboard.ngrok.com/
- Docs: https://ngrok.com/docs
- Pricing: https://ngrok.com/pricing

### Commands Reference:
```bash
# Version
/home/bighitran1905/ngrok version

# Help
/home/bighitran1905/ngrok help

# Config
/home/bighitran1905/ngrok config check

# HTTP tunnel
/home/bighitran1905/ngrok http 5000

# TCP tunnel
/home/bighitran1905/ngrok tcp 22
```

---

## ✅ CHECKLIST

Setup Ngrok:
- [x] Ngrok downloaded
- [ ] Đăng ký account
- [ ] Lấy authtoken
- [ ] Config: `ngrok config add-authtoken`
- [ ] Run: `ngrok http 5000`
- [ ] Copy URL
- [ ] Test từ browser
- [ ] Share với team!

---

## 🎉 KẾT LUẬN

**2 CÁCH CHỌN:**

### Option 1: Ngrok (NHANH - 3 phút)
```bash
1. Đăng ký: https://dashboard.ngrok.com/signup
2. Config: ngrok config add-authtoken YOUR_TOKEN
3. Run: /home/bighitran1905/ngrok http 5000
4. Share URL: https://abc123.ngrok-free.app
✅ Done!
```

### Option 2: GCP Firewall (STABLE - 5 phút)
```
1. GCP Console → VPC → Firewall
2. CREATE RULE: allow-flask-5000
3. Port: tcp:5000
4. Source: 0.0.0.0/0
5. CREATE
✅ URL: http://35.247.153.179:5000
```

---

**Chọn Ngrok nếu:**
- ✅ Muốn nhanh (3 phút)
- ✅ Không có quyền GCP
- ✅ Cần HTTPS
- ✅ Demo/testing

**Chọn GCP Firewall nếu:**
- ✅ Production
- ✅ URL cố định
- ✅ Có quyền GCP admin
- ✅ Long-term

---

**🚀 Làm ngay Option 1 (Ngrok) để truy cập trong 3 phút!**
