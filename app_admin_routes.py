"""
Admin API Routes for Bi Tool (mochiphoto.click)
Complete admin management endpoints including tool visibility control
"""

from flask import Blueprint, request, jsonify, render_template, session
from auth_vip import AuthVIPSystem, admin_required, VIPLevel
import sqlite3
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
auth_system = AuthVIPSystem()


@admin_bp.route('/')
@admin_required
def admin_dashboard():
    """Admin dashboard page"""
    session_info = auth_system.verify_session(session['session_token'])
    return render_template('admin_dashboard.html', user=session_info)


@admin_bp.route('/api/overview')
@admin_required
def api_overview():
    """Get overview statistics"""
    try:
        conn = sqlite3.connect(auth_system.db_path)
        cursor = conn.cursor()
        
        # Total users
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        # Active users
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
        active_users = cursor.fetchone()[0]
        
        # VIP users
        cursor.execute('SELECT COUNT(*) FROM users WHERE vip_level > 0')
        vip_users = cursor.fetchone()[0]
        
        # Total revenue
        cursor.execute('SELECT SUM(amount) FROM payment_history WHERE status = "completed"')
        result = cursor.fetchone()
        total_revenue = result[0] if result[0] else 0
        
        # Total operations
        cursor.execute('SELECT SUM(validations_count + generations_count + extractions_count) FROM usage_stats')
        result = cursor.fetchone()
        total_operations = result[0] if result[0] else 0
        
        # Today operations
        cursor.execute('''
            SELECT SUM(validations_count + generations_count + extractions_count)
            FROM usage_stats WHERE date = CURRENT_DATE
        ''')
        result = cursor.fetchone()
        today_operations = result[0] if result[0] else 0
        
        # Recent activities
        cursor.execute('''
            SELECT a.action, a.details, a.timestamp, u.username
            FROM activity_logs a
            LEFT JOIN users u ON a.user_id = u.id
            ORDER BY a.timestamp DESC
            LIMIT 10
        ''')
        activities = []
        for row in cursor.fetchall():
            activities.append({
                'action': row[0],
                'details': row[1],
                'timestamp': row[2],
                'username': row[3]
            })
        
        conn.close()
        
        return jsonify({
            'total_users': total_users,
            'active_users': active_users,
            'vip_users': vip_users,
            'total_revenue': total_revenue,
            'total_operations': total_operations,
            'today_operations': today_operations,
            'recent_activities': activities
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/users')
@admin_required
def api_get_users():
    """Get all users"""
    try:
        conn = sqlite3.connect(auth_system.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, full_name, role, vip_level, 
                   is_active, is_banned, created_at, last_login, login_count
            FROM users
            ORDER BY created_at DESC
        ''')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'full_name': row[3],
                'role': row[4],
                'vip_level': row[5],
                'is_active': row[6],
                'is_banned': row[7],
                'created_at': row[8],
                'last_login': row[9],
                'login_count': row[10]
            })
        
        conn.close()
        return jsonify(users)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/users', methods=['POST'])
@admin_required
def api_create_user():
    """Create new user"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        full_name = data.get('full_name')
        role = data.get('role', 'user')
        vip_level = int(data.get('vip_level', 0))
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        conn = sqlite3.connect(auth_system.db_path)
        cursor = conn.cursor()
        
        # Check if username exists
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Username already exists'}), 400
        
        # Create user
        password_hash = auth_system.hash_password(password)
        cursor.execute('''
            INSERT INTO users (username, password_hash, email, full_name, role, vip_level)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, password_hash, email, full_name, role, vip_level))
        
        user_id = cursor.lastrowid
        
        # If VIP, create subscription
        if vip_level > 0:
            vip_info = VIPLevel.get_level_info(vip_level)
            expires_at = datetime.now() + timedelta(days=vip_info['duration_days'])
            
            cursor.execute('''
                INSERT INTO vip_subscriptions (user_id, vip_level, expires_at, price, payment_method, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
            ''', (user_id, vip_level, expires_at.strftime('%Y-%m-%d %H:%M:%S'), 
                  vip_info['price'], 'admin_created'))
            
            cursor.execute('''
                UPDATE users SET vip_expires_at = ? WHERE id = ?
            ''', (expires_at.strftime('%Y-%m-%d %H:%M:%S'), user_id))
        
        # Log activity
        cursor.execute('''
            INSERT INTO activity_logs (user_id, action, details)
            VALUES (?, ?, ?)
        ''', (session.get('user_id'), 'user_created', f'Created user: {username}'))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'user_id': user_id})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def api_delete_user(user_id):
    """Delete user"""
    try:
        conn = sqlite3.connect(auth_system.db_path)
        cursor = conn.cursor()
        
        # Don't allow deleting yourself
        if user_id == session.get('user_id'):
            return jsonify({'error': 'Cannot delete yourself'}), 400
        
        # Get username for logging
        cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({'error': 'User not found'}), 404
        
        username = result[0]
        
        # Delete user (cascade will handle related records)
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        cursor.execute('DELETE FROM user_sessions WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM usage_stats WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM vip_subscriptions WHERE user_id = ?', (user_id,))
        
        # Log activity
        cursor.execute('''
            INSERT INTO activity_logs (user_id, action, details)
            VALUES (?, ?, ?)
        ''', (session.get('user_id'), 'user_deleted', f'Deleted user: {username}'))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/vip-stats')
@admin_required
def api_vip_stats():
    """Get VIP statistics"""
    try:
        conn = sqlite3.connect(auth_system.db_path)
        cursor = conn.cursor()
        
        # Count users by VIP level
        cursor.execute('SELECT COUNT(*) FROM users WHERE vip_level = 0')
        free_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE vip_level = 1')
        basic_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE vip_level = 2')
        pro_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE vip_level = 3')
        enterprise_users = cursor.fetchone()[0]
        
        # Get active subscriptions
        cursor.execute('''
            SELECT s.id, u.username, s.vip_level, s.started_at, s.expires_at, 
                   s.price, s.payment_method, s.is_active
            FROM vip_subscriptions s
            JOIN users u ON s.user_id = u.id
            WHERE s.is_active = 1
            ORDER BY s.started_at DESC
        ''')
        
        subscriptions = []
        for row in cursor.fetchall():
            subscriptions.append({
                'id': row[0],
                'username': row[1],
                'vip_level': row[2],
                'started_at': row[3],
                'expires_at': row[4],
                'price': row[5],
                'payment_method': row[6],
                'is_active': row[7]
            })
        
        conn.close()
        
        return jsonify({
            'free_users': free_users,
            'basic_users': basic_users,
            'pro_users': pro_users,
            'enterprise_users': enterprise_users,
            'subscriptions': subscriptions
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/logs')
@admin_required
def api_get_logs():
    """Get activity logs"""
    try:
        conn = sqlite3.connect(auth_system.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.id, a.action, a.details, a.timestamp, a.ip_address, u.username
            FROM activity_logs a
            LEFT JOIN users u ON a.user_id = u.id
            ORDER BY a.timestamp DESC
            LIMIT 100
        ''')
        
        logs = []
        for row in cursor.fetchall():
            logs.append({
                'id': row[0],
                'action': row[1],
                'details': row[2],
                'timestamp': row[3],
                'ip_address': row[4],
                'username': row[5]
            })
        
        conn.close()
        return jsonify(logs)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/tools')
@admin_required
def api_get_tools():
    """Get all tools configuration"""
    try:
        conn = sqlite3.connect(auth_system.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT tool_id, tool_name, tool_category, icon_class, visible, 
                   maintenance_mode, maintenance_message, order_position, requires_role
            FROM tool_config
            ORDER BY order_position ASC
        ''')
        
        tools = []
        for row in cursor.fetchall():
            tools.append({
                'tool_id': row[0],
                'tool_name': row[1],
                'tool_category': row[2],
                'icon_class': row[3],
                'visible': bool(row[4]),
                'maintenance_mode': bool(row[5]),
                'maintenance_message': row[6],
                'order_position': row[7],
                'requires_role': row[8]
            })
        
        conn.close()
        return jsonify(tools)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/tools/<tool_id>', methods=['PUT'])
@admin_required
def api_update_tool(tool_id):
    """Update tool configuration"""
    try:
        data = request.get_json()
        
        conn = sqlite3.connect(auth_system.db_path)
        cursor = conn.cursor()
        
        # Build update query dynamically based on provided fields
        update_fields = []
        values = []
        
        if 'visible' in data:
            update_fields.append('visible = ?')
            values.append(1 if data['visible'] else 0)
        
        if 'maintenance_mode' in data:
            update_fields.append('maintenance_mode = ?')
            values.append(1 if data['maintenance_mode'] else 0)
        
        if 'maintenance_message' in data:
            update_fields.append('maintenance_message = ?')
            values.append(data['maintenance_message'])
        
        if 'order_position' in data:
            update_fields.append('order_position = ?')
            values.append(data['order_position'])
        
        if 'requires_role' in data:
            update_fields.append('requires_role = ?')
            values.append(data['requires_role'])
        
        if not update_fields:
            return jsonify({'error': 'No fields to update'}), 400
        
        # Add updated_at and tool_id
        update_fields.append('updated_at = ?')
        values.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        values.append(tool_id)
        
        query = f"UPDATE tool_config SET {', '.join(update_fields)} WHERE tool_id = ?"
        cursor.execute(query, values)
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Tool not found'}), 404
        
        # Log activity
        cursor.execute('''
            INSERT INTO activity_logs (user_id, action, details)
            VALUES (?, ?, ?)
        ''', (session.get('user_id'), 'tool_updated', f'Updated tool: {tool_id}'))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/tools/batch-update', methods=['POST'])
@admin_required
def api_batch_update_tools():
    """Batch update tool configurations"""
    try:
        data = request.get_json()
        tools = data.get('tools', [])
        
        if not tools:
            return jsonify({'error': 'No tools provided'}), 400
        
        conn = sqlite3.connect(auth_system.db_path)
        cursor = conn.cursor()
        
        for tool in tools:
            tool_id = tool.get('tool_id')
            if not tool_id:
                continue
            
            update_fields = []
            values = []
            
            if 'visible' in tool:
                update_fields.append('visible = ?')
                values.append(1 if tool['visible'] else 0)
            
            if 'maintenance_mode' in tool:
                update_fields.append('maintenance_mode = ?')
                values.append(1 if tool['maintenance_mode'] else 0)
            
            if 'order_position' in tool:
                update_fields.append('order_position = ?')
                values.append(tool['order_position'])
            
            if update_fields:
                update_fields.append('updated_at = ?')
                values.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                values.append(tool_id)
                
                query = f"UPDATE tool_config SET {', '.join(update_fields)} WHERE tool_id = ?"
                cursor.execute(query, values)
        
        # Log activity
        cursor.execute('''
            INSERT INTO activity_logs (user_id, action, details)
            VALUES (?, ?, ?)
        ''', (session.get('user_id'), 'tools_batch_updated', f'Batch updated {len(tools)} tools'))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'updated': len(tools)})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/search')
@admin_required
def api_admin_search():
    """Search across all admin features"""
    try:
        query = request.args.get('q', '').strip().lower()
        
        if not query:
            return jsonify({'error': 'Search query required'}), 400
        
        conn = sqlite3.connect(auth_system.db_path)
        cursor = conn.cursor()
        
        results = {
            'users': [],
            'tools': [],
            'logs': [],
            'subscriptions': []
        }
        
        # Search users
        cursor.execute('''
            SELECT id, username, email, full_name, role, vip_level
            FROM users
            WHERE LOWER(username) LIKE ? OR LOWER(email) LIKE ? OR LOWER(full_name) LIKE ?
            LIMIT 10
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        
        for row in cursor.fetchall():
            results['users'].append({
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'full_name': row[3],
                'role': row[4],
                'vip_level': row[5]
            })
        
        # Search tools
        cursor.execute('''
            SELECT tool_id, tool_name, tool_category, visible, maintenance_mode
            FROM tool_config
            WHERE LOWER(tool_name) LIKE ? OR LOWER(tool_id) LIKE ?
            LIMIT 10
        ''', (f'%{query}%', f'%{query}%'))
        
        for row in cursor.fetchall():
            results['tools'].append({
                'tool_id': row[0],
                'tool_name': row[1],
                'tool_category': row[2],
                'visible': bool(row[3]),
                'maintenance_mode': bool(row[4])
            })
        
        # Search logs
        cursor.execute('''
            SELECT a.id, a.action, a.details, a.timestamp, u.username
            FROM activity_logs a
            LEFT JOIN users u ON a.user_id = u.id
            WHERE LOWER(a.action) LIKE ? OR LOWER(a.details) LIKE ? OR LOWER(u.username) LIKE ?
            ORDER BY a.timestamp DESC
            LIMIT 10
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        
        for row in cursor.fetchall():
            results['logs'].append({
                'id': row[0],
                'action': row[1],
                'details': row[2],
                'timestamp': row[3],
                'username': row[4]
            })
        
        conn.close()
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Export blueprint
__all__ = ['admin_bp']
