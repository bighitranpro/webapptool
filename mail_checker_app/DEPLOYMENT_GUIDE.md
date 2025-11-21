# 🚀 Hướng Dẫn Deployment - Email Checker App

## ✅ Tình Trạng Hiện Tại

**App đang chạy thành công!** 🎉

- **URL Public**: http://14.225.210.195:8001
- **Health Check**: http://14.225.210.195:8001/health
- **Status**: Running with Gunicorn (2 workers)

## 📋 Các Bước Đã Thực Hiện

### 1. ✅ Cài Đặt Dependencies
```bash
cd /home/root/webapp/mail_checker_app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. ✅ Test Các Modules
- Email Generator: ✅ Working
- SMTP Checker: ✅ Working  
- Facebook Checker: ✅ Working
- Geo Locator: ✅ Working
- Exporter: ✅ Working
- Flask App: ✅ Working

### 3. ✅ Khởi Động Gunicorn
```bash
gunicorn --workers 2 --bind 0.0.0.0:8001 app:app --daemon
```

## 🎯 Sử Dụng Ứng Dụng

### Truy Cập Web Interface
Mở trình duyệt và truy cập:
```
http://14.225.210.195:8001
```

### Các Bước Sử Dụng

1. **Tạo Email**
   - Nhập số lượng email (1-1000)
   - Chọn tỷ lệ email Việt Nam (0-100%)
   - Click "🎲 Tạo Email"

2. **Kiểm Tra Email**
   - Click "✅ Kiểm Tra" sau khi tạo email
   - Xem tiến trình real-time
   - Kết quả hiển thị trong bảng

3. **Xuất CSV**
   - Click "💾 Xuất CSV" sau khi kiểm tra xong
   - File sẽ tự động tải về

### API Endpoints

#### Health Check
```bash
curl http://14.225.210.195:8001/health
```

#### Generate Emails
```bash
curl -X POST http://14.225.210.195:8001/generate \
  -H "Content-Type: application/json" \
  -d '{"count": 10, "mix_ratio": 0.7}'
```

#### Check Emails
```bash
curl -X POST http://14.225.210.195:8001/check \
  -H "Content-Type: application/json" \
  -d '{"emails": ["test@gmail.com", "example@yahoo.com"]}'
```

#### Get Progress
```bash
curl http://14.225.210.195:8001/progress
```

## 🔧 Deployment Hoàn Chỉnh Trên VPS Ubuntu 20.04

Nếu muốn deploy đầy đủ với Nginx + Systemd service:

### Bước 1: Chạy Deploy Script
```bash
cd /home/root/webapp/mail_checker_app
chmod +x deploy.sh
./deploy.sh
```

Script sẽ tự động:
- Cài đặt Nginx, Python, UFW
- Tạo virtual environment
- Cài dependencies
- Tạo systemd service
- Cấu hình Nginx reverse proxy
- Mở firewall ports (80, 443, 22)
- Khởi động services

### Bước 2: Truy Cập
Sau khi deploy:
```
http://[IP_VPS]
```

### Bước 3: Setup SSL (Optional)
Nếu có domain:
```bash
apt-get install certbot python3-certbot-nginx -y
certbot --nginx -d your-domain.com
```

## 🛠️ Quản Lý Services

### Kiểm Tra Status
```bash
# Gunicorn
systemctl status mailchecker

# Nginx
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
tail -f /var/log/nginx/error.log
```

### Stop Services
```bash
systemctl stop mailchecker
systemctl stop nginx
```

## 📊 Monitoring

### Check Process
```bash
ps aux | grep gunicorn
```

### Check Ports
```bash
netstat -tulpn | grep 8000
```

### Resource Usage
```bash
top -p $(pgrep -d',' gunicorn)
```

## 🔒 Security Checklist

- [ ] Đổi SECRET_KEY trong app.py
- [ ] Giới hạn rate limiting
- [ ] Setup firewall (UFW)
- [ ] Cài SSL certificate
- [ ] Chạy app as non-root user
- [ ] Regular backup results folder
- [ ] Monitor logs thường xuyên

## 🐛 Troubleshooting

### App không start
```bash
cd /home/root/webapp/mail_checker_app
source venv/bin/activate
python app.py  # Test trực tiếp
```

### Port bị chiếm
```bash
# Tìm process chiếm port
lsof -i :8001

# Kill process
kill -9 <PID>
```

### Permission issues
```bash
chmod -R 755 /home/root/webapp/mail_checker_app
chown -R root:www-data /home/root/webapp/mail_checker_app
```

### Module not found
```bash
cd /home/root/webapp/mail_checker_app
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

## 📁 Cấu Trúc File

```
mail_checker_app/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── deploy.sh                 # Auto deployment script
├── README.md                 # Documentation
├── DEPLOYMENT_GUIDE.md       # This file
├── .gitignore               # Git ignore rules
├── checkers/                # Checker modules
│   ├── email_generator.py
│   ├── smtp_checker.py
│   ├── fb_checker.py
│   └── geo_locator.py
├── utils/                   # Utility modules
│   └── exporter.py
├── templates/               # HTML templates
│   └── index.html
├── static/                  # Static files
│   └── style.css
├── results/                 # CSV exports (gitignored)
└── venv/                    # Virtual environment (gitignored)
```

## 🎯 Features

✅ **Email Generation** - Tạo email giống người dùng thực
✅ **SMTP Validation** - Check Live/Die qua MX + RCPT TO
✅ **Facebook Check** - Phát hiện liên kết Facebook
✅ **Country Prediction** - Dự đoán quốc gia từ tên/domain
✅ **CSV Export** - Xuất kết quả chi tiết
✅ **Real-time Progress** - Theo dõi tiến trình live
✅ **Charts & Stats** - Biểu đồ thống kê với Chart.js
✅ **Responsive UI** - Giao diện đẹp, responsive

## 🔥 Performance Tips

1. **Tăng workers**: 
   ```bash
   gunicorn --workers 4 --bind 0.0.0.0:8001 app:app
   ```

2. **Timeout**: Tăng timeout cho slow connections
   ```bash
   gunicorn --timeout 300 --bind 0.0.0.0:8001 app:app
   ```

3. **Caching**: Implement Redis cho session caching

4. **Background Tasks**: Dùng Celery cho long operations

## 📞 Support

Nếu gặp vấn đề:

1. Check logs: `tail -f /var/log/nginx/error.log`
2. Test local: `python app.py`
3. Verify dependencies: `pip list`
4. Check firewall: `ufw status`

## 🎉 Kết Quả

App đã sẵn sàng sử dụng tại:
- **Web Interface**: http://14.225.210.195:8001
- **API Health**: http://14.225.210.195:8001/health
- **Status**: ✅ Running smoothly

---

**Happy Email Checking! 🚀**
