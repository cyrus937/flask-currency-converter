from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Dict, List
import currencyapicom
import app
from app.config import BaseConfig
from app.extensions import db
from app.models.currency import Currency
from app.models.exchange_rate import ExchangeRate
from app.providers.base_provider import BaseProvider


class CurrencyAPIProvider(BaseProvider):
    def __init__(self):
        super().__init__(api_key=BaseConfig.CURRENCYAPI_API_KEY)
        self.name = "CurrencyAPI"
        self.client = currencyapicom.Client(api_key=self.api_key)
        

    def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        pass  # Not implemented in this provider
    
    def fetch_rate(self, from_currency: str, to_currency: str) -> Decimal:
        pass  # Not implemented in this provider
    
    def fetch_rates(self, base_currency: str = 'USD') -> Dict[str, Decimal]:
        """Récupère tous les taux pour une devise de base"""
        pass  # Not implemented in this provider
    
    def is_available(self) -> bool:
        """Vérifie si le provider est disponible"""
        return True

    def fetch_currencies(self) -> None:
        result = self.client.currencies()
        for key, value in result["data"].items():
            try:
                existing_currency = Currency.query.filter_by(code=key).first()
                if existing_currency:
                    # Update existing currency
                    existing_currency.name = value['name']
                    existing_currency.symbol = value['symbol']
                    existing_currency.symbol_native = value['symbol_native']
                    existing_currency.decimal_places = value['decimal_digits']
                    existing_currency.rounding = value['rounding']
                    existing_currency.name_plural = value['name_plural']
                    existing_currency.is_crypto = (value.get('type', 'fiat') == 'crypto')
                    countries = value.get('countries', [])
                    existing_currency.countries_code = ",".join(countries)
                else:
                    countries: List[str] = value.get('countries', [])
                    data = Currency(
                        symbol=value['symbol'],
                        name=value['name'],
                        symbol_native=value['symbol_native'],
                        decimal_places=value['decimal_digits'],
                        rounding=value['rounding'],
                        code=key,
                        name_plural=value['name_plural'],
                        # type=value.get('type', 'fiat'),
                        is_crypto=(value.get('type', 'fiat') == 'crypto'),
                        countries_code=",".join(countries)
                    )
                    db.session.add(data)
                    print(f"Added new currency: {key} - {value['name']}")

            except Exception as e:
                print(f"Error processing currency {key}: {e}")
                continue
            
        db.session.commit()
        print("Currency data fetched and updated successfully.")
        
    def fetch_exchange_rates(self) -> None:
        """Récupère les taux de change en utilisant le provider actuel."""
        result = self.client.latest()
        
        if not result or 'data' not in result:
            app.logger.error("No exchange rates data found.")
            return

        try:
            last_updated_provider = None if 'last_updated_at' not in result else result['meta']['last_updated_at']
            
            for key, value in result["data"].items():
                try:
                    new_rate = ExchangeRate(
                        from_currency="USD",
                        to_currency=value['code'],
                        rate=value['value'],
                        provider=self.name,
                        last_updated_provider=datetime.fromisoformat(last_updated_provider) if last_updated_provider else datetime.utcnow()
                    )
                    db.session.add(new_rate)
                except Exception as e:
                    print(f"Error processing exchange rate {key}: {e}")
                    continue

            db.session.commit()
            print("Exchange rates converted successfully.")
        except Exception as e:
            print(f"Error committing exchange rates: {e}")
            db.session.rollback()
