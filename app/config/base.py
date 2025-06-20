# app/config/base.py
import os
from datetime import timedelta

class BaseConfig:
    """Configuration de base"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    
    # Session Configuration
    SESSION_TIMEOUT = timedelta(days=30)
    MAX_SESSIONS_PER_USER = 5
    
    # Cache Configuration (Redis)
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')
    RATELIMIT_DEFAULT = "1000 per hour"
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Currency API Keys
    FIXER_API_KEY = os.environ.get('FIXER_API_KEY')
    EXCHANGERATE_API_KEY = os.environ.get('EXCHANGERATE_API_KEY')
    
    # Currency Configuration
    DEFAULT_BASE_CURRENCY = 'USD'
    RATE_UPDATE_INTERVAL = 300  # 5 minutes
    RATE_CACHE_TIMEOUT = 600    # 10 minutes
    CONVERSION_FEE_RATE = 0.01  # 1%
    
    # Security
    BCRYPT_LOG_ROUNDS = 12
    
    # CORS
    CORS_ORIGINS = ["http://localhost:3000", "http://localhost:5000"]