# 🔍 Debug Guide - Email Validator Pro

## ✅ STATUS: API HOẠT ĐỘNG BÌNH THƯỜNG

Tôi đã test API và **nó hoạt động tốt**. Email validation đang chạy đúng.

**Test kết quả**:
```json
{
  "success": true,
  "validator": "professional",
  "stats": {
    "total": 1,
    "live": 1,
    "die": 0,
    "processing_time": 1.61
  }
}
```

---

## 🎯 DEBUG TOOLS

### 1. Trang Test/Debug Chuyên Dụng

**URL**: http://14.225.210.195:5000/test

Trang này giúp bạn:
- ✅ Test API Health
- ✅ Test single email validation
- ✅ Test bulk email validation
- ✅ Xem JavaScript console logs realtime
- ✅ Xem response JSON chi tiết

**Cách dùng**:
1. Truy cập: http://14.225.210.195:5000/test
2. Click "Test Health Endpoint" → Xem API có hoạt động không
3. Nhập email → Click "Validate Single Email"
4. Xem kết quả JSON và logs

### 2. API Test Commands

**Test Health:**
```bash
curl http://14.225.210.195:5000/api/health
```

**Test Single Email:**
```bash
curl -X POST http://14.225.210.195:5000/api/validate \
  -H "Content-Type: application/json" \
  -d '{"emails":["test@gmail.com"],"options":{"use_pro_validator":true}}'
```

**Test Bulk Emails:**
```bash
curl -X POST http://14.225.210.195:5000/api/validate \
  -H "Content-Type: application/json" \
  -d '{
    "emails":["test@gmail.com","example@yahoo.com","invalid@fake.com"],
    "options":{"use_pro_validator":true,"max_workers":20}
  }'
```

---

## 🐛 COMMON ISSUES & FIXES

### Issue 1: "updateDashboardStats is not defined"

**Status**: ✅ **ĐÃ SỬA**

**Fix**: Đã sửa trong commit `6bb5c8a`

**Nguyên nhân**: Lỗi typo trong file `static/js/dashboard.js`

**Giải pháp**: Nếu vẫn gặp, bạn đang dùng **ứng dụng cũ (app.py)**. Hãy chuyển sang **ứng dụng mới (app_pro.py)**.

---

### Issue 2: Không kết nối được WebSocket

**Triệu chứng**:
- Connection status: "Disconnected"
- Không có realtime updates
- Progress bar không động

**Nguyên nhân**:
1. WebSocket bị block bởi proxy/firewall
2. Browser không support WebSocket
3. CORS issue

**Giải pháp**:

**A. Check WebSocket Support:**
```javascript
// Mở browser console (F12) và chạy:
if ('WebSocket' in window) {
    console.log('✅ WebSocket supported');
} else {
    console.log('❌ WebSocket NOT supported');
}
```

**B. Test WebSocket Connection:**
```javascript
// Mở browser console và chạy:
const socket = io('http://14.225.210.195:5000');
socket.on('connect', () => console.log('✅ Connected'));
socket.on('disconnect', () => console.log('❌ Disconnected'));
```

**C. Bypass WebSocket (Use REST API):**

Nếu WebSocket không hoạt động, dùng trang test:
```
http://14.225.210.195:5000/test
```

Trang này dùng REST API thuần, không cần WebSocket.

---

### Issue 3: Validation không trả về kết quả

**Triệu chứng**:
- Click "Bắt đầu kiểm tra" nhưng không có gì xảy ra
- Không có progress bar
- Không có kết quả

**Debug Steps**:

**Step 1: Mở Browser Console (F12)**
```
1. Nhấn F12 hoặc Ctrl+Shift+I
2. Chọn tab "Console"
3. Click "Bắt đầu kiểm tra"
4. Xem errors màu đỏ
```

**Step 2: Check Network Tab**
```
1. Mở F12 → Tab "Network"
2. Click "Bắt đầu kiểm tra"
3. Xem request "start_validation" hoặc "validate"
4. Click vào request → Tab "Response" → Xem error
```

**Step 3: Use Test Page**
```
Truy cập: http://14.225.210.195:5000/test
- Test từng bước
- Xem logs chi tiết
```

---

### Issue 4: SMTP Timeout

**Triệu chứng**:
- Validation chậm
- Nhiều emails trả về "UNKNOWN"
- Response time > 30s

**Nguyên nhân**:
1. Port 25 bị block bởi hosting
2. SMTP server slow/unavailable
3. Timeout setting quá thấp

**Giải pháp**:

**A. Check Port 25:**
```bash
# Test từ server
telnet gmail-smtp-in.l.google.com 25

# Nếu không kết nối được → Port 25 bị block
```

**B. Tăng Timeout:**
```javascript
// Trong options khi validate:
{
  "options": {
    "timeout": 60,  // Tăng từ 30s → 60s
    "max_retries": 3
  }
}
```

**C. Giảm Workers:**
```javascript
// Giảm số workers để tránh rate limit
{
  "options": {
    "max_workers": 10  // Giảm từ 20 → 10
  }
}
```

---

### Issue 5: Kết quả không chính xác

**Triệu chứng**:
- Email hợp lệ bị đánh DIE
- Email không hợp lệ được đánh LIVE

**Nguyên nhân**:
1. Catch-all domain (domain chấp nhận mọi email)
2. Greylisting (temporary rejection)
3. Rate limiting

**Giải pháp**:

**A. Check Catch-All Status:**
```javascript
// Xem trong result:
{
  "is_catch_all": true,  // ← Domain chấp nhận mọi email
  "status": "CATCH_ALL"
}
```

**B. Check Score:**
```javascript
// Score càng cao càng đáng tin:
{
  "score": 85.5,        // ← 85.5/100 = LIVE (tin cậy)
  "score": 45.2,        // ← 45.2/100 = UNKNOWN (không chắc)
  "score": 15.8,        // ← 15.8/100 = DIE (không hợp lệ)
}
```

**C. Check Retry Count:**
```javascript
// Nếu retry nhiều → có vấn đề:
{
  "retry_count": 3,     // ← Đã retry 3 lần
  "smtp_status": 450    // ← Temporary failure
}
```

---

## 📊 DEBUGGING WORKFLOW

```
┌─────────────────────────────────────┐
│  1. Vấn Đề: Không validate được     │
└─────────────────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  2. Test API Health                 │
│  http://domain:5000/api/health      │
└─────────────────────────────────────┘
             ↓
        ┌────┴────┐
        │  OK?    │
        └────┬────┘
     ✅ YES │    │ ❌ NO
            │    └──→ App không chạy
            │          → Restart app
            ↓
┌─────────────────────────────────────┐
│  3. Test với Test Page              │
│  http://domain:5000/test            │
└─────────────────────────────────────┘
             ↓
        ┌────┴────┐
        │  OK?    │
        └────┬────┘
     ✅ YES │    │ ❌ NO
            │    └──→ API lỗi
            │          → Check logs
            ↓
┌─────────────────────────────────────┐
│  4. Test Main UI                    │
│  http://domain:5000/                │
└─────────────────────────────────────┘
             ↓
        ┌────┴────┐
        │  OK?    │
        └────┬────┘
     ✅ YES │    │ ❌ NO
            │    └──→ Frontend issue
            │          → Check console
            ↓
┌─────────────────────────────────────┐
│  5. Check Browser Console (F12)     │
│  - Console tab: Xem errors          │
│  - Network tab: Xem requests        │
└─────────────────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  6. Specific Error → Check Below    │
└─────────────────────────────────────┘
```

---

## 🔧 QUICK FIXES

### Fix 1: Clear Browser Cache
```
1. Nhấn Ctrl+Shift+Delete
2. Chọn "Cached images and files"
3. Click "Clear data"
4. Reload page (Ctrl+F5)
```

### Fix 2: Hard Reload
```
Ctrl+Shift+R  (Windows/Linux)
Cmd+Shift+R   (Mac)
```

### Fix 3: Restart App
```bash
# Stop app
pkill -f "python3 app_pro.py"

# Start app
cd /home/root/webapp
python3 app_pro.py

# Or use systemd (if configured)
sudo systemctl restart email-validator-pro
```

### Fix 4: Check Firewall
```bash
# Allow port 5000
sudo ufw allow 5000/tcp

# Check status
sudo ufw status
```

### Fix 5: Re-install Dependencies
```bash
cd /home/root/webapp
pip3 install -r requirements.txt --upgrade
```

---

## 📱 CONTACT & SUPPORT

### Logs Location
```bash
# Application logs
tail -f /home/root/webapp/logs/email_validator.log

# System logs
journalctl -u email-validator-pro -f
```

### Check App Status
```bash
# Check if running
ps aux | grep app_pro.py

# Check port
netstat -tulpn | grep 5000
lsof -i :5000
```

### Server Info
```bash
# Check system resources
free -h        # Memory
df -h          # Disk
top            # CPU
```

---

## ✅ VERIFICATION CHECKLIST

Để đảm bảo mọi thứ hoạt động:

- [ ] Health endpoint trả về `"status": "healthy"`
- [ ] Test page (http://domain:5000/test) hoạt động
- [ ] Single email validation hoạt động
- [ ] Bulk validation hoạt động
- [ ] WebSocket connection thành công
- [ ] Progress bar hiển thị
- [ ] Results table cập nhật
- [ ] Export buttons hoạt động
- [ ] No errors in browser console
- [ ] No errors in server logs

---

## 📞 STILL HAVING ISSUES?

### Option 1: Use Test Page
```
http://14.225.210.195:5000/test
```
- Bypass WebSocket
- Use REST API directly
- See detailed logs

### Option 2: Use API Directly
```bash
# Test from command line
curl -X POST http://14.225.210.195:5000/api/validate \
  -H "Content-Type: application/json" \
  -d '{"emails":["your@email.com"]}'
```

### Option 3: Check Documentation
- `README_PRO.md` - Complete guide
- `UPGRADE_SUMMARY.md` - Technical details
- `QUICK_FIX_GUIDE.md` - Quick fixes

---

## 🎯 CONCLUSION

**API đang hoạt động bình thường!**

Nếu bạn gặp lỗi:
1. ✅ Dùng trang test: http://14.225.210.195:5000/test
2. ✅ Check browser console (F12)
3. ✅ Test từng API endpoint
4. ✅ Check logs: `tail -f logs/email_validator.log`

**Most likely issues**:
- Browser cache → Clear cache
- WebSocket blocked → Use test page
- Port 25 blocked → Contact hosting

---

**Version**: 3.0.0  
**Last Updated**: 2024-11-21  
**Status**: ✅ WORKING
