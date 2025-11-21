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
