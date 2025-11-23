"""
Bi Tool - Professional Tool Suite for mochiphoto.click v2.1
Modular Architecture with Blueprint Separation
Enhanced with Security & Error Handling
"""

from flask import Flask, jsonify, session
import sys
import os

# Import security utilities
from security_utils import (
    add_security_headers, 
    generate_csrf_token,
    rate_limiter
)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'bi_tool_mochiphoto_secret_2024_secure')
app.config['JSON_AS_ASCII'] = False  # Support Vietnamese characters
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for development
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

# Security configurations
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'


# Add after-request handler for security headers and caching
@app.after_request
def add_header(response):
    """Add security headers and prevent caching"""
    # Add security headers
    response = add_security_headers(response)
    
    # Prevent caching
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    
    return response

# Context processor to inject theme variables
@app.context_processor
def inject_theme_variables():
    """Inject theme CSS variables into all templates"""
    from flask import session
    import sqlite3
    import json
    
    # Default theme
    theme_vars = {
        'primary_color': '#ffd700',
        'secondary_color': '#00d9ff',
        'accent_color': '#ff6b35',
        'background_color': '#0a0e27',
        'text_color': '#ffffff',
        'font_family': 'Inter',
        'font_size_base': '16px',
        'sidebar_width': '280px',
        'border_radius': '12px',
        'animation_speed': '0.3s'
    }
    
    # Try to load user's custom theme
    user_id = session.get('user_id')
    if user_id:
        try:
            conn = sqlite3.connect('email_tool.db')
            cursor = conn.cursor()
            cursor.execute(
                'SELECT theme_config FROM admin_settings WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1',
                (user_id,)
            )
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                custom_theme = json.loads(result[0])
                theme_vars.update(custom_theme)
        except Exception as e:
            print(f"Error loading theme: {e}")
    
    return {'theme_vars': theme_vars}


# Add CSRF token to all templates
@app.context_processor
def inject_csrf_token():
    """Inject CSRF token into all templates"""
    return {'csrf_token': generate_csrf_token}


# Clean up rate limiter periodically
@app.before_request
def cleanup_rate_limiter():
    """Clean up old rate limiter data"""
    import random
    # Clean up on ~1% of requests to avoid overhead
    if random.random() < 0.01:
        rate_limiter.clear_old_data()


# Register Blueprints
from routes import auth_bp, api_bp, dashboard_bp
from app_admin_routes import admin_bp
from routes.settings_routes import settings_bp

app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(settings_bp)


# Enhanced Error Handlers
@app.errorhandler(400)
def bad_request(error):
    """Handle bad requests"""
    return jsonify({
        'success': False,
        'error': 'Bad Request',
        'message': str(error.description) if hasattr(error, 'description') else 'Invalid request data'
    }), 400


@app.errorhandler(401)
def unauthorized(error):
    """Handle unauthorized access"""
    return jsonify({
        'success': False,
        'error': 'Unauthorized',
        'message': 'Authentication required'
    }), 401


@app.errorhandler(403)
def forbidden(error):
    """Handle forbidden access"""
    return jsonify({
        'success': False,
        'error': 'Forbidden',
        'message': 'You do not have permission to access this resource'
    }), 403


@app.errorhandler(404)
def not_found(error):
    """Handle not found errors"""
    return jsonify({
        'success': False,
        'error': 'Not Found',
        'message': 'The requested resource was not found'
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle method not allowed"""
    return jsonify({
        'success': False,
        'error': 'Method Not Allowed',
        'message': 'The HTTP method is not allowed for this endpoint'
    }), 405


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large"""
    return jsonify({
        'success': False,
        'error': 'File Too Large',
        'message': 'The uploaded file exceeds the maximum allowed size (50MB)'
    }), 413


@app.errorhandler(429)
def too_many_requests(error):
    """Handle rate limiting"""
    return jsonify({
        'success': False,
        'error': 'Too Many Requests',
        'message': 'Rate limit exceeded. Please try again later.'
    }), 429


@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    import traceback
    
    # Log the error
    print(f"Internal Server Error: {str(error)}")
    print(traceback.format_exc())
    
    return jsonify({
        'success': False,
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred. Please try again later.'
    }), 500


@app.errorhandler(Exception)
def handle_exception(error):
    """Handle all unhandled exceptions"""
    import traceback
    
    # Log the error
    print(f"Unhandled Exception: {str(error)}")
    print(traceback.format_exc())
    
    # Return generic error to user
    return jsonify({
        'success': False,
        'error': 'Server Error',
        'message': 'An unexpected error occurred. Our team has been notified.'
    }), 500


if __name__ == '__main__':
    # Check if running in production mode
    port = 80 if len(sys.argv) > 1 and sys.argv[1] == 'production' else 5003
    debug_mode = port == 5000
    
    print(f"""
    ╔══════════════════════════════════════════╗
    ║      Bi Tool v2.1 - Enhanced             ║
    ║      mochiphoto.click                    ║
    ║      Security & Performance Optimized    ║
    ╚══════════════════════════════════════════╝
    
    🚀 Server starting on port {port}
    🔧 Debug mode: {debug_mode}
    📦 Modular blueprints loaded:
       ✓ Auth Routes (login, register, logout)
       ✓ API Routes (email tools, validation, etc.)
       ✓ Dashboard Routes (user interface)
       ✓ Admin Routes (admin panel)
       ✓ Settings Routes (user settings)
    
    🔒 Security features:
       ✓ Rate limiting enabled
       ✓ CSRF protection active
       ✓ Security headers configured
       ✓ Input sanitization ready
    
    🌐 Dashboard: http://localhost:{port}/
    🔍 API Health: http://localhost:{port}/api/health
    🛡️  Admin Panel: http://localhost:{port}/admin
    """)
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
