# app/services/token_service.py
from flask_jwt_extended import decode_token, get_jti
from app.extensions import cache
from app.models.refresh_token import RefreshToken
# import redis


class TokenService:
    """Service de gestion des tokens JWT"""
    
    @staticmethod
    def get_jti_from_token(encoded_token):
        """Extrait le JTI d'un token encodé"""
        try:
            decoded_token = decode_token(encoded_token)
            return decoded_token['jti']
        except Exception:
            return None
    
    @staticmethod
    def blacklist_token(jti, expires_in_seconds):
        """Ajoute un token à la blacklist"""
        cache.set(f"blacklist:{jti}", "true", timeout=expires_in_seconds)
    
    @staticmethod
    def is_token_blacklisted(jti):
        """Vérifie si un token est blacklisté"""
        return cache.get(f"blacklist:{jti}") is not None
    
    @staticmethod
    def revoke_refresh_token(jti):
        """Révoque un refresh token"""
        refresh_token = RefreshToken.find_by_jti(jti)
        if refresh_token:
            refresh_token.revoke()
        return refresh_token is not None
