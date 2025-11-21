"""
Authentication Routes for BI GHI TOOL MMO
Add these routes to main app.py
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from auth import AuthSystem, login_required, admin_required
import os

def init_auth_routes(app):
    """Initialize authentication routes"""
    
    # Set secret key for sessions
    app.secret_key = os.environ.get('SECRET_KEY', 'bighi_tool_mmo_secret_key_2024')
    
    # Initialize auth system
    auth = AuthSystem()
    
    @app.route('/')
    def index():
        """Redirect to login if not authenticated, else dashboard"""
        if 'session_token' in session:
            session_info = auth.verify_session(session['session_token'])
            if session_info.get('valid'):
                return redirect(url_for('dashboard'))
        return redirect(url_for('login_page'))
    
    @app.route('/login')
    def login_page():
        """Login page"""
        # If already logged in, redirect to dashboard
        if 'session_token' in session:
            session_info = auth.verify_session(session['session_token'])
            if session_info.get('valid'):
                return redirect(url_for('dashboard'))
        return render_template('login.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Main dashboard (protected)"""
        session_info = auth.verify_session(session['session_token'])
        user_stats = auth.get_user_stats(session_info['user_id'])
        return render_template('dashboard.html', user=session_info, stats=user_stats)
    
    @app.route('/api/auth/login', methods=['POST'])
    def api_login():
        """Login API endpoint"""
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            remember = data.get('remember', False)
            
            if not username or not password:
                return jsonify({
                    'success': False,
                    'message': 'Username and password required'
                }), 400
            
            # Get client info
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent', '')
            
            # Authenticate
            result = auth.authenticate(username, password, ip_address, user_agent)
            
            if result['success']:
                # Set session
                session['session_token'] = result['session_token']
                session['user_id'] = result['user_id']
                session['username'] = result['username']
                session['role'] = result['role']
                
                if remember:
                    session.permanent = True
                
                return jsonify(result)
            else:
                return jsonify(result), 401
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
    
    @app.route('/api/auth/logout', methods=['POST'])
    def api_logout():
        """Logout API endpoint"""
        try:
            if 'session_token' in session:
                auth.logout(session['session_token'])
            session.clear()
            return jsonify({
                'success': True,
                'message': 'Logged out successfully'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
    
    @app.route('/api/auth/register', methods=['POST'])
    def api_register():
        """Register new user (admin only or open registration)"""
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')
            full_name = data.get('full_name')
            
            if not username or not password:
                return jsonify({
                    'success': False,
                    'message': 'Username and password required'
                }), 400
            
            result = auth.create_user(username, password, email, full_name)
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
    
    @app.route('/api/auth/profile', methods=['GET'])
    @login_required
    def api_profile():
        """Get user profile"""
        try:
            session_info = auth.verify_session(session['session_token'])
            user_stats = auth.get_user_stats(session_info['user_id'])
            
            return jsonify({
                'success': True,
                'user': session_info,
                'stats': user_stats
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
    
    @app.route('/api/auth/verify', methods=['GET'])
    def api_verify_session():
        """Verify session token"""
        try:
            if 'session_token' not in session:
                return jsonify({
                    'valid': False,
                    'message': 'No session'
                })
            
            session_info = auth.verify_session(session['session_token'])
            return jsonify(session_info)
            
        except Exception as e:
            return jsonify({
                'valid': False,
                'message': str(e)
            }), 500
    
    return app

# Usage in app.py:
# from app_routes_auth import init_auth_routes
# app = init_auth_routes(app)
