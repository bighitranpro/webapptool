# 🌐 DOMAIN CONFIGURATION GUIDE - mochiphoto.click

**Target Domain**: mochiphoto.click  
**Server IP**: 14.225.210.195  
**Port**: 5000  
**Status**: ✅ App configured, DNS setup needed

---

## 📋 STEP-BY-STEP SETUP

### Step 1: DNS Configuration (User Action Required)

Vào trang quản lý DNS của domain mochiphoto.click (ví dụ: Cloudflare, GoDaddy, Namecheap) và thêm các records sau:

#### A Records:
```
Type: A
Name: @
Value: 14.225.210.195
TTL: Auto or 300

Type: A  
Name: www
Value: 14.225.210.195
TTL: Auto or 300
```

#### Sau khi thêm DNS:
- Đợi 5-30 phút để DNS propagate
- Kiểm tra: `nslookup mochiphoto.click`
- Kết quả mong đợi: `14.225.210.195`

---

### Step 2: Verify DNS Propagation

```bash
# Check DNS resolution
nslookup mochiphoto.click
dig mochiphoto.click +short

# Expected output:
# 14.225.210.195
```

**Online Tools**:
- https://dnschecker.org
- https://www.whatsmydns.net

Enter `mochiphoto.click` and check if it resolves to `14.225.210.195`

---

### Step 3: Test Domain Access

#### Option A: HTTP (Port 5000)
```bash
# Test với curl
curl http://mochiphoto.click:5000/api/health

# Expected response:
# {"status": "healthy", "version": "3.0.0", ...}
```

#### Option B: Browser
Mở trình duyệt:
```
http://mochiphoto.click:5000/
```

Nếu thấy dashboard → Success! ✅

---

### Step 4: Setup Nginx Reverse Proxy (Recommended)

#### Install Nginx:
```bash
sudo apt update
sudo apt install nginx -y
```

#### Create Config:
```bash
sudo nano /etc/nginx/sites-available/mochiphoto.click
```

#### Add Configuration:
```nginx
server {
    listen 80;
    listen [::]:80;
    
    server_name mochiphoto.click www.mochiphoto.click;
    
    # Client max body size
    client_max_body_size 100M;
    
    # Proxy settings
    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # WebSocket support
    location /socket.io {
        proxy_pass http://localhost:5000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Enable Site:
```bash
sudo ln -s /etc/nginx/sites-available/mochiphoto.click /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Test:
```bash
curl http://mochiphoto.click/api/health
```

Now accessible on port 80 (standard HTTP)! ✅

---

### Step 5: SSL Certificate (HTTPS) - Optional but Recommended

#### Install Certbot:
```bash
sudo apt install certbot python3-certbot-nginx -y
```

#### Get Certificate:
```bash
sudo certbot --nginx -d mochiphoto.click -d www.mochiphoto.click
```

Follow prompts:
- Enter email
- Agree to terms
- Choose redirect HTTP to HTTPS (recommended)

#### Auto-renewal:
```bash
sudo certbot renew --dry-run
```

#### Test HTTPS:
```bash
curl https://mochiphoto.click/api/health
```

Now accessible via HTTPS! 🔒 ✅

---

## 🚀 CURRENT APP CONFIGURATION

### Flask App Settings:
```python
# app_pro.py
app.config['SERVER_NAME'] = None  # Allow any domain

# CORS allowed origins
allowed_origins = [
    "*",
    "http://mochiphoto.click",
    "https://mochiphoto.click",
    "http://www.mochiphoto.click",
    "https://www.mochiphoto.click",
    "http://14.225.210.195:5000",
    "http://localhost:5000"
]
```

✅ App already configured for domain!

---

## 🧪 TESTING CHECKLIST

### After DNS Setup:
- [ ] DNS resolves to 14.225.210.195
- [ ] Can ping mochiphoto.click
- [ ] Port 5000 accessible
- [ ] API health check works
- [ ] Dashboard loads
- [ ] WebSocket connects

### After Nginx Setup:
- [ ] Port 80 accessible (no :5000 needed)
- [ ] All routes work
- [ ] Static files load
- [ ] WebSocket works through proxy

### After SSL Setup:
- [ ] HTTPS certificate valid
- [ ] HTTP redirects to HTTPS
- [ ] All features work on HTTPS
- [ ] WebSocket works on WSS

---

## 📝 QUICK TEST COMMANDS

### Test DNS:
```bash
nslookup mochiphoto.click
dig mochiphoto.click +short
ping mochiphoto.click
```

### Test HTTP (Direct):
```bash
curl http://mochiphoto.click:5000/api/health
curl http://mochiphoto.click:5000/
```

### Test HTTP (via Nginx):
```bash
curl http://mochiphoto.click/api/health
curl http://mochiphoto.click/
```

### Test HTTPS:
```bash
curl https://mochiphoto.click/api/health
curl https://mochiphoto.click/
```

### Test API Endpoints:
```bash
# Generate emails
curl -X POST http://mochiphoto.click/api/generate \
  -H "Content-Type: application/json" \
  -d '{"total": 5, "domains": ["gmail.com"]}'

# Validate email
curl -X POST http://mochiphoto.click/api/validate/single \
  -H "Content-Type: application/json" \
  -d '{"email": "test@gmail.com"}'

# Extract emails
curl -X POST http://mochiphoto.click/api/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "Contact: john@example.com"}'
```

---

## 🎯 URLS AFTER SETUP

### Without Nginx:
- Dashboard: http://mochiphoto.click:5000/
- Email Checker: http://mochiphoto.click:5000/checker
- Validator: http://mochiphoto.click:5000/complete
- Generator: http://mochiphoto.click:5000/generator
- API Health: http://mochiphoto.click:5000/api/health

### With Nginx (Recommended):
- Dashboard: http://mochiphoto.click/
- Email Checker: http://mochiphoto.click/checker
- Validator: http://mochiphoto.click/complete
- Generator: http://mochiphoto.click/generator
- API Health: http://mochiphoto.click/api/health

### With SSL:
- Dashboard: https://mochiphoto.click/
- Email Checker: https://mochiphoto.click/checker
- Validator: https://mochiphoto.click/complete
- Generator: https://mochiphoto.click/generator
- API Health: https://mochiphoto.click/api/health

---

## 🔧 TROUBLESHOOTING

### Issue 1: DNS not resolving
**Solution**:
- Wait 30 minutes for propagation
- Clear DNS cache: `sudo systemd-resolve --flush-caches`
- Try different DNS: `8.8.8.8` (Google)

### Issue 2: Port 5000 blocked
**Solution**:
- Check firewall: `sudo ufw allow 5000`
- Check if Flask running: `curl localhost:5000/api/health`

### Issue 3: Nginx not working
**Solution**:
- Check config: `sudo nginx -t`
- Check logs: `sudo tail -f /var/log/nginx/error.log`
- Restart: `sudo systemctl restart nginx`

### Issue 4: SSL certificate fails
**Solution**:
- Ensure port 80 and 443 open
- Check domain ownership
- Use staging first: `certbot --staging`

### Issue 5: WebSocket not connecting
**Solution**:
- Check Nginx WebSocket config
- Verify upgrade headers
- Check browser console for errors

---

## 📊 EXPECTED BEHAVIOR

### Before DNS Setup:
✅ http://14.225.210.195:5000/ - Works  
❌ http://mochiphoto.click:5000/ - Doesn't work (DNS not configured)

### After DNS Setup:
✅ http://14.225.210.195:5000/ - Works  
✅ http://mochiphoto.click:5000/ - Works (DNS propagated)

### After Nginx Setup:
✅ http://14.225.210.195:5000/ - Works  
✅ http://mochiphoto.click:5000/ - Works  
✅ http://mochiphoto.click/ - Works (port 80, no :5000 needed)

### After SSL Setup:
✅ http://mochiphoto.click/ - Redirects to HTTPS  
✅ https://mochiphoto.click/ - Works with secure connection 🔒

---

## 🎉 FINAL CHECKLIST

- [ ] DNS A records configured
- [ ] DNS propagated (check with nslookup)
- [ ] Domain resolves to 14.225.210.195
- [ ] Port 5000 accessible
- [ ] Flask app running
- [ ] API health check works
- [ ] Dashboard loads on domain
- [ ] All features working
- [ ] (Optional) Nginx installed and configured
- [ ] (Optional) SSL certificate installed
- [ ] (Optional) HTTPS working

---

## 📞 SUPPORT

If issues persist:
1. Check Flask logs: `tail -f /path/to/flask.log`
2. Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`
3. Test locally first: `curl localhost:5000/api/health`
4. Verify firewall: `sudo ufw status`
5. Check DNS: `nslookup mochiphoto.click`

---

**Status**: ✅ App configured and ready  
**Next Step**: Configure DNS records  
**ETA**: 5-30 minutes after DNS setup

---

**Last Updated**: 2025-11-22 15:05 UTC  
**Maintained By**: GenSpark AI Developer
