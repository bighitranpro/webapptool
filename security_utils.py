"""
Security utilities for Bi Tool v2.1
Includes rate limiting, CSRF protection, and input sanitization
"""

import hashlib
import time
import re
from functools import wraps
from flask import request, jsonify, session, abort
from collections import defaultdict
from datetime import datetime, timedelta
import secrets

# ==========================================
# RATE LIMITING
# ==========================================

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.blocked_ips = {}
        
    def is_rate_limited(self, identifier, max_requests=60, window_seconds=60):
        """
        Check if identifier (IP/user) has exceeded rate limit
        
        Args:
            identifier: IP address or user ID
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            tuple: (is_limited, remaining_requests, reset_time)
        """
        current_time = time.time()
        
        # Check if IP is blocked
        if identifier in self.blocked_ips:
            block_until = self.blocked_ips[identifier]
            if current_time < block_until:
                return True, 0, int(block_until)
            else:
                # Unblock
                del self.blocked_ips[identifier]
        
        # Clean old requests outside window
        cutoff_time = current_time - window_seconds
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > cutoff_time
        ]
        
        # Check rate limit
        request_count = len(self.requests[identifier])
        
        if request_count >= max_requests:
            # Block for 5 minutes if exceeded
            self.blocked_ips[identifier] = current_time + 300
            return True, 0, int(current_time + 300)
        
        # Record this request
        self.requests[identifier].append(current_time)
        
        remaining = max_requests - request_count - 1
        reset_time = int(current_time + window_seconds)
        
        return False, remaining, reset_time
    
    def clear_old_data(self):
        """Clear old data to prevent memory leaks"""
        current_time = time.time()
        
        # Clear old requests (older than 1 hour)
        cutoff = current_time - 3600
        for identifier in list(self.requests.keys()):
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > cutoff
            ]
            if not self.requests[identifier]:
                del self.requests[identifier]
        
        # Clear expired blocks
        for identifier in list(self.blocked_ips.keys()):
            if current_time >= self.blocked_ips[identifier]:
                del self.blocked_ips[identifier]

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(max_requests=60, window_seconds=60):
    """
    Decorator for rate limiting endpoints
    
    Usage:
        @app.route('/api/endpoint')
        @rate_limit(max_requests=10, window_seconds=60)
        def endpoint():
            return 'OK'
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Get identifier (IP or user ID)
            if 'user_id' in session:
                identifier = f"user_{session['user_id']}"
            else:
                identifier = request.remote_addr
            
            # Check rate limit
            is_limited, remaining, reset_time = rate_limiter.is_rate_limited(
                identifier, max_requests, window_seconds
            )
            
            if is_limited:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Try again later.',
                    'reset_at': reset_time
                }), 429
            
            # Add rate limit headers
            response = f(*args, **kwargs)
            if isinstance(response, tuple):
                response_obj, status_code = response[0], response[1]
            else:
                response_obj = response
                status_code = 200
            
            # Add headers if response is json-like
            if hasattr(response_obj, 'headers'):
                response_obj.headers['X-RateLimit-Limit'] = str(max_requests)
                response_obj.headers['X-RateLimit-Remaining'] = str(remaining)
                response_obj.headers['X-RateLimit-Reset'] = str(reset_time)
            
            if isinstance(response, tuple):
                return response_obj, status_code
            return response_obj
        
        return wrapped
    return decorator

# ==========================================
# CSRF PROTECTION
# ==========================================

def generate_csrf_token():
    """Generate a CSRF token"""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']

def validate_csrf_token(token):
    """Validate CSRF token"""
    if 'csrf_token' not in session:
        return False
    return secrets.compare_digest(session['csrf_token'], token)

def csrf_protect(f):
    """
    Decorator for CSRF protection on POST/PUT/DELETE requests
    
    Usage:
        @app.route('/api/endpoint', methods=['POST'])
        @csrf_protect
        def endpoint():
            return 'OK'
    """
    @wraps(f)
    def wrapped(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            # Get token from header or form data
            token = request.headers.get('X-CSRF-Token')
            if not token:
                token = request.form.get('csrf_token')
            if not token:
                token = request.json.get('csrf_token') if request.is_json else None
            
            if not token or not validate_csrf_token(token):
                return jsonify({
                    'error': 'CSRF validation failed',
                    'message': 'Invalid or missing CSRF token'
                }), 403
        
        return f(*args, **kwargs)
    return wrapped

# ==========================================
# INPUT SANITIZATION
# ==========================================

class InputSanitizer:
    """Sanitize user inputs to prevent XSS and SQL injection"""
    
    # Patterns for validation
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{3,50}$')
    SAFE_STRING_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_.,!?@#()]+$')
    
    # Dangerous characters/patterns
    DANGEROUS_PATTERNS = [
        r'<script',
        r'javascript:',
        r'onerror=',
        r'onclick=',
        r'onload=',
        r'eval\(',
        r'document\.',
        r'window\.',
        r'--',  # SQL comment
        r';',   # SQL statement separator (in suspicious contexts)
        r'DROP\s+TABLE',
        r'DELETE\s+FROM',
        r'INSERT\s+INTO',
        r'UPDATE\s+.*SET',
    ]
    
    @staticmethod
    def sanitize_html(text):
        """Remove HTML tags and dangerous characters"""
        if not text:
            return text
        
        # Convert to string
        text = str(text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Check for dangerous patterns
        text_lower = text.lower()
        for pattern in InputSanitizer.DANGEROUS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                # Remove the dangerous part
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Escape special characters
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        text = text.replace('"', '&quot;').replace("'", '&#39;')
        
        return text.strip()
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not email:
            return False
        email = str(email).strip().lower()
        return bool(InputSanitizer.EMAIL_PATTERN.match(email))
    
    @staticmethod
    def validate_username(username):
        """Validate username format"""
        if not username:
            return False
        username = str(username).strip()
        return bool(InputSanitizer.USERNAME_PATTERN.match(username))
    
    @staticmethod
    def sanitize_filename(filename):
        """Sanitize filename to prevent directory traversal"""
        if not filename:
            return 'unnamed_file'
        
        # Remove path separators
        filename = str(filename).replace('/', '_').replace('\\', '_')
        
        # Remove dangerous characters
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')
        
        return filename
    
    @staticmethod
    def sanitize_sql_like_pattern(pattern):
        """Escape special characters in SQL LIKE patterns"""
        if not pattern:
            return pattern
        
        # Escape SQL LIKE special characters
        pattern = str(pattern).replace('%', '\\%').replace('_', '\\_')
        return pattern
    
    @staticmethod
    def validate_integer(value, min_val=None, max_val=None):
        """Validate and sanitize integer input"""
        try:
            value = int(value)
            if min_val is not None and value < min_val:
                return None
            if max_val is not None and value > max_val:
                return None
            return value
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def sanitize_dict(data, allowed_keys=None):
        """Sanitize dictionary values"""
        if not isinstance(data, dict):
            return {}
        
        sanitized = {}
        for key, value in data.items():
            # Skip if key not allowed
            if allowed_keys and key not in allowed_keys:
                continue
            
            # Sanitize based on type
            if isinstance(value, str):
                sanitized[key] = InputSanitizer.sanitize_html(value)
            elif isinstance(value, (int, float, bool)):
                sanitized[key] = value
            elif isinstance(value, dict):
                sanitized[key] = InputSanitizer.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    InputSanitizer.sanitize_html(item) if isinstance(item, str) else item
                    for item in value
                ]
        
        return sanitized

# ==========================================
# SECURITY HEADERS
# ==========================================

def add_security_headers(response):
    """Add security headers to response"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self';"
    )
    return response

# ==========================================
# PASSWORD SECURITY
# ==========================================

def hash_password(password):
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${password_hash}"

def verify_password(password, hashed_password):
    """Verify password against hash"""
    try:
        salt, password_hash = hashed_password.split('$')
        computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return secrets.compare_digest(computed_hash, password_hash)
    except:
        return False

def check_password_strength(password):
    """
    Check password strength
    
    Returns:
        tuple: (is_strong, issues[])
    """
    issues = []
    
    if len(password) < 8:
        issues.append("Mật khẩu phải có ít nhất 8 ký tự")
    
    if not re.search(r'[A-Z]', password):
        issues.append("Mật khẩu phải có ít nhất 1 chữ hoa")
    
    if not re.search(r'[a-z]', password):
        issues.append("Mật khẩu phải có ít nhất 1 chữ thường")
    
    if not re.search(r'[0-9]', password):
        issues.append("Mật khẩu phải có ít nhất 1 số")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        issues.append("Mật khẩu phải có ít nhất 1 ký tự đặc biệt")
    
    return len(issues) == 0, issues

# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def get_client_ip():
    """Get real client IP address (considering proxies)"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr

def log_security_event(event_type, details, severity='INFO'):
    """Log security-related events"""
    timestamp = datetime.now().isoformat()
    ip = get_client_ip()
    user_id = session.get('user_id', 'anonymous')
    
    log_entry = {
        'timestamp': timestamp,
        'event_type': event_type,
        'severity': severity,
        'ip': ip,
        'user_id': user_id,
        'details': details
    }
    
    # TODO: Write to security log file or database
    print(f"[SECURITY {severity}] {event_type}: {details} (IP: {ip}, User: {user_id})")
    
    return log_entry
