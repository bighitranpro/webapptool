# Email Tool - Công cụ xử lý Email chuyên nghiệp

Ứng dụng web mạnh mẽ cung cấp đầy đủ các chức năng xử lý và kiểm tra email, đặc biệt tập trung vào email Facebook.

## 🚀 Tính năng

### 1. Kiểm tra liên kết email Facebook và trích xuất
- Trích xuất tất cả email Facebook từ văn bản
- Tự động phát hiện và lọc email Facebook

### 2. Kiểm tra email nhận được mã code Facebook
- Xác định email có thể nhận mã xác minh Facebook
- Kiểm tra tính hợp lệ của domain

### 3. Check email validation
- Kiểm tra định dạng email
- Validation chi tiết theo chuẩn RFC
- Kiểm tra độ dài, ký tự đặc biệt

### 4. Kiểm tra thông tin tài khoản Facebook từ Email
- Trích xuất username, domain
- Gợi ý tên người dùng từ email
- Xác định email Facebook

### 5. Check valid Facebook email
- Kiểm tra email có thể đăng ký Facebook
- Phát hiện email tạm, spam
- Đề xuất các domain được khuyến nghị

### 6. Lọc trùng, tách email từ văn bản bất kì
- Trích xuất email từ văn bản lớn
- Loại bỏ email trùng lặp
- Phân biệt email hợp lệ/không hợp lệ

### 7. Phân loại email
- Phân loại theo loại: social media, free email, business, temporary
- Xác định nhà cung cấp
- Phân tích domain

### 8. Get random email with number
- Tạo email ngẫu nhiên theo số lượng
- Tùy chọn có/không có số
- Nhiều domain phổ biến

### 9. Scan uid, tên, thông tin nick FB từ email
- Scan chi tiết thông tin email
- Tạo hash MD5 cho email
- Phân tích cấu trúc email
- Gợi ý tên từ username

### 10. Lọc Hotmail - Yahoo - Gmail
- Lọc email theo nhà cung cấp
- Phân loại Gmail, Yahoo, Hotmail, Outlook
- Thống kê số lượng theo từng loại

## 📦 Cài đặt

### Yêu cầu
- Python 3.7+
- pip

### Các bước cài đặt

1. Clone repository hoặc tải về source code

2. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

3. Chạy ứng dụng:
```bash
python app.py
```

4. Mở trình duyệt và truy cập:
```
http://localhost:5000
```

## 🎯 Sử dụng

### Giao diện Web
- Truy cập trang chủ để sử dụng tất cả các công cụ
- Mỗi công cụ có giao diện riêng với hướng dẫn rõ ràng
- Kết quả hiển thị ngay lập tức với định dạng đẹp mắt

### API Endpoints

#### 1. Validate Email
```
POST /api/validate-email
Body: {"email": "example@gmail.com"}
```

#### 2. Extract Facebook Email
```
POST /api/extract-facebook-email
Body: {"text": "Text containing emails..."}
```

#### 3. Check Facebook Code
```
POST /api/check-facebook-code
Body: {"email": "example@gmail.com"}
```

#### 4. Extract Account Info
```
POST /api/extract-account-info
Body: {"email": "example@gmail.com"}
```

#### 5. Check Valid Facebook
```
POST /api/check-valid-facebook
Body: {"email": "example@gmail.com"}
```

#### 6. Filter Emails
```
POST /api/filter-emails
Body: {"text": "...", "remove_duplicates": true}
```

#### 7. Classify Email
```
POST /api/classify-email
Body: {"email": "example@gmail.com"}
```

#### 8. Generate Random Email
```
POST /api/generate-random-email
Body: {"count": 5, "include_numbers": true}
```

#### 9. Scan Email
```
POST /api/scan-email
Body: {"email": "example@gmail.com"}
```

#### 10. Extract Providers
```
POST /api/extract-providers
Body: {"text": "Text containing emails..."}
```

## 🛠️ Công nghệ sử dụng

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Styling**: Custom CSS với Gradient hiện đại
- **Icons**: Font Awesome 6.4.0
- **Architecture**: RESTful API

## 🎨 Tính năng giao diện

- ✅ Responsive design - tương thích mọi thiết bị
- ✅ Modern UI với gradient đẹp mắt
- ✅ Animation mượt mà
- ✅ Màu sắc phân biệt rõ ràng cho từng chức năng
- ✅ Hiển thị kết quả trực quan
- ✅ Badge và icon sinh động

## 📝 Cấu trúc dự án

```
webapp/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md              # Documentation
├── templates/
│   └── index.html         # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css      # Stylesheet
│   └── js/
│       └── script.js      # JavaScript functionality
```

## 🔒 Bảo mật

- Validation đầu vào nghiêm ngặt
- Không lưu trữ dữ liệu người dùng
- Hash email khi cần thiết (MD5)
- CORS được cấu hình an toàn

## 🚀 Deploy

### Local Development
```bash
python app.py
```

### Production
Sử dụng WSGI server như Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📞 Hỗ trợ

Nếu gặp vấn đề, vui lòng tạo issue hoặc liên hệ.

## 📄 License

MIT License - Tự do sử dụng và chỉnh sửa.

## 👨‍💻 Phát triển bởi

AI Assistant - 2024

---

**Lưu ý**: Công cụ này chỉ dùng cho mục đích học tập và nghiên cứu. Vui lòng sử dụng có trách nhiệm.
