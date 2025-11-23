# 🔌 BiTool API Guide

Quick reference for using BiTool APIs

---

## 🌐 Base URL
```
Production: http://14.225.210.195:5003
Local: http://localhost:5003
```

---

## 📧 Email Validation API

### Validate Emails
```bash
POST /api/validate
Content-Type: application/json

{
  "emails": ["test@gmail.com", "user@yahoo.com"],
  "options": {
    "check_mx": true,
    "check_smtp": true,
    "max_workers": 10,
    "use_cache": true
  }
}
```

**Response**:
```json
{
  "success": true,
  "stats": {
    "total": 2,
    "live": 2,
    "die": 0,
    "can_receive_code": 2
  },
  "results": {
    "live": [...],
    "die": [...],
    "unknown": [...]
  }
}
```

---

## 🎲 Email Generation API

### Generate Random Emails
```bash
POST /api/generate
Content-Type: application/json

{
  "email_type": "random",
  "text": "user",
  "total": 10,
  "domains": ["gmail.com", "yahoo.com"],
  "char_type": "lowercase",
  "number_type": "suffix"
}
```

**Parameters**:
- `email_type`: random, name_based, number_based, mixed
- `char_type`: lowercase, uppercase, mixed, alphanumeric
- `number_type`: prefix, suffix, middle, random_position, no_numbers

---

## 📝 Email Template API

### List All Templates
```bash
GET /api/templates/list
GET /api/templates/list?category=business
```

### Get Template Categories
```bash
GET /api/templates/categories
```

### Search Templates
```bash
GET /api/templates/search?q=vietnamese
```

### Generate from Template
```bash
POST /api/templates/generate
Content-Type: application/json

{
  "template_id": "business_standard",
  "variables": {
    "firstname": "John",
    "lastname": "Smith",
    "domain": "company.com"
  },
  "count": 10
}
```

**Popular Templates**:
- `business_standard`: john.smith@company.com
- `business_initial`: jsmith@company.com
- `personal_casual`: john123@gmail.com
- `vietnamese_year`: nguyenvan1995@gmail.com
- `marketing_campaign`: spring_sale_001@marketing.com

---

## 🎯 Facebook Tools API

### Check Facebook Linked
```bash
POST /api/fb-check
Content-Type: application/json

{
  "emails": ["test@gmail.com"],
  "options": {
    "api_type": "api1",
    "max_workers": 100,
    "start_from": 0,
    "check_code_68": true
  }
}
```

**API Types**: api1, api2, api3, api4, api5, api6, random

**Response**:
```json
{
  "success": true,
  "stats": {
    "total": 1,
    "linked": 1,
    "hidden_linked": 0,
    "not_linked": 0,
    "code6_count": 1,
    "code8_count": 0
  },
  "results": {
    "linked": [...],
    "hidden_linked": [...],
    "not_linked": [...]
  }
}
```

### Check 2FA & Pages
```bash
POST /api/check-2fa
Content-Type: application/json

{
  "accounts": ["email1:password1", "email2:password2"],
  "options": {
    "api_type": "api1",
    "password_pattern": "1|@|.|#|*|5|*|!|?",
    "validate_pattern": true,
    "max_workers": 200
  }
}
```

---

## 📊 Progress Tracking API

### Get Task Progress
```bash
GET /api/progress/{task_id}
```

### Get All Tasks
```bash
GET /api/progress/all
GET /api/progress/active  # Only running tasks
```

### Control Tasks
```bash
POST /api/progress/{task_id}/pause
POST /api/progress/{task_id}/resume
POST /api/progress/{task_id}/cancel
DELETE /api/progress/{task_id}
```

### Get Statistics
```bash
GET /api/progress/statistics
```

**Response**:
```json
{
  "statistics": {
    "total_tasks": 5,
    "running": 2,
    "completed": 3,
    "total_processed": 1500,
    "total_errors": 10
  }
}
```

---

## 🔍 Other Tools API

### Extract Emails
```bash
POST /api/extract
{
  "text": "Contact us at test@gmail.com or info@company.com",
  "options": {
    "remove_dups": true,
    "filter_domains": ["gmail.com"],
    "filter_pattern": "test.*"
  }
}
```

### Format Emails
```bash
POST /api/format
{
  "emails": ["TEST@GMAIL.COM"],
  "case_format": "lowercase",
  "sort_type": "alphabetical",
  "new_domain": "company.com"
}
```

### Deduplicate Emails
```bash
POST /api/deduplicate
{
  "emails": ["test@gmail.com", "TEST@GMAIL.COM"],
  "method": "case_insensitive",
  "keep_strategy": "first"
}
```

### Analyze Emails
```bash
POST /api/analyze
{
  "emails": ["test@gmail.com", "user@yahoo.com"]
}
```

---

## 🏢 Page Mining API

### Mine Pages from UIDs
```bash
POST /api/page-mining
Content-Type: application/json

{
  "uids": ["100001234567890"],
  "options": {
    "max_workers": 100,
    "filters": {
      "has_ads": true,
      "country": "Vietnam",
      "min_likes": 1000,
      "has_email": true
    }
  }
}
```

---

## 📈 Dashboard & Stats API

### Get Dashboard Stats
```bash
GET /api/dashboard/stats
```

### Get Database Stats
```bash
GET /api/db/stats
```

### Search Emails in Database
```bash
POST /api/db/search
{
  "query": "gmail.com"
}
```

---

## ❤️ Health Check

```bash
GET /api/health
```

**Response**:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2025-11-23T20:00:00",
  "database": {
    "healthy": true,
    "stats": {
      "total": 4364,
      "live": 4360,
      "die": 4,
      "live_rate": 99.91
    }
  },
  "modules": {
    "validator": true,
    "generator": true,
    ...
  }
}
```

---

## 🔐 Authentication

Most endpoints require authentication:

```bash
# Include session cookie or token
-H "Cookie: session=your_session_token"
```

For `/api/health` and public endpoints, no auth required.

---

## 📝 Rate Limiting

- General endpoints: **10 requests/second**
- API endpoints: **5 requests/second**
- Auth endpoints: **3 requests/second**

429 Too Many Requests if exceeded.

---

## 🐛 Error Responses

```json
{
  "success": false,
  "error": "Error Type",
  "message": "Detailed error message"
}
```

**Common HTTP Codes**:
- `200`: Success
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `429`: Too Many Requests
- `500`: Internal Server Error

---

## 💡 Tips

1. **Batch Processing**: Use max_workers to control concurrency
2. **Caching**: Enable use_cache for better performance
3. **Progress Tracking**: Create tasks for long-running operations
4. **Templates**: Use templates for consistent email generation
5. **Validation**: Always validate emails before using in production

---

## 📚 Examples

### Complete Email Validation Flow
```bash
# 1. Generate emails
curl -X POST http://localhost:5003/api/generate \
  -H "Content-Type: application/json" \
  -d '{"total": 10, "domains": ["gmail.com"]}'

# 2. Validate emails
curl -X POST http://localhost:5003/api/validate \
  -H "Content-Type: application/json" \
  -d '{"emails": [...], "options": {"check_mx": true}}'

# 3. Check Facebook linked
curl -X POST http://localhost:5003/api/fb-check \
  -H "Content-Type: application/json" \
  -d '{"emails": [...], "options": {"api_type": "api1"}}'
```

---

**🚀 Happy Coding!**
