# 🔥 KHẮC PHỤC FIREWALL - CHO PHÉP TRUY CẬP PORT 5000

## ⚠️ VẤN ĐỀ

Server Flask đang chạy trên port 5000 NHƯNG không thể truy cập từ bên ngoài vì:
**GCP Firewall chưa mở port 5000**

---

## ✅ GIẢI PHÁP

### CÁCH 1: TẠO FIREWALL RULE QUA GCP CONSOLE (KHUYẾN NGHỊ)

#### Bước 1: Đăng nhập GCP Console
```
1. Vào: https://console.cloud.google.com/
2. Chọn Project: mystical-method-478206-s0
3. Đăng nhập với tài khoản Google của bạn
```

#### Bước 2: Vào VPC Network → Firewall
```
1. Menu bên trái → VPC network → Firewall
2. Hoặc search "Firewall" trong thanh tìm kiếm
3. Click "CREATE FIREWALL RULE"
```

#### Bước 3: Tạo Firewall Rule mới
```
Name: allow-flask-5000
Description: Allow Flask app on port 5000

Logs: Off (hoặc On nếu muốn track)

Network: default

Priority: 1000

Direction of traffic: Ingress

Action on match: Allow

Targets: All instances in the network
(Hoặc chọn "Specified target tags" nếu muốn cụ thể)

Source filter: IPv4 ranges

Source IPv4 ranges: 0.0.0.0/0
(Cho phép tất cả IP - public access)

Protocols and ports:
✓ Specified protocols and ports
✓ TCP: 5000

Click "CREATE"
```

#### Bước 4: Đợi 1-2 phút
```
Firewall rule sẽ có hiệu lực sau vài giây đến 1-2 phút
```

#### Bước 5: Test
```
Mở browser trên máy khác
Vào: http://35.247.153.179:5000
✅ Sẽ thấy Email Tool!
```

---

### CÁCH 2: DÙNG GCLOUD CLI (Nếu có quyền)

Nếu bạn có gcloud CLI trên máy local với đầy đủ quyền:

```bash
gcloud auth login

gcloud config set project mystical-method-478206-s0

gcloud compute firewall-rules create allow-flask-5000 \
    --allow tcp:5000 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow Flask app on port 5000" \
    --direction INGRESS \
    --priority 1000

# Verify
gcloud compute firewall-rules list --filter="name:allow-flask-5000"
```

---

### CÁCH 3: DÙNG NGROK (KHÔNG CẦN FIREWALL)

Nếu không muốn động vào GCP Firewall, dùng Ngrok để expose:

```bash
# SSH vào server
ssh bighitran1905@35.247.153.179

# Download ngrok
cd ~
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz

# Đăng ký account: https://dashboard.ngrok.com/signup
# Lấy authtoken và config:
./ngrok config add-authtoken YOUR_TOKEN_HERE

# Chạy ngrok
./ngrok http 5000

# Lấy URL public (https://abc123.ngrok-free.app)
# Share URL này!
```

**Ưu điểm Ngrok:**
- ✅ Không cần config firewall
- ✅ HTTPS tự động
- ✅ Setup nhanh 5 phút
- ✅ Public URL ngay

**Nhược điểm:**
- ⚠️ Free plan: URL thay đổi khi restart
- ⚠️ Timeout sau 2 giờ
- ⚠️ Giới hạn 40 connections/phút

---

## 🔍 KIỂM TRA SAU KHI TẠO FIREWALL

### Từ máy khác:
```bash
# Test kết nối đến port 5000
telnet 35.247.153.179 5000

# Hoặc dùng curl
curl -I http://35.247.153.179:5000

# Hoặc mở browser
http://35.247.153.179:5000
```

### Từ server (SSH):
```bash
# Check firewall rules
gcloud compute firewall-rules list

# Check port
sudo netstat -tulpn | grep 5000

# Check process
ps aux | grep "python app.py"

# Test local
curl http://localhost:5000
```

---

## 📋 TEMPLATE FIREWALL RULE

Nếu tạo thủ công, dùng thông tin này:

```yaml
Name: allow-flask-5000
Network: default
Priority: 1000
Direction: INGRESS
Action: ALLOW
Targets: All instances
Source IPv4 ranges: 0.0.0.0/0
Protocols and ports: tcp:5000
```

---

## 🔒 BẢO MẬT (Tùy chọn)

### Nếu chỉ muốn cho phép IP cụ thể:

Thay vì `0.0.0.0/0`, dùng IP của bạn:

```
Source IPv4 ranges: YOUR_IP_ADDRESS/32

Ví dụ: 
- Nhà: 118.70.128.45/32
- Công ty: 192.168.1.100/32
- Nhiều IP: 118.70.128.45/32,192.168.1.100/32
```

### Nếu chỉ cho phép từ một quốc gia:

Có thể dùng Cloud Armor (nâng cao):
```
Google Cloud Console → Network Security → Cloud Armor
```

---

## ⚡ TROUBLESHOOTING

### 1. Firewall rule đã tạo nhưng vẫn không truy cập được?

**Check firewall rule có applied không:**
```bash
gcloud compute firewall-rules describe allow-flask-5000
```

**Đợi thêm 2-3 phút** để rule có hiệu lực

### 2. Test từ chính server được nhưng từ ngoài không được?

Chắc chắn là firewall issue. Tạo lại rule:
```bash
gcloud compute firewall-rules delete allow-flask-5000
gcloud compute firewall-rules create allow-flask-5000 --allow tcp:5000 --source-ranges 0.0.0.0/0
```

### 3. Vẫn không được?

Check xem instance có network tags không:
```bash
gcloud compute instances describe instance-20251114-070318 --format="get(tags.items)"
```

Nếu có tags, firewall rule phải target tags đó.

### 4. Dùng Ngrok thay thế

Nhanh nhất: Dùng Ngrok (5 phút setup)

---

## 📞 SUPPORT

### Link hữu ích:
- GCP Firewall: https://console.cloud.google.com/networking/firewalls
- Ngrok: https://ngrok.com/
- GCP Docs: https://cloud.google.com/vpc/docs/firewalls

### Commands nhanh:
```bash
# List all firewall rules
gcloud compute firewall-rules list

# Check specific rule
gcloud compute firewall-rules describe allow-flask-5000

# Delete rule
gcloud compute firewall-rules delete allow-flask-5000

# Test port
nc -zv 35.247.153.179 5000
telnet 35.247.153.179 5000
```

---

## ✅ CHECKLIST

Sau khi tạo firewall rule:

- [ ] Firewall rule created: allow-flask-5000
- [ ] Protocol: TCP
- [ ] Port: 5000
- [ ] Source: 0.0.0.0/0
- [ ] Direction: Ingress
- [ ] Action: Allow
- [ ] Target: All instances (or specific tags)
- [ ] Đợi 1-2 phút
- [ ] Test: curl http://35.247.153.179:5000
- [ ] Test: Mở browser từ máy khác
- [ ] ✅ Truy cập thành công!

---

## 🎯 TÓM TẮT

**Nguyên nhân:** GCP Firewall chặn port 5000

**Giải pháp:**
1. ✅ **TỐT NHẤT:** Tạo firewall rule qua GCP Console
2. ✅ **Nhanh:** Dùng Ngrok (không cần config firewall)
3. ✅ **CLI:** Dùng gcloud nếu có quyền

**Sau khi fix:**
- Server sẽ truy cập được từ mọi máy
- URL: http://35.247.153.179:5000
- Hoặc Ngrok: https://abc123.ngrok-free.app

---

## 🚀 HÀNH ĐỘNG

**Làm ngay:**

### Option 1: GCP Console (5 phút)
1. Vào https://console.cloud.google.com/
2. VPC Network → Firewall
3. CREATE FIREWALL RULE
4. Name: allow-flask-5000, Port: tcp:5000
5. Source: 0.0.0.0/0
6. CREATE
7. Đợi 1-2 phút
8. Test: http://35.247.153.179:5000

### Option 2: Ngrok (3 phút)
1. SSH vào server
2. Download & install ngrok
3. Config authtoken
4. Run: ngrok http 5000
5. Share public URL

---

**Chọn 1 trong 2 cách và làm ngay!**

Sau đó server sẽ truy cập được từ mọi thiết bị! 🎉
