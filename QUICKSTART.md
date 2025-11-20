# ⚡ QUICKSTART GUIDE

## 🎯 Chạy nhanh trong 3 phút!

### 📋 Yêu cầu
- Python 3.7+
- pip
- Internet connection

---

## 🚀 3 BƯỚC CHẠY SERVER

### Bước 1: Clone/Download code
```bash
# Nếu có Git
git clone https://github.com/bighitranpro/webapptool.git
cd webapptool

# Hoặc download ZIP và giải nén
```

### Bước 2: Cài đặt dependencies
```bash
# Linux/MacOS
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Bước 3: Chạy!
```bash
python app.py
```

**✅ XONG! Truy cập:** http://localhost:5000

---

## 🌐 CHIA SẺ LÊN INTERNET (2 PHÚT)

### Dùng Ngrok (Đơn giản nhất!)

#### 1. Tải Ngrok
```
Windows: https://ngrok.com/download
Download file .zip, giải nén ra
```

#### 2. Chạy Flask server (terminal 1)
```bash
python app.py
```

#### 3. Chạy Ngrok (terminal 2)
```bash
# Di chuyển vào thư mục chứa ngrok.exe
cd C:\path\to\ngrok

# Expose port 5000
ngrok http 5000
```

#### 4. Copy URL
```
Ngrok hiển thị:
Forwarding: https://abc123.ngrok.io -> http://localhost:5000

🎉 Share link này với mọi người!
```

---

## 🧪 TEST NHANH 10 CHỨC NĂNG

### 1. Test Extract Facebook Email
```
Mở tool #1
Paste:
contact@facebook.com, support@fb.com, john@gmail.com
Click "Trích xuất"
✅ Sẽ tìm thấy 2 Facebook emails
```

### 2. Test Check Facebook Code
```
Mở tool #2
Nhập: test@gmail.com
Click "Kiểm tra"
✅ Hiển thị "CÓ THỂ nhận mã"
```

### 3. Test Validate Email
```
Mở tool #3
Nhập: john.doe@gmail.com
Click "Validate"
✅ Hiển thị điểm mạnh và chi tiết
```

### 4. Test Extract Account Info
```
Mở tool #4
Nhập: john.smith@facebook.com
Click "Lấy thông tin"
✅ Hiển thị username, tên gợi ý
```

### 5. Test Valid Facebook Email
```
Mở tool #5
Nhập: user@gmail.com
Click "Kiểm tra"
✅ Hiển thị "Hợp lệ" + recommended
```

### 6. Test Filter Emails
```
Mở tool #6
Paste:
test@gmail.com, support@yahoo.com, test@gmail.com
invalid@, @test.com
Click "Lọc Email"
✅ Tìm 3 emails, 2 unique, 2 valid
```

### 7. Test Classify Email
```
Mở tool #7
Nhập: contact@facebook.com
Click "Phân loại"
✅ Type: social_media
```

### 8. Test Random Email
```
Mở tool #8
Số lượng: 10
Check: Include numbers
Click "Tạo Email"
✅ 10 email ngẫu nhiên
```

### 9. Test Scan Email
```
Mở tool #9
Nhập: john.doe123@gmail.com
Click "Scan Email"
✅ Hiển thị hash, analysis, pattern
```

### 10. Test Filter Providers
```
Mở tool #10
Paste:
user1@gmail.com, user2@yahoo.com
user3@hotmail.com, user4@outlook.com
Click "Lọc theo nhà cung cấp"
✅ Phân loại 4 categories
```

---

## 🎨 FEATURES NÂNG CẤP MỚI

### ✨ Backend Enhancements
- ✅ **MX Record Validation** - Kiểm tra domain có thật
- ✅ **Email Strength Score** - Đánh giá độ mạnh email
- ✅ **Pattern Detection** - Phát hiện pattern email
- ✅ **Complexity Analysis** - Phân tích độ phức tạp
- ✅ **Hash Generation** - MD5 + SHA256
- ✅ **Bulk Validation** - Validate nhiều email cùng lúc
- ✅ **Email Statistics** - Thống kê chi tiết
- ✅ **Realistic Email Gen** - Tạo email realistic hơn

### 🎨 Frontend Enhancements
- ✅ **Loading States** - Button loading animation
- ✅ **Progress Bars** - Strength score visualization
- ✅ **Notifications** - Toast notifications
- ✅ **Copy to Clipboard** - Copy kết quả dễ dàng
- ✅ **Tooltips** - Giải thích chi tiết
- ✅ **Better Error Handling** - Xử lý lỗi tốt hơn

---

## 📊 API ENDPOINTS MỚI

```bash
# Bulk validate nhiều emails
POST /api/bulk-validate
Body: {"emails": ["email1@test.com", "email2@test.com"]}

# Thống kê từ văn bản
POST /api/email-statistics
Body: {"text": "văn bản chứa nhiều email..."}
```

---

## 🐛 TROUBLESHOOTING

### Server không start?
```bash
# Check port 5000
netstat -ano | findstr :5000  # Windows
lsof -i :5000                  # Linux/Mac

# Chạy port khác
export FLASK_RUN_PORT=8000    # Linux/Mac
set FLASK_RUN_PORT=8000       # Windows
python app.py
```

### Import error?
```bash
pip install -r requirements.txt --upgrade
```

### Ngrok timeout?
```bash
# Free plan có giới hạn 2 giờ
# Restart ngrok để có URL mới
```

---

## 🎯 CÁC TÌNH HUỐNG SỬ DỤNG

### Tình huống 1: Lọc email từ file lớn
```
1. Copy toàn bộ nội dung file
2. Paste vào tool #6 (Filter emails)
3. Check "Remove duplicates"
4. Click "Lọc Email"
5. Copy kết quả
```

### Tình huống 2: Validate list email hàng loạt
```
1. Chuẩn bị list email (1 email/dòng)
2. Paste vào tool #3 (Validate)
3. Xem kết quả từng email
4. Check strength score
```

### Tình huống 3: Generate test emails
```
1. Mở tool #8
2. Nhập số lượng cần (vd: 100)
3. Click Generate
4. Copy toàn bộ list
5. Dùng cho testing
```

### Tình huống 4: Scan email nghi ngờ
```
1. Mở tool #9
2. Nhập email cần scan
3. Xem analysis chi tiết
4. Check security score
5. Đánh giá độ tin cậy
```

---

## 📝 NOTES

- **Free MX lookup**: Tool tự động check MX record
- **No data stored**: Không lưu dữ liệu người dùng
- **Real-time**: Kết quả tức thì
- **Offline capable**: Chạy được offline (trừ MX check)

---

## 🎓 TIPS & TRICKS

1. **Ctrl + A** để select all trong textarea
2. **Ctrl + C** để copy kết quả
3. Sử dụng **DevTools** (F12) để debug
4. Check **Console** nếu có lỗi
5. **Refresh** page nếu UI bị lag

---

## 🚀 NEXT STEPS

Sau khi test xong:
1. ✅ Test tất cả 10 chức năng
2. ✅ Chạy ngrok để share online
3. ✅ Share link với team/bạn bè
4. ✅ Collect feedback
5. ✅ Report bugs nếu có

---

**🎉 Enjoy your Email Tool! Happy Testing!**

Để biết thêm chi tiết, xem:
- `TESTING_GUIDE.md` - Hướng dẫn test chi tiết
- `README.md` - Documentation đầy đủ
- `DEPLOYMENT.md` - Hướng dẫn deploy
