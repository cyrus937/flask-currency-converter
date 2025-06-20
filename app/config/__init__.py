# app/config/__init__.py
from app.config.base import BaseConfig
from app.config.development import DevelopmentConfig
from app.config.production import ProductionConfig

config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': DevelopmentConfig  # Pour les tests
}

def get_config(config_name):
    return config_map.get(config_name, DevelopmentConfig)