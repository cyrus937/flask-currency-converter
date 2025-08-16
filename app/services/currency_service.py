from app.models.conversion import Conversion
from app.models.currency import Currency
from app.services.cache_service import CacheService
from app.services.conversion_service import ConversionService
from app.utils.exceptions import ValidationError
from collections import Counter


class CurrencyService:
    """Service de gestion des devises"""

    def __init__(self):
        self.conversion_service = ConversionService()
        self.cache = CacheService()

    def get_supported_currencies(self):
        """Récupère la liste des devises supportées"""
        return [curr.to_dict() for curr in Currency.get_active_currencies()]

    def is_valid_currency(self, currency):
        """Vérifie si une devise est valide"""
        return currency in [curr.code for curr in Currency.get_active_currencies()]
    
    def get_popular_currencies(self):
        """Récupère les devises les plus populaires"""
        codes = Conversion.get_popular_currencies()
        
        res = self._get_popular_currencies_from_cache()
        if res:
            return res
        
        currencies = []
        
        for code in codes:
            currency = Currency.find_by_code(code)
            if currency:
                currencies.append(currency.to_dict())
        
        # Enregistre les devises populaires dans le cache
        cache_key = 'currency:popular_currencies'
        self.cache.set_popular_currencies(cache_key, currencies)
                
        return currencies
    
    def get_latest_rates(self, base_currency='USD', symbols=None):
        """Récupère les taux de change actuels pour une devise de base"""
        if not self.is_valid_currency(base_currency):
            raise ValidationError(f"Devise de base invalide: {base_currency}")
        
        if symbols:
            for symbol in symbols:
                if not self.is_valid_currency(symbol):
                    raise ValidationError(f"Devise cible invalide: {symbol}")
        
        
        # Filtrer les taux si des symboles sont spécifiés
        if symbols:
            rates = {k: v for k, v in rates.items() if k in symbols}
        
        return rates
    
    def _get_popular_currencies_from_cache(self):
        """Récupère les devises populaires depuis le cache"""
        cache_key = 'currency:popular_currencies'
        cached_data = self.cache.get_popular_currencies(cache_key)
        if cached_data:
            return cached_data
        
        return None