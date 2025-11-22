# 📧 Email Checker - Flask Web Application

Ứng dụng web kiểm tra email SMTP Live/Die, liên kết Facebook, và dự đoán quốc gia người dùng.

## 🎯 Tính Năng

1. **Tạo Email Giả Lập** - Tạo danh sách email giống người dùng thực tế (Việt Nam & Quốc tế)
2. **Kiểm Tra SMTP** - Xác minh email Live/Die qua MX records và RCPT TO
3. **Kiểm Tra Facebook** - Phát hiện email có liên kết tài khoản Facebook
4. **Dự Đoán Quốc Gia** - Phân tích quốc gia dựa trên họ tên và domain
5. **Xuất CSV** - Export kết quả chi tiết
6. **Biểu Đồ Thống Kê** - Visualization với Chart.js
7. **Giao Diện Responsive** - Hoạt động mọi thiết bị

## 📁 Cấu Trúc Dự Án

```
mail_checker_app/
├── app.py                          # Flask web server
├── requirements.txt                # Python dependencies
├── deploy.sh                       # Deployment script
├── README.md                       # Documentation
├── checkers/
│   ├── __init__.py
│   ├── email_generator.py          # Email generator
│   ├── smtp_checker.py             # SMTP validator
│   ├── fb_checker.py               # Facebook checker
│   └── geo_locator.py              # Country predictor
├── utils/
│   ├── __init__.py
│   └── exporter.py                 # CSV exporter
├── templates/
│   └── index.html                  # Web interface
├── static/
│   └── style.css                   # Styling
└── results/                        # CSV output directory
```

## 🚀 Cài Đặt Nhanh

### Yêu Cầu Hệ Thống
- Ubuntu 20.04 LTS
- Python 3.8+
- Root access hoặc sudo privileges

### Bước 1: Clone hoặc Upload Code

```bash
# Nếu code đã ở /root/mail_checker_app/
cd /root/mail_checker_app

# Hoặc tạo thư mục mới
mkdir -p /root/mail_checker_app
cd /root/mail_checker_app
```

### Bước 2: Chạy Deploy Script

```bash
chmod +x deploy.sh
./deploy.sh
```

Script sẽ tự động:
- Cập nhật system packages
- Cài đặt Python, Nginx, UFW
- Tạo virtual environment
- Cài dependencies
- Cấu hình Gunicorn systemd service
- Cấu hình Nginx reverse proxy
- Mở firewall ports
- Khởi động services

### Bước 3: Truy Cập Ứng Dụng

```
http://[IP_CỦA_BẠN]
```

## 🔧 Quản Lý Service

### Kiểm Tra Trạng Thái
```bash
systemctl status mailchecker
systemctl status nginx
```

### Khởi Động Lại
```bash
systemctl restart mailchecker
systemctl restart nginx
```

### Xem Logs
```bash
# Gunicorn logs
journalctl -u mailchecker -f

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Dừng Service
```bash
systemctl stop mailchecker
systemctl stop nginx
```

## 📝 Cấu Hình Chi Tiết

### Gunicorn Service

File: `/etc/systemd/system/mailchecker.service`

```ini
[Unit]
Description=Gunicorn instance for Email Checker Flask App
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/root/mail_checker_app
Environment="PATH=/root/mail_checker_app/venv/bin"
ExecStart=/root/mail_checker_app/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 --timeout 120 app:app

[Install]
WantedBy=multi-user.target
```

### Nginx Configuration

File: `/etc/nginx/sites-available/mailchecker`

```nginx
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
```

## 🔒 Cài Đặt SSL (Let's Encrypt)

Nếu bạn có domain, cài SSL miễn phí:

```bash
# Cài certbot
apt-get install certbot python3-certbot-nginx -y

# Lấy certificate (thay your-domain.com)
certbot --nginx -d your-domain.com

# Auto-renewal
certbot renew --dry-run
```

## 🧪 Chạy Thử Nghiệm Local

```bash
cd /root/mail_checker_app
source venv/bin/activate
python app.py
```

Truy cập: `http://localhost:8000`

## 📊 API Endpoints

### POST /generate
Tạo danh sách email

**Request:**
```json
{
  "count": 10,
  "mix_ratio": 0.7
}
```

**Response:**
```json
{
  "success": true,
  "emails": ["email1@gmail.com", ...],
  "count": 10
}
```

### POST /check
Bắt đầu kiểm tra email

**Request:**
```json
{
  "emails": ["email1@gmail.com", "email2@yahoo.com"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Checking started",
  "total": 2
}
```

### GET /progress
Lấy tiến trình kiểm tra

**Response:**
```json
{
  "is_running": true,
  "current": 5,
  "total": 10,
  "status": "running",
  "results": [...]
}
```

### POST /export
Xuất kết quả ra CSV

**Request:**
```json
{
  "results": [...],
  "filename": "my_results.csv"
}
```

### GET /download/<filename>
Tải file CSV đã xuất

## 🔥 Firewall (UFW)

```bash
# Kiểm tra status
ufw status

# Cho phép ports
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS

# Enable firewall
ufw enable
```

## 🐛 Troubleshooting

### Service không start được

```bash
# Xem logs chi tiết
journalctl -u mailchecker -n 100 --no-pager

# Kiểm tra syntax Python
cd /root/mail_checker_app
source venv/bin/activate
python app.py
```

### Nginx 502 Bad Gateway

```bash
# Kiểm tra Gunicorn có chạy không
systemctl status mailchecker

# Kiểm tra port 8000
netstat -tulpn | grep 8000

# Restart cả 2 services
systemctl restart mailchecker nginx
```

### Permission denied

```bash
# Cấp quyền cho directories
chmod -R 755 /root/mail_checker_app
chown -R root:www-data /root/mail_checker_app/results
```

### Python module not found

```bash
# Reinstall dependencies
cd /root/mail_checker_app
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

## ⚡ Performance Tips

1. **Tăng workers**: Edit `/etc/systemd/system/mailchecker.service`
   ```
   --workers 8  # Tùy CPU cores
   ```

2. **Caching**: Thêm Redis cho session caching

3. **Rate Limiting**: Giới hạn requests để tránh bị block

4. **Background Tasks**: Dùng Celery cho long-running tasks

## 🔐 Security Best Practices

1. **Đổi Secret Key** trong `app.py`:
   ```python
   app.config['SECRET_KEY'] = 'your-random-secret-key-here'
   ```

2. **Chạy as non-root user**:
   ```bash
   useradd -m -s /bin/bash mailchecker
   chown -R mailchecker:mailchecker /root/mail_checker_app
   ```

3. **Giới hạn rate limiting**:
   - Cài Flask-Limiter
   - Thêm rate limits cho endpoints

4. **Environment Variables**:
   - Dùng `.env` file cho sensitive data
   - Không commit secrets vào Git

## 📦 Dependencies

- **flask** - Web framework
- **gunicorn** - WSGI HTTP server
- **requests** - HTTP client
- **dnspython** - DNS toolkit
- **pandas** - Data manipulation
- **aiohttp** - Async HTTP client
- **scikit-learn** - ML utilities

## 🤝 Contributing

Mọi đóng góp đều được chào đón!

## 📄 License

MIT License

## 👨‍💻 Author

Email Checker Team

## 📞 Support

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra logs: `journalctl -u mailchecker -f`
2. Xem nginx logs: `tail -f /var/log/nginx/error.log`
3. Test local: `python app.py`

---

**🎉 Chúc bạn deploy thành công!**
