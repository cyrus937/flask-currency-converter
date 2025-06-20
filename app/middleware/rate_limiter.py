# app/middleware/rate_limiter.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request


def get_user_id():
    """Récupère l'ID utilisateur pour le rate limiting personnalisé"""
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        return user_id if user_id else get_remote_address()
    except:
        return get_remote_address()


# Configuration du rate limiter
limiter = Limiter(
    key_func=get_user_id,
    default_limits=["1000 per hour"],
    storage_uri="redis://localhost:6379/1"
)
