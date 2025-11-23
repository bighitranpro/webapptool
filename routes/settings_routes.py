"""
Settings Routes
API endpoints for system settings management
"""

from flask import Blueprint, render_template, jsonify, request, current_app
from functools import wraps
import sqlite3
import json
import os
from werkzeug.utils import secure_filename
from datetime import datetime

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'ico', 'svg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TODO: Implement proper session check
        # For now, allow all requests (will be secured in production)
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    """Get database connection"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'email_tool.db')
    return sqlite3.connect(db_path)

def get_settings():
    """Get all system settings"""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM system_settings LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return {}

def update_setting(key, value):
    """Update a single setting"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if setting exists
    cursor.execute(f"SELECT COUNT(*) FROM system_settings")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Insert new row
        cursor.execute(f"INSERT INTO system_settings ({key}) VALUES (?)", (value,))
    else:
        # Update existing
        cursor.execute(f"UPDATE system_settings SET {key} = ? WHERE 1=1", (value,))
    
    conn.commit()
    conn.close()

# ==================== ROUTES ====================

@settings_bp.route('/')
@admin_required
def settings_page():
    """Render settings dashboard page"""
    return render_template('settings/settings_dashboard.html')

@settings_bp.route('/api/settings', methods=['GET'])
@admin_required
def api_get_settings():
    """Get all system settings"""
    try:
        settings = get_settings()
        
        # Parse JSON fields
        if settings.get('generator_config'):
            try:
                settings['generator_config'] = json.loads(settings['generator_config'])
            except:
                settings['generator_config'] = {}
        
        if settings.get('allowed_domains'):
            settings['allowed_domains_list'] = settings['allowed_domains'].split(',')
        
        if settings.get('custom_domains'):
            settings['custom_domains_list'] = settings['custom_domains'].split(',')
        
        return jsonify({
            'success': True,
            'settings': settings
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/settings', methods=['PUT'])
@admin_required
def api_update_settings():
    """Update system settings"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build UPDATE query dynamically
        allowed_fields = [
            'tool_name', 'tool_description', 'company_name', 'company_website',
            'support_email', 'support_phone', 'default_email_count', 
            'max_email_count', 'default_locale', 'default_persona'
        ]
        
        updates = []
        values = []
        
        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = ?")
                values.append(data[field])
        
        if updates:
            sql = f"UPDATE system_settings SET {', '.join(updates)} WHERE 1=1"
            cursor.execute(sql, values)
            conn.commit()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Settings updated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/settings/upload-logo', methods=['POST'])
@admin_required
def api_upload_logo():
    """Upload logo file"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'success': False,
                'error': f'File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB'
            }), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"logo_{timestamp}_{filename}"
        
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # Update database
        logo_url = f"/static/uploads/{filename}"
        update_setting('logo_url', logo_url)
        
        return jsonify({
            'success': True,
            'logo_url': logo_url,
            'message': 'Logo uploaded successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/settings/upload-favicon', methods=['POST'])
@admin_required
def api_upload_favicon():
    """Upload favicon file"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"favicon_{timestamp}_{filename}"
        
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # Update database
        favicon_url = f"/static/uploads/{filename}"
        update_setting('favicon_url', favicon_url)
        
        return jsonify({
            'success': True,
            'favicon_url': favicon_url,
            'message': 'Favicon uploaded successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/settings/domains', methods=['GET'])
@admin_required
def api_get_domains():
    """Get domain lists"""
    try:
        settings = get_settings()
        
        allowed = settings.get('allowed_domains', 'gmail.com,yahoo.com,outlook.com').split(',')
        custom = settings.get('custom_domains', '').split(',') if settings.get('custom_domains') else []
        
        return jsonify({
            'success': True,
            'allowed_domains': [d.strip() for d in allowed if d.strip()],
            'custom_domains': [d.strip() for d in custom if d.strip()]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/settings/domains', methods=['PUT'])
@admin_required
def api_update_domains():
    """Update domain lists"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if 'allowed_domains' in data:
            allowed = ','.join(data['allowed_domains'])
            cursor.execute("UPDATE system_settings SET allowed_domains = ?", (allowed,))
        
        if 'custom_domains' in data:
            custom = ','.join(data['custom_domains'])
            cursor.execute("UPDATE system_settings SET custom_domains = ?", (custom,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Domains updated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/settings/generator', methods=['GET'])
@admin_required
def api_get_generator_config():
    """Get generator configuration"""
    try:
        settings = get_settings()
        
        config = {}
        if settings.get('generator_config'):
            try:
                config = json.loads(settings['generator_config'])
            except:
                pass
        
        # Add defaults
        config.setdefault('number_probability', 0.6)
        config.setdefault('year_probability', 0.3)
        config.setdefault('year_range_start', 1980)
        config.setdefault('year_range_end', 2005)
        config.setdefault('dedup', True)
        
        return jsonify({
            'success': True,
            'config': config
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/settings/generator', methods=['PUT'])
@admin_required
def api_update_generator_config():
    """Update generator configuration"""
    try:
        data = request.get_json()
        
        config_json = json.dumps(data)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE system_settings SET generator_config = ?", (config_json,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Generator configuration updated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/settings/smtp', methods=['GET'])
@admin_required
def api_get_smtp():
    """Get SMTP settings"""
    try:
        settings = get_settings()
        
        smtp = {
            'smtp_host': settings.get('smtp_host', ''),
            'smtp_port': settings.get('smtp_port', 587),
            'smtp_user': settings.get('smtp_user', ''),
            'smtp_password': '***' if settings.get('smtp_password') else '',
            'smtp_use_tls': bool(settings.get('smtp_use_tls', 1))
        }
        
        return jsonify({
            'success': True,
            'smtp': smtp
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/settings/smtp', methods=['PUT'])
@admin_required
def api_update_smtp():
    """Update SMTP settings"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        updates = []
        values = []
        
        for field in ['smtp_host', 'smtp_port', 'smtp_user', 'smtp_password', 'smtp_use_tls']:
            if field in data:
                updates.append(f"{field} = ?")
                values.append(data[field])
        
        if updates:
            sql = f"UPDATE system_settings SET {', '.join(updates)}"
            cursor.execute(sql, values)
            conn.commit()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'SMTP settings updated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/settings/notifications', methods=['GET'])
@admin_required
def api_get_notifications():
    """Get notification settings"""
    try:
        settings = get_settings()
        
        return jsonify({
            'success': True,
            'enable_email_notifications': bool(settings.get('enable_email_notifications', 1))
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/settings/notifications', methods=['PUT'])
@admin_required
def api_update_notifications():
    """Update notification settings"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if 'enable_email_notifications' in data:
            value = 1 if data['enable_email_notifications'] else 0
            cursor.execute("UPDATE system_settings SET enable_email_notifications = ?", (value,))
            conn.commit()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Notification settings updated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
