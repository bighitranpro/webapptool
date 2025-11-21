"""
Routes Package
Modular routing for BI GHI TOOL MMO
"""

from .auth_routes import auth_bp
from .api_routes import api_bp
from .dashboard_routes import dashboard_bp

__all__ = ['auth_bp', 'api_bp', 'dashboard_bp']
