# app/__init__.py
from flask import Flask, jsonify
from app.extensions import db, jwt, limiter, cache, mail, migrate, api, cors
from app.config import get_config


def create_app(config_name='development'):
    """Factory pattern pour créer l'application Flask"""
    app = Flask(__name__)
    
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


def register_blueprints(app):
    """Enregistre tous les blueprints"""
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    from app.routes.currencies import currencies_bp
    from app.routes.conversions import conversions_bp
    from app.routes.dashboard import dashboard_bp

    api.register_blueprint(auth_bp)
    api.register_blueprint(user_bp)
    api.register_blueprint(currencies_bp)
    api.register_blueprint(conversions_bp)

    app.register_blueprint(dashboard_bp)


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
