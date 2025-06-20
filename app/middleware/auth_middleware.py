# app/middleware/auth_middleware.py
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from app.utils.exceptions import AuthenticationError


def token_required(f):
    """Décorateur pour exiger un token valide"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Token invalide ou manquant'}), 401
    return decorated


def optional_auth(f):
    """Décorateur pour authentification optionnelle"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
        except Exception:
            pass  # Ignorer les erreurs d'authentification
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Décorateur pour exiger les droits admin"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            
            if not claims.get('is_admin', False):
                return jsonify({'error': 'Droits administrateur requis'}), 403
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Token invalide ou manquant'}), 401
    return decorated
