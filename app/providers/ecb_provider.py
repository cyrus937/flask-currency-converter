# app/providers/ecb_provider.py
from decimal import Decimal
from typing import Dict
import xml.etree.ElementTree as ET
from app.providers.base_provider import BaseProvider


class ECBProvider(BaseProvider):
    """Provider pour la Banque Centrale Européenne (gratuit)"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.ecb.europa.eu/stats/eurofxref"
        self.name = "European Central Bank"
        self.rate_limit = float('inf')  # Pas de limite
    
    def fetch_rate(self, from_currency: str, to_currency: str) -> Decimal:
        """Récupère un taux de change spécifique"""
        if not self.is_available():
            raise Exception("Provider ECB non disponible")
        
        # ECB utilise EUR comme base
        if from_currency == 'EUR':
            rates = self.fetch_rates('EUR')
            if to_currency not in rates:
                raise Exception(f"Devise {to_currency} non supportée par ECB")
            return rates[to_currency]
        
        elif to_currency == 'EUR':
            rates = self.fetch_rates('EUR')
            if from_currency not in rates:
                raise Exception(f"Devise {from_currency} non supportée par ECB")
            return Decimal('1') / rates[from_currency]
        
        else:
            # Conversion via EUR
            rates = self.fetch_rates('EUR')
            if from_currency not in rates or to_currency not in rates:
                raise Exception(f"Paire {from_currency}/{to_currency} non supportée par ECB")
            
            eur_to_from = rates[from_currency]
            eur_to_to = rates[to_currency]
            
            return eur_to_to / eur_to_from
    
    def fetch_rates(self, base_currency: str = 'EUR') -> Dict[str, Decimal]:
        """Récupère tous les taux depuis ECB"""
        if base_currency != 'EUR':
            raise Exception("ECB supporte uniquement EUR comme devise de base")
        
        url = f"{self.base_url}/eurofxref-daily.xml"
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parser le XML
            root = ET.fromstring(response.content)
            
            rates = {'EUR': Decimal('1')}  # EUR = 1 par définition
            
            # Namespace ECB
            ns = {'ecb': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref'}
            
            # Trouver les taux
            for cube in root.findall('.//ecb:Cube[@currency]', ns):
                currency = cube.get('currency')
                rate = cube.get('rate')
                
                if currency and rate:
                    rates[currency] = self._convert_to_decimal(rate)
            
            return rates
        
        except ET.ParseError:
            raise Exception("Erreur lors du parsing des données ECB")
        except Exception as e:
            raise Exception(f"Erreur ECB: {str(e)}")
    
    def is_available(self) -> bool:
        """Vérifie si ECB est disponible"""
        try:
            url = f"{self.base_url}/eurofxref-daily.xml"
            response = self.session.get(url, timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_supported_currencies(self) -> list:
        """Retourne la liste des devises supportées par ECB"""
        try:
            rates = self.fetch_rates('EUR')
            return list(rates.keys())
        except Exception:
            # Fallback avec les devises ECB typiques
            return [
                'EUR', 'USD', 'JPY', 'BGN', 'CZK', 'DKK', 'GBP', 'HUF',
                'PLN', 'RON', 'SEK', 'CHF', 'ISK', 'NOK', 'HRK', 'RUB',
                'TRY', 'AUD', 'BRL', 'CAD', 'CNY', 'HKD', 'IDR', 'ILS',
                'INR', 'KRW', 'MXN', 'MYR', 'NZD', 'PHP', 'SGD', 'THB', 'ZAR'
            ]
