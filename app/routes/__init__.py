# app/routes/__init__.py
from app.routes.auth import auth_bp
from app.routes.user import user_bp
from app.routes.currencies import currencies_bp
from app.routes.conversions import conversions_bp
from app.routes.dashboard import dashboard_bp

__all__ = ['auth_bp', 'user_bp', 'currencies_bp', 'conversions_bp', 'dashboard_bp']
