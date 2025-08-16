# app/__init__.py
import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask, jsonify, request
from app.extensions import db, jwt, limiter, cache, mail, migrate, api, cors
from app.config import get_config


def create_app(config_name='development'):
    """Factory pattern pour créer l'application Flask"""
    app = Flask(__name__, static_folder='../static', template_folder='../templates')
    
    # Configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Initialisation des extensions
    init_extensions(app)
    
    # Enregistrement des blueprints
    register_blueprints(app)
    
    # Gestionnaires d'erreurs
    register_error_handlers(app)
    
    # JWT callbacks
    setup_jwt_callbacks(app)
    
    return app


def init_extensions(app):
    """Initialise les extensions Flask"""
    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    cors.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    api.init_app(app)  # Initialiser Swagger
    
    setup_logging(app)


def setup_logging(app):
    """Configuration avancée des logs pour Flask"""
    
    # Créer le dossier logs s'il n'existe pas
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # Configuration du niveau de log selon l'environnement
    if app.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    
    # Format des logs
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s [%(name)s] [%(pathname)s:%(lineno)d] - %(message)s'
    )
    
    # Handler pour fichier principal (rotation automatique)
    file_handler = RotatingFileHandler(
        'logs/app.log', 
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    
    # Handler pour les erreurs (fichier séparé)
    error_handler = RotatingFileHandler(
        'logs/errors.log',
        maxBytes=10240000,
        backupCount=5
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Handler pour la console (development)
    if app.debug:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        console_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(console_handler)
    
    # Ajouter les handlers à l'app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    app.logger.setLevel(log_level)
    
    # Désactiver les logs par défaut de Werkzeug en production
    if not app.debug:
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
    
    # Logger pour les requêtes
    @app.before_request
    def log_request_info():
        app.logger.debug(f"Request: {request.method} {request.url} - IP: {request.remote_addr}")
    
    @app.after_request
    def log_response_info(response):
        app.logger.debug(f"Response: {response.status_code} - {request.method} {request.url}")
        return response
    
    # Logger pour les erreurs non gérées
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Erreur serveur: {str(error)}")
        return jsonify({'message': 'Erreur interne du serveur'}), 500
    
    @app.errorhandler(404)
    def not_found(error):
        app.logger.warning(f"Page non trouvée: {request.url} - IP: {request.remote_addr}")
        return jsonify({'message': 'Ressource non trouvée'}), 404
    
    app.logger.info('Application Flask démarrée avec succès')

def register_blueprints(app):
    """Enregistre tous les blueprints"""
    from app.routes.auth import auth_bp, auth_pages_bp
    from app.routes.user import user_bp
    from app.routes.currencies import currencies_bp
    from app.routes.conversions import conversions_bp
    from app.routes.dashboard import dashboard_bp, api_dashboard
    from app.routes.api_key import api_keys_bp

    api.register_blueprint(auth_bp)
    api.register_blueprint(user_bp)
    api.register_blueprint(currencies_bp)
    api.register_blueprint(conversions_bp)
    api.register_blueprint(api_keys_bp)
    # api.register_blueprint(api_dashboard)  # API pour le dashboard

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_pages_bp)  # Pages d'authentification pour l'interface web


def register_error_handlers(app):
    """Gestionnaires d'erreurs globaux"""
    from flask import jsonify
    from app.utils.exceptions import AuthenticationError, CurrencyError, ValidationError
    
    @app.errorhandler(AuthenticationError)
    def handle_auth_error(e):
        return jsonify({'error': str(e)}), 401
    
    @app.errorhandler(CurrencyError)
    def handle_currency_error(e):
        return jsonify({'error': str(e)}), 400
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return jsonify({'error': str(e)}), 400
    
    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def handle_internal_error(e):
        return jsonify({'error': 'Internal server error'}), 500


def setup_jwt_callbacks(app):
    """Configuration des callbacks JWT"""
    from flask_jwt_extended import get_jwt
    from app.services.token_service import TokenService

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
       jti = jwt_payload['jti']
       return TokenService.is_token_blacklisted(jti)
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token'}), 401
