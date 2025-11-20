# 📖 HƯỚNG DẪN TEST VÀ CHẠY SERVER

## 🎯 MỤC LỤC
1. [Cách chạy server local](#cách-chạy-server-local)
2. [Cách host lên online (Windows CMD)](#cách-host-lên-online-windows-cmd)
3. [Hướng dẫn test từng chức năng](#hướng-dẫn-test-từng-chức-năng)
4. [Test data mẫu](#test-data-mẫu)

---

## 🚀 CÁCH CHẠY SERVER LOCAL

### A. Trên Linux/MacOS

```bash
# Bước 1: Di chuyển vào thư mục project
cd /home/bighitran1905/webapp

# Bước 2: Tạo virtual environment (nếu chưa có)
python3 -m venv venv

# Bước 3: Kích hoạt virtual environment
source venv/bin/activate

# Bước 4: Cài đặt dependencies
pip install -r requirements.txt

# Bước 5: Chạy server
python app.py

# Server sẽ chạy tại: http://localhost:5000
```

### B. Trên Windows

```cmd
REM Bước 1: Di chuyển vào thư mục project
cd C:\path\to\webapp

REM Bước 2: Tạo virtual environment (nếu chưa có)
python -m venv venv

REM Bước 3: Kích hoạt virtual environment
venv\Scripts\activate

REM Bước 4: Cài đặt dependencies
pip install -r requirements.txt

REM Bước 5: Chạy server
python app.py

REM Server sẽ chạy tại: http://localhost:5000
```

---

## 🌐 CÁCH HOST LÊN ONLINE (WINDOWS CMD)

### Phương án 1: Sử dụng Ngrok (Khuyến nghị - Đơn giản nhất)

**Ngrok** cho phép expose local server ra internet với URL public miễn phí!

#### Bước 1: Tải và cài đặt Ngrok

```cmd
REM Vào https://ngrok.com/download
REM Tải file ngrok.exe về
REM Giải nén vào thư mục C:\ngrok
```

#### Bước 2: Đăng ký tài khoản Ngrok (miễn phí)

```
Vào: https://dashboard.ngrok.com/signup
Đăng ký tài khoản miễn phí
Copy authentication token
```

#### Bước 3: Setup Ngrok

```cmd
REM Di chuyển vào thư mục ngrok
cd C:\ngrok

REM Xác thực với token (chỉ cần làm 1 lần)
ngrok authtoken YOUR_AUTH_TOKEN_HERE
```

#### Bước 4: Chạy server Flask trước

```cmd
REM Terminal 1: Chạy Flask server
cd C:\path\to\webapp
venv\Scripts\activate
python app.py
```

#### Bước 5: Chạy Ngrok

```cmd
REM Terminal 2: Chạy Ngrok
cd C:\ngrok
ngrok http 5000
```

#### Kết quả:

```
Ngrok sẽ hiển thị:

Session Status: online
Forwarding: https://abc123.ngrok.io -> http://localhost:5000

🎉 TRUY CẬP: https://abc123.ngrok.io
```

**✅ Ưu điểm:**
- Miễn phí
- Cực kỳ đơn giản
- HTTPS tự động
- Không cần config firewall

**⚠️ Lưu ý:**
- Free plan: URL thay đổi mỗi khi restart
- Giới hạn 40 connections/phút
- Session timeout sau 2 giờ (phải restart)

---

### Phương án 2: Sử dụng Localtunnel

#### Bước 1: Cài đặt Node.js
```cmd
REM Tải Node.js từ: https://nodejs.org/
REM Cài đặt Node.js
```

#### Bước 2: Cài đặt Localtunnel
```cmd
npm install -g localtunnel
```

#### Bước 3: Chạy server Flask
```cmd
cd C:\path\to\webapp
venv\Scripts\activate
python app.py
```

#### Bước 4: Chạy Localtunnel
```cmd
REM Terminal mới
lt --port 5000
```

**Kết quả:**
```
Your url is: https://funny-dog-12.loca.lt
```

---

### Phương án 3: Sử dụng Serveo (Không cần cài đặt)

#### Bước 1: Cài đặt OpenSSH trên Windows
```cmd
REM Settings > Apps > Optional Features
REM Thêm "OpenSSH Client"
```

#### Bước 2: Chạy server Flask
```cmd
cd C:\path\to\webapp
venv\Scripts\activate
python app.py
```

#### Bước 3: Chạy Serveo
```cmd
ssh -R 80:localhost:5000 serveo.net
```

**Kết quả:**
```
Forwarding HTTP traffic from https://random.serveo.net
```

---

### Phương án 4: Deploy lên Cloud (Production)

#### A. Deploy lên Heroku (Free tier)

```cmd
REM 1. Cài đặt Heroku CLI
REM Tải từ: https://devcenter.heroku.com/articles/heroku-cli

REM 2. Login
heroku login

REM 3. Tạo app
cd C:\path\to\webapp
heroku create your-app-name

REM 4. Tạo Procfile
echo web: python app.py > Procfile

REM 5. Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main

REM Truy cập: https://your-app-name.herokuapp.com
```

#### B. Deploy lên PythonAnywhere (Free)

```
1. Đăng ký tại: https://www.pythonanywhere.com/
2. Upload code lên
3. Tạo Web app mới
4. Configure WSGI file
5. Reload web app
```

#### C. Deploy lên Railway.app (Free tier)

```
1. Vào: https://railway.app/
2. Connect GitHub repository
3. Deploy tự động
4. Nhận public URL
```

---

## 🧪 HƯỚNG DẪN TEST TỪNG CHỨC NĂNG

### 1️⃣ Kiểm tra liên kết email Facebook và trích xuất

**Cách test:**
1. Truy cập tool #1
2. Nhập văn bản chứa email Facebook:
```
Liên hệ với chúng tôi qua john.doe@facebook.com hoặc support@fb.com
Các email khác: test@facebook.com, admin@workplace.facebook.com
```
3. Click "Trích xuất Email"
4. Kiểm tra kết quả hiển thị đúng các email Facebook

**Kết quả mong đợi:**
- Tìm thấy 4 email Facebook
- Hiển thị danh sách email
- Không có email duplicate

---

### 2️⃣ Kiểm tra email nhận được mã code Facebook

**Cách test:**
```
Test với các email:
✅ Valid: test@gmail.com
✅ Valid: user@yahoo.com
❌ Invalid: fake@tempmail.com
❌ Invalid: test@nonexistentdomain.xyz
```

**Kết quả mong đợi:**
- Gmail/Yahoo: ✅ Có thể nhận mã
- Tempmail: ❌ Không thể nhận mã
- Hiển thị MX record status
- Hiển thị nhà cung cấp tin cậy

---

### 3️⃣ Check email validation

**Cách test:**
```
✅ Valid emails:
- john.doe@gmail.com
- user_123@yahoo.com
- contact@company.com

❌ Invalid emails:
- invalid@
- @gmail.com
- user name@gmail.com
- test..test@gmail.com
```

**Kết quả mong đợi:**
- Hiển thị điểm mạnh (strength score)
- Chi tiết kiểm tra từng tiêu chí
- Khuyến nghị cải thiện

---

### 4️⃣ Kiểm tra thông tin tài khoản Facebook từ Email

**Cách test:**
```
Email: john.doe@facebook.com
```

**Kết quả mong đợi:**
- Username: john.doe
- Domain: facebook.com
- Potential name: John Doe
- Is Facebook: Yes

---

### 5️⃣ Check valid Facebook email

**Cách test:**
```
✅ Recommended:
- user@gmail.com
- contact@yahoo.com

⚠️ Accepted but not recommended:
- test@customdomain.com

❌ Not allowed:
- temp@tempmail.com
- throwaway@guerrillamail.com
```

**Kết quả mong đợi:**
- Status: Valid/Invalid
- Reason nếu invalid
- Recommended status

---

### 6️⃣ Lọc trùng, tách email từ văn bản

**Cách test:**
```
Nhập văn bản:
Contact us at: support@company.com, sales@company.com
Or email: john@gmail.com, jane@yahoo.com, john@gmail.com
Invalid: notanemail, @test.com
```

**Kết quả mong đợi:**
- Total found: 5 (hoặc 4 nếu remove duplicates)
- Valid emails: 4
- Invalid emails: 0 (vì đã lọc)
- Hiển thị badge cho mỗi email

---

### 7️⃣ Phân loại email

**Cách test:**
```
Test các email:
- john@facebook.com → social_media
- user@gmail.com → free_email
- contact@company.com → custom
- temp@tempmail.com → temporary
```

**Kết quả mong đợi:**
- Type chính xác
- Domain info
- Provider name

---

### 8️⃣ Generate random email

**Cách test:**
1. Nhập số lượng: 10
2. Check "Include numbers"
3. Click generate

**Kết quả mong đợi:**
- 10 email ngẫu nhiên
- Format đúng
- Domain đa dạng (gmail, yahoo, hotmail, etc.)
- Có số nếu đã check option

---

### 9️⃣ Scan uid, tên, thông tin nick FB

**Cách test:**
```
Email: john.doe123@gmail.com
```

**Kết quả mong đợi:**
- MD5 hash
- SHA256 hash
- Username analysis
- Pattern detection
- Character analysis
- Complexity score
- Potential name
- Domain validation

---

### 🔟 Lọc Hotmail - Yahoo - Gmail

**Cách test:**
```
Nhập văn bản:
Emails: john@gmail.com, jane@yahoo.com, bob@hotmail.com
Also: alice@outlook.com, charlie@gmail.com, dave@custom.com
```

**Kết quả mong đợi:**
- Gmail: 2 emails
- Yahoo: 1 email
- Hotmail: 1 email
- Outlook: 1 email
- Phân loại đúng theo category

---

## 📊 TEST DATA MẪU

### Văn bản chứa nhiều email:
```
Company Contacts:
- CEO: ceo@company.com
- Support: support@gmail.com
- Sales: sales@yahoo.com
- HR: hr@hotmail.com
- Marketing: marketing@outlook.com
- Facebook: fb.page@facebook.com
- Temp: test@tempmail.com

Personal emails:
john.doe@gmail.com, jane_smith123@yahoo.com
alice.wonderland@icloud.com, bob-builder@protonmail.com
```

### Email list để bulk validate:
```
valid1@gmail.com
valid2@yahoo.com
invalid@
@gmail.com
test..test@gmail.com
good_email@company.com
```

---

## 🎨 CHECKLIST TEST GIAO DIỆN

- [ ] Tất cả 10 tool cards hiển thị đúng
- [ ] Màu sắc khác nhau cho mỗi tool
- [ ] Hover effect hoạt động
- [ ] Button có loading state
- [ ] Kết quả hiển thị mượt mà (animation)
- [ ] Responsive trên mobile
- [ ] Icons hiển thị đúng
- [ ] Badge có màu phù hợp
- [ ] Scrollbar custom
- [ ] Copy to clipboard hoạt động
- [ ] Notification hiển thị

---

## 🔧 TROUBLESHOOTING

### Lỗi: "Port 5000 already in use"
```cmd
REM Windows: Tìm và kill process
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F

REM Hoặc chạy trên port khác
python app.py --port 8000
```

### Lỗi: "Module not found"
```cmd
pip install -r requirements.txt
```

### Lỗi: "Permission denied"
```cmd
REM Chạy CMD as Administrator
```

### Ngrok không kết nối
```cmd
REM Check internet connection
REM Restart ngrok
REM Verify authtoken
```

---

## 🌟 TIPS TESTING

1. **Sử dụng Browser DevTools (F12)**
   - Console: Xem lỗi JavaScript
   - Network: Xem API calls
   - Elements: Inspect CSS

2. **Test trên nhiều browser**
   - Chrome
   - Firefox
   - Edge
   - Safari (nếu có Mac)

3. **Test responsive**
   - Desktop: 1920x1080
   - Tablet: 768x1024
   - Mobile: 375x667

4. **Test performance**
   - Lighthouse score
   - Page load time
   - API response time

---

## 📞 HỖ TRỢ

Nếu gặp vấn đề:
1. Check console logs
2. Verify server đang chạy
3. Check network connectivity
4. Review error messages

---

**Happy Testing! 🎉**
