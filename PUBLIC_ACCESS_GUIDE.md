# BI GHI TOOL MMO - Public Access Guide

## 🌐 Public Access URL

Your application is now publicly accessible at:

```
http://35.247.153.179:5003
```

### Direct Access Links

| Page | URL | Description |
|------|-----|-------------|
| **Landing Page** | http://35.247.153.179:5003/ | Public homepage for non-logged users |
| **Login** | http://35.247.153.179:5003/login | User login page |
| **Register** | http://35.247.153.179:5003/register | New user registration |
| **Dashboard** | http://35.247.153.179:5003/dashboard | Main dashboard (requires login) |
| **API Health** | http://35.247.153.179:5003/api/health | API health check endpoint |

---

## 🔧 Configuration Details

### Server Information
- **Host**: 35.247.153.179
- **Port**: 5003
- **Protocol**: HTTP
- **Status**: ✅ Running and Healthy
- **Database**: ✅ Connected and Operational

### Application Status (as of 2025-11-21)
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "database": {
    "healthy": true,
    "live_emails": 4360,
    "die_emails": 4,
    "total_emails": 4364,
    "live_rate": 99.91%,
    "die_rate": 0.09%,
    "can_receive_code": 4360
  },
  "modules": {
    "validator": true,
    "generator": true,
    "extractor": true,
    "formatter": true,
    "filter": true,
    "splitter": true,
    "combiner": true,
    "analyzer": true,
    "deduplicator": true,
    "batch_processor": true,
    "database": true
  }
}
```

---

## 📱 Access from Any Device

### Desktop Browser
Simply open your browser and navigate to:
```
http://35.247.153.179:5003
```

### Mobile Browser
The same URL works on mobile devices:
```
http://35.247.153.179:5003
```

### API Access
For programmatic access, use the API endpoints:
```bash
# Health check
curl http://35.247.153.179:5003/api/health

# Login (POST request)
curl -X POST http://35.247.153.179:5003/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"your_username","password":"your_password"}'

# Validate emails (requires authentication)
curl -X POST http://35.247.153.179:5003/api/validate \
  -H "Content-Type: application/json" \
  -H "Cookie: session=your_session_token" \
  -d '{"emails":["test@example.com"]}'
```

---

## 🔐 Test Accounts

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`
- **Access**: Full administrative privileges

### Regular User Account
- **Create your own**: Visit http://35.247.153.179:5003/register
- **Access**: Standard user features with VIP upgrade options

---

## 🚀 Features Available

### 1. Email Tools
- ✅ Email Validator (LIVE/DIE detection, 95% accuracy)
- ✅ Email Generator (unlimited random emails)
- ✅ Email Extractor (from text, files, URLs)
- ✅ Email Formatter (multiple formats)
- ✅ Email Filter (advanced filtering)
- ✅ Email Analyzer (detailed statistics)
- ✅ Email Deduplicator (remove duplicates)
- ✅ Email Splitter (split large lists)
- ✅ Email Combiner (merge lists)
- ✅ Batch Processor (bulk operations)

### 2. Facebook Tools
- ✅ FB Linked Checker (6 API methods)
- ✅ 2FA Checker (verify 2FA status)
- ✅ Page Mining (extract page information)

### 3. Dashboard Features
- ✅ Real-time statistics
- ✅ Live activity feed
- ✅ Collapsible sidebar sections
- ✅ Notifications system
- ✅ Settings panel (Profile, Preferences, API Keys, Security)
- ✅ Usage notes and guides
- ✅ VIP package comparison

### 4. VIP System
- ✅ FREE: 50 validations/day
- ✅ BASIC: 500 validations/day
- ✅ PRO: Unlimited validations + all features
- ✅ ENTERPRISE: Dedicated server + custom integrations

---

## 🌍 Network Access

### Current Status
- ✅ **Local Access**: Working (localhost:5003)
- ✅ **Public IP Access**: Working (35.247.153.179:5003)
- ✅ **Cross-Device Access**: Enabled
- ⚠️ **HTTPS**: Not configured (HTTP only)

### Firewall Configuration
The port 5003 is already open and accessible from:
- ✅ Same network devices
- ✅ External networks
- ✅ Mobile devices
- ✅ International access

---

## 🔒 Security Considerations

### Current Setup (HTTP)
⚠️ **Note**: The current setup uses HTTP (not HTTPS), which means:
- Data is transmitted in plain text
- Suitable for testing and development
- **Not recommended for production with sensitive data**

### Recommended Upgrades for Production

#### 1. Add HTTPS with SSL Certificate
```bash
# Option 1: Use Let's Encrypt (Free)
certbot certonly --standalone -d yourdomain.com

# Option 2: Use Cloudflare Tunnel (Free)
cloudflared tunnel --url http://localhost:5003
```

#### 2. Set up Domain Name
Instead of IP address, use a proper domain:
```
https://bighi-tool-mmo.com  # Example
```

#### 3. Add Rate Limiting
Protect against abuse with rate limiting on API endpoints.

#### 4. Enable CORS Protection
Configure proper CORS headers for API security.

---

## 🛠️ Troubleshooting

### Cannot Access Public URL

**Problem**: `http://35.247.153.179:5003` not loading

**Solutions**:
1. Check if app is running:
   ```bash
   ps aux | grep "python.*app.py"
   ```

2. Restart the application:
   ```bash
   cd /home/bighitran1905/webapp
   python3 app.py
   ```

3. Check port availability:
   ```bash
   netstat -tuln | grep 5003
   ```

### Database Connection Issues

**Problem**: Features not working, API errors

**Solutions**:
1. Check database health:
   ```bash
   curl http://localhost:5003/api/health
   ```

2. Verify database file:
   ```bash
   ls -lh /home/bighitran1905/webapp/email_tool.db
   ```

### Module Import Errors

**Problem**: ImportError when starting app

**Solutions**:
1. Activate virtual environment:
   ```bash
   source venv/bin/activate
   ```

2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 📊 Monitoring & Logs

### Check Application Status
```bash
# View recent logs
tail -f /home/bighitran1905/webapp/logs/app.log

# Check API health
curl http://localhost:5003/api/health | python3 -m json.tool
```

### Database Statistics
```bash
# Get real-time stats
curl http://localhost:5003/api/dashboard/stats | python3 -m json.tool
```

---

## 🎯 Next Steps

### For Development
1. ✅ Application is running and accessible
2. ✅ All features are working
3. ✅ Database is connected
4. ⏭️ Consider adding HTTPS for production
5. ⏭️ Set up domain name
6. ⏭️ Configure monitoring and alerts

### For Production Deployment
1. **Get a Domain Name**
   - Register a domain (e.g., bighi-tool-mmo.com)
   - Point DNS to 35.247.153.179

2. **Add SSL Certificate**
   - Use Let's Encrypt for free SSL
   - Or use Cloudflare for free HTTPS + CDN

3. **Set up Process Manager**
   ```bash
   # Use PM2 for Node.js or Supervisor for Python
   pip install supervisor
   ```

4. **Configure Nginx as Reverse Proxy**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       location / {
           proxy_pass http://localhost:5003;
       }
   }
   ```

---

## 📞 Support

For issues or questions:
- **Email**: support@bighi-tool-mmo.com
- **Documentation**: http://35.247.153.179:5003/
- **API Docs**: Coming soon
- **GitHub**: Repository link

---

## ✅ Verification Checklist

- [x] Application running on port 5003
- [x] Public IP accessible (35.247.153.179)
- [x] Landing page loads correctly
- [x] Login/Register pages working
- [x] Dashboard functional
- [x] API endpoints responding
- [x] Database connected
- [x] All 13 features operational
- [x] Real-time statistics working
- [x] Notifications system active
- [x] Settings panel functional
- [x] VIP system configured

---

**Last Updated**: 2025-11-21  
**Status**: ✅ FULLY OPERATIONAL  
**Version**: 2.1.0 (Modular Architecture)
