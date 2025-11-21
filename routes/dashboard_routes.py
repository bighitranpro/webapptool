"""
Dashboard Routes
Main dashboard and user interface endpoints
"""

from flask import Blueprint, render_template, session
from auth_vip import AuthVIPSystem, login_required

dashboard_bp = Blueprint('dashboard', __name__)
auth_system = AuthVIPSystem()


@dashboard_bp.route('/dashboard')
@login_required
def dashboard_page():
    """Main dashboard (requires authentication)"""
    session_info = auth_system.verify_session(session['session_token'])
    user_stats = auth_system.get_user_stats(session_info['user_id'])
    return render_template('dashboard.html', user=session_info, stats=user_stats)
