"""
BI GHI TOOL MMO - Professional Email Tool Suite v2.1
Modular Architecture with Blueprint Separation
"""

from flask import Flask
import sys
import os

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'bighi_tool_mmo_secret_2024_secure')
app.config['JSON_AS_ASCII'] = False  # Support Vietnamese characters
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for development
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours


# Add after-request handler to prevent caching
@app.after_request
def add_header(response):
    """Add headers to prevent caching"""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


# Register Blueprints
from routes import auth_bp, api_bp, dashboard_bp
from app_admin_routes import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(admin_bp)


# Error Handlers
@app.errorhandler(404)
def not_found(error):
    from flask import jsonify
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    from flask import jsonify
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # Check if running in production mode
    port = 80 if len(sys.argv) > 1 and sys.argv[1] == 'production' else 5003
    debug_mode = port == 5000
    
    print(f"""
    ╔══════════════════════════════════════════╗
    ║      Email Tool Pro v2.1 - Modular       ║
    ║      Optimized Architecture              ║
    ╚══════════════════════════════════════════╝
    
    🚀 Server starting on port {port}
    🔧 Debug mode: {debug_mode}
    📦 Modular blueprints loaded:
       ✓ Auth Routes (login, register, logout)
       ✓ API Routes (email tools, validation, etc.)
       ✓ Dashboard Routes (user interface)
       ✓ Admin Routes (admin panel)
    
    🌐 Dashboard: http://localhost:{port}/
    🔍 API Health: http://localhost:{port}/api/health
    🛡️  Admin Panel: http://localhost:{port}/admin
    """)
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
