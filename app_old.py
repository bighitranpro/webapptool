from flask import Flask, render_template, request, jsonify
import re
import random
import string
import hashlib
from datetime import datetime
import uuid
import dns.resolver
import socket
from collections import Counter
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Support Vietnamese characters

# Các hàm xử lý Email Tool

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def extract_facebook_email(text):
    """Extract Facebook emails from text"""
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]*facebook[A-Za-z0-9.-]*\.[A-Za-z]{2,}\b'
    emails = re.findall(pattern, text, re.IGNORECASE)
    return list(set(emails))

def check_facebook_code_email(email):
    """Check if email can receive Facebook verification code"""
    valid_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'icloud.com', 
                     'protonmail.com', 'mail.com', 'zoho.com', 'aol.com']
    if validate_email(email):
        domain = email.split('@')[1].lower()
        is_valid = domain in valid_domains or 'facebook.com' in domain
        
        # Check MX records for extra validation
        has_mx = check_mx_record(domain)
        
        return {
            "can_receive": is_valid and has_mx,
            "domain": domain,
            "has_mx_record": has_mx,
            "is_trusted_provider": domain in valid_domains,
            "details": "Email có thể nhận mã" if (is_valid and has_mx) else "Email không thể nhận mã"
        }
    return {
        "can_receive": False,
        "error": "Invalid email format"
    }

def check_mx_record(domain):
    """Check if domain has MX record"""
    try:
        dns.resolver.resolve(domain, 'MX')
        return True
    except:
        return False

def validate_email_advanced(email):
    """Advanced email validation with detailed checks"""
    if not validate_email(email):
        return {"valid": False, "message": "Invalid email format"}
    
    local, domain = email.split('@')
    
    # Check various rules
    checks = {
        "format": True,
        "local_length": len(local) <= 64,
        "domain_length": len(domain) <= 255,
        "no_double_dots": '..' not in email,
        "valid_chars": all(c.isalnum() or c in '._%+-@' for c in email),
        "has_mx_record": check_mx_record(domain),
        "starts_with_letter": local[0].isalpha() if local else False
    }
    
    # Calculate email strength score
    strength_score = sum([1 for v in checks.values() if v]) / len(checks) * 100
    
    all_valid = all(checks.values())
    return {
        "valid": all_valid,
        "email": email,
        "checks": checks,
        "strength_score": round(strength_score, 2),
        "message": "Valid email" if all_valid else "Email has validation issues",
        "recommendation": get_email_recommendation(checks)
    }

def get_email_recommendation(checks):
    """Get recommendation based on checks"""
    if all(checks.values()):
        return "✅ Email hoàn hảo, đạt tất cả tiêu chuẩn!"
    elif not checks.get('has_mx_record'):
        return "⚠️ Domain không có MX record, email có thể không nhận được thư"
    elif not checks.get('starts_with_letter'):
        return "⚠️ Nên bắt đầu email bằng chữ cái"
    else:
        return "⚠️ Email có một số vấn đề cần khắc phục"

def extract_account_info_from_email(email):
    """Extract account information from Facebook email"""
    if not validate_email(email):
        return {"error": "Invalid email format"}
    
    local, domain = email.split('@')
    
    return {
        "email": email,
        "username": local,
        "domain": domain,
        "is_facebook": 'facebook.com' in domain.lower(),
        "potential_name": local.replace('.', ' ').replace('_', ' ').title(),
        "created_at": datetime.now().isoformat()
    }

def check_valid_facebook_email(email):
    """Check if email is valid for Facebook registration"""
    if not validate_email(email):
        return {"valid": False, "reason": "Invalid email format"}
    
    domain = email.split('@')[1].lower()
    
    # Blacklisted domains
    blacklist = ['tempmail.com', 'guerrillamail.com', 'throwaway.email', '10minutemail.com']
    
    if any(bl in domain for bl in blacklist):
        return {"valid": False, "reason": "Temporary email service not allowed"}
    
    return {
        "valid": True,
        "email": email,
        "domain": domain,
        "recommended": domain in ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
    }

def filter_and_split_emails(text, remove_duplicates=True):
    """Extract and filter emails from text"""
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    emails = re.findall(pattern, text)
    
    if remove_duplicates:
        emails = list(set(emails))
    
    return {
        "total_found": len(emails),
        "emails": emails,
        "valid_emails": [e for e in emails if validate_email(e)]
    }

def classify_email(email):
    """Classify email into categories"""
    if not validate_email(email):
        return {"error": "Invalid email"}
    
    domain = email.split('@')[1].lower()
    
    categories = {
        "social_media": ['facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com'],
        "free_email": ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com'],
        "business": ['company.com', 'corp.com', 'enterprise.com'],
        "temporary": ['tempmail.com', 'guerrillamail.com', '10minutemail.com']
    }
    
    email_type = "custom"
    for category, domains in categories.items():
        if any(d in domain for d in domains):
            email_type = category
            break
    
    return {
        "email": email,
        "type": email_type,
        "domain": domain,
        "provider": domain.split('.')[0].title()
    }

def generate_random_email(count=1, include_numbers=True, style='random'):
    """Generate random email addresses with different styles"""
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com']
    emails = []
    
    first_names = ['john', 'jane', 'alex', 'sam', 'chris', 'jordan', 'taylor', 'morgan']
    last_names = ['smith', 'johnson', 'williams', 'brown', 'davis', 'miller', 'wilson']
    
    for _ in range(count):
        if style == 'realistic':
            # Generate realistic looking email
            first = random.choice(first_names)
            last = random.choice(last_names)
            separator = random.choice(['.', '_', ''])
            username = f"{first}{separator}{last}"
            if include_numbers:
                username += str(random.randint(1, 999))
        else:
            # Random style
            username_length = random.randint(6, 12)
            chars = string.ascii_lowercase
            if include_numbers:
                chars += string.digits
            username = ''.join(random.choice(chars) for _ in range(username_length))
        
        domain = random.choice(domains)
        email = f"{username}@{domain}"
        emails.append(email)
    
    return {
        "count": len(emails),
        "emails": emails,
        "style": style
    }

def scan_email_info(email):
    """Scan and extract detailed information from email"""
    if not validate_email(email):
        return {"error": "Invalid email format"}
    
    local, domain = email.split('@')
    
    # Generate hashes for privacy
    email_hash_md5 = hashlib.md5(email.encode()).hexdigest()
    email_hash_sha256 = hashlib.sha256(email.encode()).hexdigest()
    
    # Analyze username patterns
    char_analysis = Counter(local)
    
    # Check email pattern
    pattern_type = detect_email_pattern(local)
    
    info = {
        "email": email,
        "hashes": {
            "md5": email_hash_md5,
            "sha256": email_hash_sha256
        },
        "username": local,
        "domain": domain,
        "domain_parts": domain.split('.'),
        "tld": domain.split('.')[-1],
        "analysis": {
            "has_numbers": any(c.isdigit() for c in local),
            "has_dots": '.' in local,
            "has_underscores": '_' in local,
            "has_hyphens": '-' in local,
            "username_length": len(local),
            "char_count": dict(char_analysis.most_common(5)),
            "pattern_type": pattern_type
        },
        "security": {
            "complexity_score": calculate_email_complexity(local),
            "is_common_pattern": is_common_email_pattern(local)
        },
        "scan_id": str(uuid.uuid4()),
        "scan_date": datetime.now().isoformat()
    }
    
    # Try to extract name from email
    name_parts = re.split(r'[._\-\d]', local)
    potential_names = [part.title() for part in name_parts if len(part) > 2]
    if potential_names:
        info["potential_name"] = " ".join(potential_names[:2])
    
    # Check if domain has MX record
    info["domain_valid"] = check_mx_record(domain)
    
    return info

def detect_email_pattern(local):
    """Detect email username pattern"""
    if re.match(r'^[a-z]+\.[a-z]+$', local):
        return "firstname.lastname"
    elif re.match(r'^[a-z]+_[a-z]+$', local):
        return "firstname_lastname"
    elif re.match(r'^[a-z]+\d+$', local):
        return "name_with_numbers"
    elif re.match(r'^[a-z]+$', local):
        return "simple_name"
    else:
        return "mixed_pattern"

def calculate_email_complexity(local):
    """Calculate email complexity score"""
    score = 0
    if len(local) >= 8: score += 20
    if any(c.isupper() for c in local): score += 15
    if any(c.isdigit() for c in local): score += 20
    if any(c in '._-' for c in local): score += 15
    if len(set(local)) > len(local) * 0.6: score += 30  # Character diversity
    return min(score, 100)

def is_common_email_pattern(local):
    """Check if email follows common patterns"""
    common_patterns = ['test', 'admin', 'info', 'support', 'contact', 'user']
    return any(pattern in local.lower() for pattern in common_patterns)

def extract_hotmail_yahoo_gmail(text):
    """Extract emails from Hotmail, Yahoo, and Gmail"""
    pattern = r'\b[A-Za-z0-9._%+-]+@(gmail|yahoo|hotmail|outlook)\.[A-Za-z]{2,}\b'
    emails = re.findall(pattern, text, re.IGNORECASE)
    
    categorized = {
        "gmail": [],
        "yahoo": [],
        "hotmail": [],
        "outlook": []
    }
    
    all_emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', text)
    
    for email in all_emails:
        email_lower = email.lower()
        if 'gmail.com' in email_lower:
            categorized["gmail"].append(email)
        elif 'yahoo.com' in email_lower or 'yahoo' in email_lower:
            categorized["yahoo"].append(email)
        elif 'hotmail.com' in email_lower:
            categorized["hotmail"].append(email)
        elif 'outlook.com' in email_lower:
            categorized["outlook"].append(email)
    
    return {
        "total": sum(len(v) for v in categorized.values()),
        "categorized": categorized,
        "all_emails": list(set(all_emails))
    }

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/validate-email', methods=['POST'])
def api_validate_email():
    data = request.json
    email = data.get('email', '')
    return jsonify(validate_email_advanced(email))

@app.route('/api/extract-facebook-email', methods=['POST'])
def api_extract_facebook_email():
    data = request.json
    text = data.get('text', '')
    emails = extract_facebook_email(text)
    return jsonify({"emails": emails, "count": len(emails)})

@app.route('/api/check-facebook-code', methods=['POST'])
def api_check_facebook_code():
    data = request.json
    email = data.get('email', '')
    result = check_facebook_code_email(email)
    result['email'] = email
    return jsonify(result)

@app.route('/api/extract-account-info', methods=['POST'])
def api_extract_account_info():
    data = request.json
    email = data.get('email', '')
    return jsonify(extract_account_info_from_email(email))

@app.route('/api/check-valid-facebook', methods=['POST'])
def api_check_valid_facebook():
    data = request.json
    email = data.get('email', '')
    return jsonify(check_valid_facebook_email(email))

@app.route('/api/filter-emails', methods=['POST'])
def api_filter_emails():
    data = request.json
    text = data.get('text', '')
    remove_duplicates = data.get('remove_duplicates', True)
    return jsonify(filter_and_split_emails(text, remove_duplicates))

@app.route('/api/classify-email', methods=['POST'])
def api_classify_email():
    data = request.json
    email = data.get('email', '')
    return jsonify(classify_email(email))

@app.route('/api/generate-random-email', methods=['POST'])
def api_generate_random_email():
    data = request.json
    count = data.get('count', 1)
    include_numbers = data.get('include_numbers', True)
    style = data.get('style', 'random')
    return jsonify(generate_random_email(count, include_numbers, style))

@app.route('/api/bulk-validate', methods=['POST'])
def api_bulk_validate():
    """Validate multiple emails at once"""
    data = request.json
    emails = data.get('emails', [])
    
    results = []
    for email in emails:
        result = validate_email_advanced(email.strip())
        results.append(result)
    
    # Statistics
    valid_count = sum(1 for r in results if r.get('valid'))
    invalid_count = len(results) - valid_count
    
    return jsonify({
        "total": len(results),
        "valid": valid_count,
        "invalid": invalid_count,
        "results": results
    })

@app.route('/api/email-statistics', methods=['POST'])
def api_email_statistics():
    """Get statistics from list of emails"""
    data = request.json
    text = data.get('text', '')
    
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', text)
    
    domains = [e.split('@')[1].lower() for e in emails]
    domain_stats = Counter(domains)
    
    # Provider statistics
    providers = {
        'gmail': sum(1 for d in domains if 'gmail.com' in d),
        'yahoo': sum(1 for d in domains if 'yahoo' in d),
        'hotmail': sum(1 for d in domains if 'hotmail.com' in d),
        'outlook': sum(1 for d in domains if 'outlook.com' in d),
        'other': 0
    }
    providers['other'] = len(emails) - sum(providers.values())
    
    return jsonify({
        "total_emails": len(emails),
        "unique_emails": len(set(emails)),
        "unique_domains": len(set(domains)),
        "top_domains": dict(domain_stats.most_common(10)),
        "provider_distribution": providers
    })

@app.route('/api/scan-email', methods=['POST'])
def api_scan_email():
    data = request.json
    email = data.get('email', '')
    return jsonify(scan_email_info(email))

@app.route('/api/extract-providers', methods=['POST'])
def api_extract_providers():
    data = request.json
    text = data.get('text', '')
    return jsonify(extract_hotmail_yahoo_gmail(text))

if __name__ == '__main__':
    # Changed to port 80 to bypass GCP firewall (port 80 is open by default)
    import sys
    port = 80 if len(sys.argv) > 1 and sys.argv[1] == 'production' else 5000
    debug_mode = port == 5000
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
