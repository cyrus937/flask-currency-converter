# app/services/cache_service.py
from app.extensions import cache
import json


class CacheService:
    """Service de gestion du cache Redis"""
    
    @staticmethod
    def get_rate(cache_key):
        """Récupère un taux depuis le cache"""
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return json.loads(cached_data) if isinstance(cached_data, str) else cached_data
        except Exception:
            pass
        return None
    
    @staticmethod
    def set_rate(cache_key, rate_data, timeout=300):
        """Sauvegarde un taux dans le cache"""
        try:
            # Convertir les Decimal en float pour la sérialisation JSON
            serializable_data = {
                'rate': float(rate_data['rate']),
                'provider': rate_data['provider']
            }
            cache.set(cache_key, json.dumps(serializable_data), timeout=timeout)
        except Exception as e:
            print(f"Erreur cache: {e}")
    
    @staticmethod
    def invalidate_rate(from_currency, to_currency):
        """Invalide le cache pour une paire de devises"""
        cache_key = f"rate:{from_currency}:{to_currency}"
        cache.delete(cache_key)
    
    @staticmethod
    def get_user_favorites(user_id):
        """Récupère les devises favorites depuis le cache"""
        cache_key = f"user_favorites:{user_id}"
        return cache.get(cache_key)
    
    @staticmethod
    def set_user_favorites(user_id, favorites, timeout=3600):
        """Sauvegarde les devises favorites dans le cache"""
        cache_key = f"user_favorites:{user_id}"
        cache.set(cache_key, favorites, timeout=timeout)
    
    @staticmethod
    def invalidate_user_favorites(user_id):
        """Invalide le cache des favoris utilisateur"""
        cache_key = f"user_favorites:{user_id}"
        cache.delete(cache_key)