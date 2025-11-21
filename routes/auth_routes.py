"""
Authentication Routes
Login, Register, Logout endpoints
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from auth_vip import AuthVIPSystem

auth_bp = Blueprint('auth', __name__)
auth_system = AuthVIPSystem()


@auth_bp.route('/')
def index():
    """Show landing page or redirect to dashboard if logged in"""
    if 'session_token' in session:
        session_info = auth_system.verify_session(session['session_token'])
        if session_info.get('valid'):
            return redirect(url_for('dashboard.dashboard_page'))
    return render_template('landing.html')


@auth_bp.route('/login')
def login_page():
    """Login page"""
    if 'session_token' in session:
        session_info = auth_system.verify_session(session['session_token'])
        if session_info.get('valid'):
            return redirect(url_for('dashboard.dashboard_page'))
    return render_template('login.html')


@auth_bp.route('/register')
def register_page():
    """Register page"""
    if 'session_token' in session:
        session_info = auth_system.verify_session(session['session_token'])
        if session_info.get('valid'):
            return redirect(url_for('dashboard.dashboard_page'))
    return render_template('register.html')


@auth_bp.route('/api/auth/login', methods=['POST'])
def api_login():
    """Login API"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        
        result = auth_system.authenticate(
            username, password,
            request.remote_addr,
            request.headers.get('User-Agent', '')
        )
        
        if result['success']:
            session['session_token'] = result['session_token']
            session['user_id'] = result['user_id']
            session['username'] = result['username']
            session['role'] = result['role']
            session.permanent = data.get('remember', False)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@auth_bp.route('/api/auth/register', methods=['POST'])
def api_register():
    """Register new user API"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validate input
        if not username or not email or not password:
            return jsonify({
                'success': False,
                'message': 'Tất cả các trường đều bắt buộc / All fields are required'
            }), 400
        
        if len(username) < 3:
            return jsonify({
                'success': False,
                'message': 'Tên đăng nhập phải có ít nhất 3 ký tự / Username must be at least 3 characters'
            }), 400
        
        if len(password) < 6:
            return jsonify({
                'success': False,
                'message': 'Mật khẩu phải có ít nhất 6 ký tự / Password must be at least 6 characters'
            }), 400
        
        if '@' not in email or '.' not in email:
            return jsonify({
                'success': False,
                'message': 'Email không hợp lệ / Invalid email address'
            }), 400
        
        # Create user with FREE VIP level (0)
        result = auth_system.create_user(
            username=username,
            password=password,
            email=email,
            role='user',
            vip_level=0
        )
        
        if result.get('success'):
            user_id = result.get('user_id')
            auth_system.log_activity(
                user_id=user_id,
                activity_type='user_registered',
                description=f'New user registered: {username}',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )
            
            return jsonify({
                'success': True,
                'message': 'Đăng ký thành công! Đang chuyển hướng... / Registration successful! Redirecting...',
                'user_id': user_id
            })
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi đăng ký / Registration error: {str(e)}'
        }), 500


@auth_bp.route('/api/auth/logout', methods=['POST'])
def api_logout():
    """Logout API"""
    if 'session_token' in session:
        auth_system.logout(session['session_token'])
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out'})
