"""
Authentication System for BI GHI TOOL MMO
Advanced user authentication with session management
"""

import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
from flask import session, redirect, url_for, request
from typing import Dict, Optional
import json


class AuthSystem:
    """Advanced authentication system with security features"""
    
    def __init__(self, db_path='email_tool.db'):
        self.db_path = db_path
        self.session_timeout = 24  # hours
        self.init_database()
    
    def init_database(self):
        """Initialize authentication database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                full_name TEXT,
                role TEXT DEFAULT 'user',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                login_count INTEGER DEFAULT 0,
                api_key TEXT UNIQUE
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Activity logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER PRIMARY KEY,
                theme TEXT DEFAULT 'dark',
                language TEXT DEFAULT 'vi',
                notifications_enabled INTEGER DEFAULT 1,
                auto_save INTEGER DEFAULT 1,
                preferences_json TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        
        # Create default admin if not exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", ('admin',))
        if cursor.fetchone()[0] == 0:
            admin_pass = self.hash_password('admin123')
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, full_name, role)
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin', admin_pass, 'admin@bighitool.com', 'Administrator', 'admin'))
            conn.commit()
            
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt"""
        salt = "bighi_tool_mmo_2024"  # In production, use per-user salt
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return self.hash_password(password) == password_hash
    
    def create_user(self, username: str, password: str, email: str = None, 
                   full_name: str = None, role: str = 'user') -> Dict:
        """Create new user account"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if username exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                return {'success': False, 'message': 'Username already exists'}
            
            password_hash = self.hash_password(password)
            api_key = secrets.token_urlsafe(32)
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, full_name, role, api_key)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, password_hash, email, full_name, role, api_key))
            
            user_id = cursor.lastrowid
            
            # Create default preferences
            cursor.execute('''
                INSERT INTO user_preferences (user_id)
                VALUES (?)
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            self.log_activity(user_id, 'USER_CREATED', f'User {username} created')
            
            return {
                'success': True,
                'message': 'User created successfully',
                'user_id': user_id,
                'api_key': api_key
            }
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def authenticate(self, username: str, password: str, ip_address: str = None, 
                    user_agent: str = None) -> Dict:
        """Authenticate user and create session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, password_hash, is_active, role, full_name
                FROM users WHERE username = ?
            ''', (username,))
            
            result = cursor.fetchone()
            
            if not result:
                return {'success': False, 'message': 'Invalid username or password'}
            
            user_id, password_hash, is_active, role, full_name = result
            
            if not is_active:
                return {'success': False, 'message': 'Account is disabled'}
            
            if not self.verify_password(password, password_hash):
                self.log_activity(user_id, 'LOGIN_FAILED', 'Invalid password')
                return {'success': False, 'message': 'Invalid username or password'}
            
            # Create session token
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=self.session_timeout)
            
            cursor.execute('''
                INSERT INTO user_sessions 
                (user_id, session_token, ip_address, user_agent, expires_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, session_token, ip_address, user_agent, expires_at))
            
            # Update last login
            cursor.execute('''
                UPDATE users 
                SET last_login = CURRENT_TIMESTAMP, login_count = login_count + 1
                WHERE id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            self.log_activity(user_id, 'LOGIN_SUCCESS', f'Logged in from {ip_address}')
            
            return {
                'success': True,
                'message': 'Login successful',
                'user_id': user_id,
                'username': username,
                'role': role,
                'full_name': full_name,
                'session_token': session_token,
                'expires_at': expires_at.isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def verify_session(self, session_token: str) -> Dict:
        """Verify session token and return user info"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.user_id, u.username, u.role, u.full_name, s.expires_at
                FROM user_sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = ? AND s.is_active = 1
            ''', (session_token,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return {'valid': False, 'message': 'Invalid session'}
            
            user_id, username, role, full_name, expires_at = result
            
            # Check if session expired
            if datetime.fromisoformat(expires_at) < datetime.now():
                self.invalidate_session(session_token)
                return {'valid': False, 'message': 'Session expired'}
            
            return {
                'valid': True,
                'user_id': user_id,
                'username': username,
                'role': role,
                'full_name': full_name
            }
            
        except Exception as e:
            return {'valid': False, 'message': str(e)}
    
    def invalidate_session(self, session_token: str):
        """Invalidate/logout session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_sessions SET is_active = 0
                WHERE session_token = ?
            ''', (session_token,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error invalidating session: {e}")
    
    def logout(self, session_token: str):
        """Logout user"""
        session_info = self.verify_session(session_token)
        if session_info.get('valid'):
            self.log_activity(
                session_info['user_id'], 
                'LOGOUT', 
                f"User {session_info['username']} logged out"
            )
        self.invalidate_session(session_token)
    
    def log_activity(self, user_id: int, action: str, details: str = None, 
                    ip_address: str = None):
        """Log user activity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO activity_logs (user_id, action, details, ip_address)
                VALUES (?, ?, ?, ?)
            ''', (user_id, action, details, ip_address))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error logging activity: {e}")
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # User info
            cursor.execute('''
                SELECT username, email, full_name, role, created_at, 
                       last_login, login_count
                FROM users WHERE id = ?
            ''', (user_id,))
            
            user_info = cursor.fetchone()
            
            # Activity count
            cursor.execute('''
                SELECT COUNT(*) FROM activity_logs WHERE user_id = ?
            ''', (user_id,))
            
            activity_count = cursor.fetchone()[0]
            
            conn.close()
            
            if user_info:
                return {
                    'username': user_info[0],
                    'email': user_info[1],
                    'full_name': user_info[2],
                    'role': user_info[3],
                    'created_at': user_info[4],
                    'last_login': user_info[5],
                    'login_count': user_info[6],
                    'total_activities': activity_count
                }
            
            return {}
            
        except Exception as e:
            return {'error': str(e)}


def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'session_token' not in session:
            return redirect(url_for('login_page'))
        
        auth = AuthSystem()
        session_info = auth.verify_session(session['session_token'])
        
        if not session_info.get('valid'):
            session.clear()
            return redirect(url_for('login_page'))
        
        return f(*args, **kwargs)
    
    return decorated_function


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'session_token' not in session:
            return redirect(url_for('login_page'))
        
        auth = AuthSystem()
        session_info = auth.verify_session(session['session_token'])
        
        if not session_info.get('valid'):
            session.clear()
            return redirect(url_for('login_page'))
        
        if session_info.get('role') != 'admin':
            return "Access denied", 403
        
        return f(*args, **kwargs)
    
    return decorated_function
