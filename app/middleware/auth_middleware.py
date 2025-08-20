# app/middleware/auth_middleware.py
from functools import wraps
from flask import request, jsonify
from flask_smorest import abort
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from app.models.api_key import ApiKey
from app.utils.exceptions import AuthenticationError
import hashlib


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

def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("X-API-KEY")

        if api_key:
            # Vérification API key
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            record: ApiKey = ApiKey.query.filter_by(key_hash=key_hash, active=True).first()
            if not record:
                return abort(403, message='API key invalide')
            # Optionnel : tu peux attacher l’info de l’app externe dans request
            request.user_id = record.owner_id
            return fn(*args, **kwargs)

        else:
            # Vérification JWT
            try:
                verify_jwt_in_request()
            except Exception as e:
                return abort(401, message="Missing or invalid token")
            identity = get_jwt_identity()
            request.user_id = identity
            return fn(*args, **kwargs)

    return wrapper