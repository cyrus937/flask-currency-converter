# app/services/rate_fetcher_service.py
from decimal import Decimal
from typing import List, Optional
from app.providers.fixer_provider import FixerProvider
from app.providers.ecb_provider import ECBProvider
from app.config.base import BaseConfig


class RateFetcherService:
    """Service de récupération des taux de change avec fallback"""
    
    def __init__(self):
        self.providers = self._initialize_providers()
        self.last_successful_provider = None
    
    def _initialize_providers(self) -> List:
        """Initialise les providers avec ordre de priorité"""
        providers = []
        
        # Provider Fixer.io (si clé API disponible)
        if BaseConfig.FIXER_API_KEY:
            providers.append(FixerProvider(BaseConfig.FIXER_API_KEY))
        
        # Provider ECB (gratuit, toujours disponible)
        providers.append(ECBProvider())
        
        return providers
    
    def fetch_rate(self, from_currency: str, to_currency: str) -> Decimal:
        """Récupère un taux avec fallback entre providers"""
        
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        last_error = None
        
        for provider in self.providers:
            try:
                if provider.is_available():
                    rate = provider.fetch_rate(from_currency, to_currency)
                    self.last_successful_provider = provider.name
                    return rate
            except Exception as e:
                last_error = e
                continue
        
        # Aucun provider n'a fonctionné
        raise Exception(f"Impossible de récupérer le taux {from_currency}/{to_currency}. Dernière erreur: {last_error}")
    
    def fetch_rates(self, base_currency: str = 'USD') -> dict:
        """Récupère tous les taux pour une devise de base"""
        
        base_currency = base_currency.upper()
        
        for provider in self.providers:
            try:
                if provider.is_available():
                    rates = provider.fetch_rates(base_currency)
                    self.last_successful_provider = provider.name
                    return rates
            except Exception:
                continue
        
        raise Exception(f"Impossible de récupérer les taux pour {base_currency}")
    
    def get_available_providers(self) -> List[str]:
        """Retourne la liste des providers disponibles"""
        available = []
        for provider in self.providers:
            if provider.is_available():
                available.append(provider.name)
        return available
    
    def get_supported_currencies(self) -> List[str]:
        """Retourne toutes les devises supportées par au moins un provider"""
        all_currencies = set()
        
        for provider in self.providers:
            try:
                if provider.is_available():
                    currencies = provider.get_supported_currencies()
                    all_currencies.update(currencies)
            except Exception:
                continue
        
        return sorted(list(all_currencies))
    
    def test_providers(self) -> dict:
        """Teste tous les providers et retourne leur statut"""
        results = {}
        
        for provider in self.providers:
            try:
                is_available = provider.is_available()
                if is_available:
                    # Test avec une conversion simple
                    test_rate = provider.fetch_rate('USD', 'EUR')
                    results[provider.name] = {
                        'available': True,
                        'test_rate_usd_eur': float(test_rate),
                        'error': None
                    }
                else:
                    results[provider.name] = {
                        'available': False,
                        'error': 'Provider non disponible'
                    }
            except Exception as e:
                results[provider.name] = {
                    'available': False,
                    'error': str(e)
                }
        
        return results