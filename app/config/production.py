# app/config/production.py
from app.config.base import BaseConfig

class ProductionConfig(BaseConfig):
    """Configuration pour la production"""
    DEBUG = False
    TESTING = False
    
    # Sécurité renforcée
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Logs
    LOG_LEVEL = 'INFO'