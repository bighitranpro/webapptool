"""
VIP Management System for BI GHI TOOL MMO
Advanced subscription and permission management
"""

import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
from flask import session, redirect, url_for, request, jsonify
from typing import Dict, Optional, List
import json


class VIPLevel:
    """VIP Level definitions with features and limits"""
    
    FREE = {
        'name': 'Free',
        'level': 0,
        'price': 0,
        'duration_days': 365,
        'features': {
            'email_validator': True,
            'email_generator': True,
            'email_extractor': False,
            'fb_linked_checker': False,
            'check_2fa': False,
            'page_mining': False,
            'max_daily_validations': 100,
            'max_daily_generations': 50,
            'api_access': False,
            'priority_support': False,
            'concurrent_tasks': 1,
            'export_formats': ['txt'],
            'bulk_operations': False
        },
        'color': '#95a5a6',
        'badge': '🆓'
    }
    
    BASIC = {
        'name': 'Basic',
        'level': 1,
        'price': 99000,  # VND per month
        'duration_days': 30,
        'features': {
            'email_validator': True,
            'email_generator': True,
            'email_extractor': True,
            'fb_linked_checker': True,
            'check_2fa': False,
            'page_mining': False,
            'max_daily_validations': 1000,
            'max_daily_generations': 500,
            'api_access': False,
            'priority_support': False,
            'concurrent_tasks': 2,
            'export_formats': ['txt', 'csv'],
            'bulk_operations': True
        },
        'color': '#3498db',
        'badge': '⭐'
    }
    
    PRO = {
        'name': 'Pro',
        'level': 2,
        'price': 299000,  # VND per month
        'duration_days': 30,
        'features': {
            'email_validator': True,
            'email_generator': True,
            'email_extractor': True,
            'fb_linked_checker': True,
            'check_2fa': True,
            'page_mining': True,
            'max_daily_validations': 10000,
            'max_daily_generations': 5000,
            'api_access': True,
            'priority_support': True,
            'concurrent_tasks': 5,
            'export_formats': ['txt', 'csv', 'json', 'xlsx'],
            'bulk_operations': True
        },
        'color': '#f39c12',
        'badge': '👑'
    }
    
    ENTERPRISE = {
        'name': 'Enterprise',
        'level': 3,
        'price': 999000,  # VND per month
        'duration_days': 30,
        'features': {
            'email_validator': True,
            'email_generator': True,
            'email_extractor': True,
            'fb_linked_checker': True,
            'check_2fa': True,
            'page_mining': True,
            'max_daily_validations': -1,  # Unlimited
            'max_daily_generations': -1,  # Unlimited
            'api_access': True,
            'priority_support': True,
            'concurrent_tasks': 20,
            'export_formats': ['txt', 'csv', 'json', 'xlsx', 'xml'],
            'bulk_operations': True,
            'custom_integration': True,
            'dedicated_support': True,
            'white_label': True
        },
        'color': '#9b59b6',
        'badge': '💎'
    }
    
    @classmethod
    def get_level_info(cls, level: int) -> Dict:
        """Get VIP level information by level number"""
        levels = {0: cls.FREE, 1: cls.BASIC, 2: cls.PRO, 3: cls.ENTERPRISE}
        return levels.get(level, cls.FREE)
    
    @classmethod
    def get_all_levels(cls) -> List[Dict]:
        """Get all VIP levels"""
        return [cls.FREE, cls.BASIC, cls.PRO, cls.ENTERPRISE]


class AuthVIPSystem:
    """Enhanced authentication system with VIP management"""
    
    def __init__(self, db_path='email_tool.db'):
        self.db_path = db_path
        self.session_timeout = 24  # hours
        self.init_database()
    
    def init_database(self):
        """Initialize authentication and VIP database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced Users table with VIP info
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE,
                full_name TEXT,
                role TEXT DEFAULT 'user',
                vip_level INTEGER DEFAULT 0,
                vip_expires_at TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                is_banned INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                login_count INTEGER DEFAULT 0,
                api_key TEXT UNIQUE,
                referral_code TEXT UNIQUE,
                referred_by INTEGER,
                avatar_url TEXT,
                phone TEXT,
                FOREIGN KEY (referred_by) REFERENCES users(id)
            )
        ''')
        
        # VIP Subscriptions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vip_subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                vip_level INTEGER NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                price REAL,
                payment_method TEXT,
                transaction_id TEXT,
                is_active INTEGER DEFAULT 1,
                auto_renew INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Usage statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE DEFAULT CURRENT_DATE,
                validations_count INTEGER DEFAULT 0,
                generations_count INTEGER DEFAULT 0,
                extractions_count INTEGER DEFAULT 0,
                api_calls_count INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, date)
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
                email_notifications INTEGER DEFAULT 1,
                auto_save INTEGER DEFAULT 1,
                preferences_json TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Payment history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'VND',
                payment_method TEXT,
                transaction_id TEXT UNIQUE,
                status TEXT DEFAULT 'pending',
                vip_level INTEGER,
                duration_days INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # System settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        
        # Create default admin if not exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", ('admin',))
        if cursor.fetchone()[0] == 0:
            admin_pass = self.hash_password('admin123')
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, full_name, role, vip_level)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('admin', admin_pass, 'admin@bighitool.com', 'Administrator', 'admin', 3))
            admin_id = cursor.lastrowid
            
            # Set admin VIP to never expire
            cursor.execute('''
                INSERT INTO vip_subscriptions (user_id, vip_level, expires_at, price, is_active)
                VALUES (?, ?, ?, ?, ?)
            ''', (admin_id, 3, '2099-12-31 23:59:59', 0, 1))
            
            conn.commit()
            
        conn.close()
        print("✅ VIP Database initialized:", self.db_path)
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = "bighi_tool_mmo_vip_2024"
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def generate_api_key(self) -> str:
        """Generate unique API key"""
        return 'btm_' + secrets.token_urlsafe(32)
    
    def generate_referral_code(self, username: str) -> str:
        """Generate referral code"""
        random_part = secrets.token_urlsafe(6)
        return f"{username[:4].upper()}{random_part}"
    
    def create_user(self, username: str, password: str, email: str, 
                    role: str = 'user', vip_level: int = 0, full_name: str = None) -> Dict:
        """
        Create new user account
        
        Args:
            username: Unique username
            password: Plain text password (will be hashed)
            email: User email address
            role: User role (default: 'user')
            vip_level: VIP level (default: 0 = FREE)
            full_name: Full name (optional)
        
        Returns:
            {
                'success': True/False,
                'message': 'Success/Error message',
                'user_id': user_id (if success)
            }
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if username already exists
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                conn.close()
                return {
                    'success': False,
                    'message': 'Tên đăng nhập đã tồn tại / Username already exists'
                }
            
            # Check if email already exists
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                conn.close()
                return {
                    'success': False,
                    'message': 'Email đã được đăng ký / Email already registered'
                }
            
            # Hash password
            password_hash = self.hash_password(password)
            
            # Generate API key and referral code
            api_key = self.generate_api_key()
            referral_code = self.generate_referral_code(username)
            
            # Insert new user
            cursor.execute('''
                INSERT INTO users (
                    username, password_hash, email, full_name, role, 
                    vip_level, api_key, referral_code, is_active
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                username, password_hash, email, full_name or username, 
                role, vip_level, api_key, referral_code, 1
            ))
            
            user_id = cursor.lastrowid
            
            # Initialize user preferences
            cursor.execute('''
                INSERT INTO user_preferences (user_id, theme, language)
                VALUES (?, ?, ?)
            ''', (user_id, 'dark', 'vi'))
            
            # If VIP level > 0, create subscription record
            if vip_level > 0:
                from datetime import datetime, timedelta
                expires_at = datetime.now() + timedelta(days=30)
                cursor.execute('''
                    INSERT INTO vip_subscriptions (
                        user_id, vip_level, expires_at, is_active
                    )
                    VALUES (?, ?, ?, ?)
                ''', (user_id, vip_level, expires_at.strftime('%Y-%m-%d %H:%M:%S'), 1))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'Đăng ký thành công / Registration successful',
                'user_id': user_id
            }
            
        except Exception as e:
            print(f"❌ Error creating user: {str(e)}")
            return {
                'success': False,
                'message': f'Lỗi tạo tài khoản / Error creating account: {str(e)}'
            }
    
    def authenticate(self, username: str, password: str, ip_address: str, user_agent: str) -> Dict:
        """Authenticate user and create session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get user
            password_hash = self.hash_password(password)
            cursor.execute('''
                SELECT id, username, role, email, full_name, vip_level, vip_expires_at, 
                       is_active, is_banned, avatar_url
                FROM users 
                WHERE username = ? AND password_hash = ?
            ''', (username, password_hash))
            
            user = cursor.fetchone()
            
            if not user:
                return {'success': False, 'message': 'Invalid username or password'}
            
            user_id, username, role, email, full_name, vip_level, vip_expires_at, is_active, is_banned, avatar_url = user
            
            if not is_active:
                return {'success': False, 'message': 'Account is deactivated'}
            
            if is_banned:
                return {'success': False, 'message': 'Account is banned'}
            
            # Check VIP expiration
            if vip_expires_at:
                vip_expires = datetime.strptime(vip_expires_at, '%Y-%m-%d %H:%M:%S')
                if datetime.now() > vip_expires and vip_level > 0:
                    # VIP expired, downgrade to free
                    cursor.execute('UPDATE users SET vip_level = 0 WHERE id = ?', (user_id,))
                    vip_level = 0
            
            # Create session
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=self.session_timeout)
            
            cursor.execute('''
                INSERT INTO user_sessions (user_id, session_token, ip_address, user_agent, expires_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, session_token, ip_address, user_agent, expires_at.strftime('%Y-%m-%d %H:%M:%S')))
            
            # Update login stats
            cursor.execute('''
                UPDATE users 
                SET last_login = CURRENT_TIMESTAMP, login_count = login_count + 1
                WHERE id = ?
            ''', (user_id,))
            
            # Log activity
            cursor.execute('''
                INSERT INTO activity_logs (user_id, action, details, ip_address)
                VALUES (?, ?, ?, ?)
            ''', (user_id, 'login', f'Successful login from {ip_address}', ip_address))
            
            conn.commit()
            conn.close()
            
            vip_info = VIPLevel.get_level_info(vip_level)
            
            return {
                'success': True,
                'session_token': session_token,
                'user_id': user_id,
                'username': username,
                'role': role,
                'email': email,
                'full_name': full_name,
                'vip_level': vip_level,
                'vip_name': vip_info['name'],
                'vip_badge': vip_info['badge'],
                'vip_expires_at': vip_expires_at,
                'avatar_url': avatar_url
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Authentication error: {str(e)}'}
    
    def verify_session(self, session_token: str) -> Dict:
        """Verify session token"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.user_id, u.username, u.role, u.email, u.full_name, 
                       u.vip_level, u.vip_expires_at, u.avatar_url, s.expires_at
                FROM user_sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = ? AND s.is_active = 1
            ''', (session_token,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return {'valid': False, 'message': 'Invalid session'}
            
            user_id, username, role, email, full_name, vip_level, vip_expires_at, avatar_url, expires_at = result
            
            # Check expiration
            if datetime.now() > datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S'):
                return {'valid': False, 'message': 'Session expired'}
            
            vip_info = VIPLevel.get_level_info(vip_level)
            
            return {
                'valid': True,
                'user_id': user_id,
                'username': username,
                'role': role,
                'email': email,
                'full_name': full_name,
                'vip_level': vip_level,
                'vip_name': vip_info['name'],
                'vip_badge': vip_info['badge'],
                'vip_expires_at': vip_expires_at,
                'avatar_url': avatar_url
            }
            
        except Exception as e:
            return {'valid': False, 'message': f'Verification error: {str(e)}'}
    
    def logout(self, session_token: str) -> bool:
        """Logout user by deactivating session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('UPDATE user_sessions SET is_active = 0 WHERE session_token = ?', (session_token,))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def check_permission(self, user_id: int, feature: str) -> bool:
        """Check if user has permission to use feature"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT vip_level FROM users WHERE id = ?', (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return False
            
            vip_level = result[0]
            vip_info = VIPLevel.get_level_info(vip_level)
            
            return vip_info['features'].get(feature, False)
            
        except:
            return False
    
    def check_daily_limit(self, user_id: int, action_type: str) -> Dict:
        """Check if user has reached daily limit"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get user VIP level
            cursor.execute('SELECT vip_level FROM users WHERE id = ?', (user_id,))
            result = cursor.fetchone()
            if not result:
                return {'allowed': False, 'message': 'User not found'}
            
            vip_level = result[0]
            vip_info = VIPLevel.get_level_info(vip_level)
            
            # Get today's usage
            cursor.execute('''
                SELECT validations_count, generations_count, extractions_count, api_calls_count
                FROM usage_stats
                WHERE user_id = ? AND date = CURRENT_DATE
            ''', (user_id,))
            
            usage = cursor.fetchone()
            
            if not usage:
                # No usage today, insert record
                cursor.execute('''
                    INSERT INTO usage_stats (user_id, date, validations_count, generations_count)
                    VALUES (?, CURRENT_DATE, 0, 0)
                ''', (user_id,))
                conn.commit()
                usage = (0, 0, 0, 0)
            
            conn.close()
            
            validations, generations, extractions, api_calls = usage
            
            # Check limits
            if action_type == 'validation':
                limit = vip_info['features']['max_daily_validations']
                current = validations
            elif action_type == 'generation':
                limit = vip_info['features']['max_daily_generations']
                current = generations
            else:
                return {'allowed': True}  # No limit for other actions
            
            if limit == -1:  # Unlimited
                return {'allowed': True, 'remaining': -1}
            
            if current >= limit:
                return {
                    'allowed': False,
                    'message': f'Daily limit reached ({limit})',
                    'current': current,
                    'limit': limit
                }
            
            return {
                'allowed': True,
                'current': current,
                'limit': limit,
                'remaining': limit - current
            }
            
        except Exception as e:
            return {'allowed': False, 'message': f'Error: {str(e)}'}
    
    def increment_usage(self, user_id: int, action_type: str) -> bool:
        """Increment usage counter"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            column_map = {
                'validation': 'validations_count',
                'generation': 'generations_count',
                'extraction': 'extractions_count',
                'api_call': 'api_calls_count'
            }
            
            column = column_map.get(action_type)
            if not column:
                return False
            
            # Check if record exists
            cursor.execute('''
                SELECT id FROM usage_stats WHERE user_id = ? AND date = CURRENT_DATE
            ''', (user_id,))
            
            if cursor.fetchone():
                # Update existing
                cursor.execute(f'''
                    UPDATE usage_stats 
                    SET {column} = {column} + 1
                    WHERE user_id = ? AND date = CURRENT_DATE
                ''', (user_id,))
            else:
                # Insert new
                cursor.execute(f'''
                    INSERT INTO usage_stats (user_id, date, {column})
                    VALUES (?, CURRENT_DATE, 1)
                ''', (user_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except:
            return False
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Basic user info
            cursor.execute('''
                SELECT username, email, full_name, role, vip_level, vip_expires_at,
                       created_at, last_login, login_count, avatar_url
                FROM users WHERE id = ?
            ''', (user_id,))
            user = cursor.fetchone()
            
            if not user:
                return {}
            
            # Today's usage
            cursor.execute('''
                SELECT validations_count, generations_count, extractions_count, api_calls_count
                FROM usage_stats WHERE user_id = ? AND date = CURRENT_DATE
            ''', (user_id,))
            today_usage = cursor.fetchone() or (0, 0, 0, 0)
            
            # Total usage
            cursor.execute('''
                SELECT SUM(validations_count), SUM(generations_count), 
                       SUM(extractions_count), SUM(api_calls_count)
                FROM usage_stats WHERE user_id = ?
            ''', (user_id,))
            total_usage = cursor.fetchone() or (0, 0, 0, 0)
            
            # Activity count
            cursor.execute('SELECT COUNT(*) FROM activity_logs WHERE user_id = ?', (user_id,))
            total_activities = cursor.fetchone()[0]
            
            conn.close()
            
            vip_level = user[4]
            vip_info = VIPLevel.get_level_info(vip_level)
            
            return {
                'username': user[0],
                'email': user[1],
                'full_name': user[2],
                'role': user[3],
                'vip_level': vip_level,
                'vip_name': vip_info['name'],
                'vip_badge': vip_info['badge'],
                'vip_color': vip_info['color'],
                'vip_expires_at': user[5],
                'created_at': user[6],
                'last_login': user[7],
                'login_count': user[8],
                'avatar_url': user[9],
                'today_validations': today_usage[0],
                'today_generations': today_usage[1],
                'today_extractions': today_usage[2],
                'today_api_calls': today_usage[3],
                'total_validations': total_usage[0] or 0,
                'total_generations': total_usage[1] or 0,
                'total_extractions': total_usage[2] or 0,
                'total_api_calls': total_usage[3] or 0,
                'total_activities': total_activities,
                'features': vip_info['features']
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def upgrade_vip(self, user_id: int, new_level: int, duration_days: int, 
                    payment_method: str = 'manual', transaction_id: str = None) -> Dict:
        """Upgrade user VIP level"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            vip_info = VIPLevel.get_level_info(new_level)
            expires_at = datetime.now() + timedelta(days=duration_days)
            
            # Update user VIP
            cursor.execute('''
                UPDATE users 
                SET vip_level = ?, vip_expires_at = ?
                WHERE id = ?
            ''', (new_level, expires_at.strftime('%Y-%m-%d %H:%M:%S'), user_id))
            
            # Insert subscription record
            cursor.execute('''
                INSERT INTO vip_subscriptions 
                (user_id, vip_level, expires_at, price, payment_method, transaction_id, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            ''', (user_id, new_level, expires_at.strftime('%Y-%m-%d %H:%M:%S'),
                  vip_info['price'], payment_method, transaction_id))
            
            # Log activity
            cursor.execute('''
                INSERT INTO activity_logs (user_id, action, details)
                VALUES (?, ?, ?)
            ''', (user_id, 'vip_upgrade', f'Upgraded to {vip_info["name"]} VIP'))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': f'Upgraded to {vip_info["name"]} VIP',
                'expires_at': expires_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Upgrade error: {str(e)}'}
    
    def log_activity(self, user_id: int, activity_type: str, description: str = '',
                     ip_address: str = '', user_agent: str = '') -> bool:
        """
        Log user activity to database
        
        Args:
            user_id: User ID
            activity_type: Type of activity (e.g., 'login', 'logout', 'user_registered')
            description: Activity description
            ip_address: IP address
            user_agent: User agent string
        
        Returns:
            True if logged successfully, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert into activity_logs table
            cursor.execute('''
                INSERT INTO activity_logs (user_id, action, details, ip_address)
                VALUES (?, ?, ?, ?)
            ''', (user_id, activity_type, description, ip_address))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"❌ Error logging activity: {str(e)}")
            return False


# Decorators for route protection
def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'session_token' not in session:
            return redirect(url_for('auth.login_page'))
        
        # Verify session is still valid
        auth_system = AuthVIPSystem()
        session_info = auth_system.verify_session(session['session_token'])
        
        if not session_info.get('valid'):
            session.clear()
            return redirect(url_for('auth.login_page'))
        
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'session_token' not in session:
            return redirect(url_for('auth.login_page'))
        
        auth_system = AuthVIPSystem()
        session_info = auth_system.verify_session(session['session_token'])
        
        if not session_info.get('valid') or session_info.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function


def vip_required(min_level: int):
    """Decorator to require minimum VIP level"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'session_token' not in session:
                return jsonify({'error': 'Login required'}), 401
            
            auth_system = AuthVIPSystem()
            session_info = auth_system.verify_session(session['session_token'])
            
            if not session_info.get('valid'):
                return jsonify({'error': 'Invalid session'}), 401
            
            if session_info.get('vip_level', 0) < min_level:
                vip_name = VIPLevel.get_level_info(min_level)['name']
                return jsonify({
                    'error': f'{vip_name} VIP required',
                    'required_level': min_level,
                    'current_level': session_info.get('vip_level', 0)
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
