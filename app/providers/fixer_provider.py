# app/providers/fixer_provider.py
from decimal import Decimal
from typing import Dict
from app.providers.base_provider import BaseProvider


class FixerProvider(BaseProvider):
    """Provider pour Fixer.io API"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "http://data.fixer.io/api"
        self.name = "Fixer.io"
        self.rate_limit = 1000  # 1000 requêtes/mois pour le plan gratuit
    
    def fetch_rate(self, from_currency: str, to_currency: str) -> Decimal:
        """Récupère un taux de change spécifique"""
        if not self.is_available():
            raise Exception("Provider Fixer.io non disponible")
        
        # Fixer utilise EUR comme base, donc on doit adapter
        if from_currency == 'EUR':
            # EUR vers autre devise
            rates = self.fetch_rates('EUR')
            if to_currency not in rates:
                raise Exception(f"Devise {to_currency} non supportée")
            return rates[to_currency]
        
        elif to_currency == 'EUR':
            # Autre devise vers EUR
            rates = self.fetch_rates('EUR')
            if from_currency not in rates:
                raise Exception(f"Devise {from_currency} non supportée")
            return Decimal('1') / rates[from_currency]
        
        else:
            # Conversion via EUR
            rates = self.fetch_rates('EUR')
            if from_currency not in rates or to_currency not in rates:
                raise Exception(f"Paire {from_currency}/{to_currency} non supportée")
            
            eur_to_from = rates[from_currency]
            eur_to_to = rates[to_currency]
            
            # Taux croisé: (1/EUR_FROM) * EUR_TO
            return eur_to_to / eur_to_from
    
    def fetch_rates(self, base_currency: str = 'EUR') -> Dict[str, Decimal]:
        """Récupère tous les taux pour une devise de base"""
        if base_currency != 'EUR':
            raise Exception("Fixer.io supporte uniquement EUR comme devise de base")
        
        url = f"{self.base_url}/latest"
        params = {
            'access_key': self.api_key,
            'base': base_currency
        }
        
        data = self._make_request(url, params)
        
        if not data.get('success', False):
            error = data.get('error', {})
            raise Exception(f"Erreur Fixer: {error.get('info', 'Erreur inconnue')}")
        
        rates = {}
        for currency, rate in data.get('rates', {}).items():
            rates[currency] = self._convert_to_decimal(rate)
        
        return rates
    
    def is_available(self) -> bool:
        """Vérifie si le provider est disponible"""
        if not self.api_key:
            return False
        
        try:
            url = f"{self.base_url}/latest"
            params = {
                'access_key': self.api_key,
                'base': 'EUR',
                'symbols': 'USD'  # Test avec une seule devise
            }
            
            data = self._make_request(url, params)
            return data.get('success', False)
        
        except Exception:
            return False
    
    def get_supported_currencies(self) -> list:
        """Retourne la liste des devises supportées"""
        try:
            url = f"{self.base_url}/symbols"
            params = {'access_key': self.api_key}
            
            data = self._make_request(url, params)
            
            if data.get('success', False):
                return list(data.get('symbols', {}).keys())
        
        except Exception:
            pass
        
        # Fallback avec les devises principales
        return [
            'USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD',
            'SEK', 'NOK', 'DKK', 'PLN', 'CZK', 'HUF', 'RUB', 'CNY',
            'INR', 'BRL', 'ZAR', 'KRW', 'SGD', 'HKD', 'MXN', 'TRY'
        ]
