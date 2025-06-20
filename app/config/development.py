# app/config/development.py
from app.config.base import BaseConfig

class DevelopmentConfig(BaseConfig):
    """Configuration pour le développement"""
    DEBUG = True
    TESTING = False
    
    # Logs plus verbeux en développement
    LOG_LEVEL = 'DEBUG'
    
    # Rate limiting plus permissif en dev
    RATELIMIT_DEFAULT = "10000 per hour"