# app/services/conversion_service.py
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Dict
from flask import request
from app.models.conversion import Conversion
from app.models.exchange_rate import ExchangeRate
from app.services.rate_fetcher_service import RateFetcherService
from app.services.cache_service import CacheService
from app.utils.exceptions import CurrencyError, ValidationError


class ConversionService:
    """Service de conversion de devises"""
    
    def __init__(self):
        self.rate_fetcher = RateFetcherService()
        self.cache = CacheService()
    
    def convert(self, amount, from_currency, to_currency, user_id=None):
        """Convertit un montant d'une devise à une autre"""
        
        # Validation
        self._validate_conversion_params(amount, from_currency, to_currency)
        
        # Conversion du montant en Decimal pour la précision
        amount = Decimal(str(amount))
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        # Si même devise, pas de conversion
        if from_currency == to_currency:
            return self._build_same_currency_response(amount, from_currency)
        
        # Récupérer le taux de change
        rate_data = self._get_exchange_rate(from_currency, to_currency)
        
        # Calculer la conversion
        gross_amount = self._calculate_conversion(amount, rate_data['rate'])
        
        # Appliquer les frais
        fee_data = self._calculate_fees(gross_amount, user_id)
        net_amount = gross_amount - fee_data['fee_amount']
        
        # Sauvegarder l'historique
        conversion = self._save_conversion_history(
            amount=amount,
            from_currency=from_currency,
            to_currency=to_currency,
            converted_amount=net_amount,
            exchange_rate=rate_data['rate'],
            fee_amount=fee_data['fee_amount'],
            fee_rate=fee_data['fee_rate'],
            provider=rate_data['provider'],
            user_id=user_id
        )
        
        return self._build_conversion_response(
            original_amount=amount,
            converted_amount=net_amount,
            gross_amount=gross_amount,
            exchange_rate=rate_data['rate'],
            from_currency=from_currency,
            to_currency=to_currency,
            fee_data=fee_data,
            provider=rate_data['provider'],
            conversion_id=conversion.id
        )
    
    def get_user_conversion_history(self, user_id, limit=50):
        """Récupère l'historique des conversions d'un utilisateur"""
        conversions = Conversion.get_user_history(user_id, limit)
        return [conv.to_dict() for conv in conversions]
    
    def get_popular_conversion_pairs(self, days=30):
        """Récupère les paires de conversion les plus populaires"""
        return Conversion.get_popular_pairs(days)
    
    def _validate_conversion_params(self, amount, from_currency, to_currency):
        """Valide les paramètres de conversion"""
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValidationError("Le montant doit être positif")
            if amount > 1000000000:  # 1 milliard max
                raise ValidationError("Montant trop élevé")
        except (ValueError, TypeError):
            raise ValidationError("Montant invalide")
        
        if not from_currency or not to_currency:
            raise ValidationError("Devises source et destination requises")
        
        if len(from_currency) != 3 or len(to_currency) != 3:
            raise ValidationError("Codes de devise invalides")
    
    def _get_exchange_rate(self, from_currency, to_currency):
        """Récupère le taux de change avec cache et fallback"""
        cache_key = f"rate:{from_currency}:{to_currency}"
        
        # Tentative depuis le cache
        cached_rate = self.cache.get_rate(cache_key)
        if cached_rate:
            return {
                'rate': Decimal(str(cached_rate['rate'])),
                'provider': cached_rate['provider']
            }
        
        # Tentative depuis la base de données
        db_rate = ExchangeRate.get_latest_rate(from_currency, to_currency)
        if db_rate and not db_rate.is_stale(minutes=10):
            rate_data = {
                'rate': db_rate.rate,
                'provider': db_rate.provider
            }
            self.cache.set_rate(cache_key, rate_data, timeout=300)
            return rate_data
        
        # Récupération depuis les providers externes
        try:
            rate = self.rate_fetcher.fetch_rate(from_currency, to_currency)
            provider = self.rate_fetcher.last_successful_provider
            
            # Sauvegarder en base
            ExchangeRate.update_or_create(from_currency, to_currency, rate, provider)
            
            rate_data = {
                'rate': Decimal(str(rate)),
                'provider': provider
            }
            self.cache.set_rate(cache_key, rate_data, timeout=300)
            
            return rate_data
            
        except Exception as e:
            raise CurrencyError(f"Impossible de récupérer le taux {from_currency}/{to_currency}: {str(e)}")
    
    def _calculate_conversion(self, amount, rate):
        """Calcule la conversion avec précision"""
        return (amount * rate).quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
    
    def _calculate_fees(self, amount, user_id=None):
        """Calcule les frais de conversion"""
        from app.models.user import User
        from app.config.base import BaseConfig
        
        fee_rate = Decimal(str(BaseConfig.CONVERSION_FEE_RATE))
        
        # Frais réduits pour les utilisateurs premium
        if user_id:
            user = User.query.get(user_id)
            if user and user.is_premium:
                fee_rate = fee_rate * Decimal('0.5')  # 50% de réduction
        
        fee_amount = (amount * fee_rate).quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
        
        return {
            'fee_rate': fee_rate,
            'fee_amount': fee_amount
        }
    
    def _save_conversion_history(self, **kwargs):
        """Sauvegarde la conversion dans l'historique"""
        conversion = Conversion(
            user_id=kwargs.get('user_id'),
            from_currency=kwargs['from_currency'],
            to_currency=kwargs['to_currency'],
            original_amount=kwargs['amount'],
            converted_amount=kwargs['converted_amount'],
            exchange_rate=kwargs['exchange_rate'],
            fee_amount=kwargs['fee_amount'],
            fee_rate=kwargs['fee_rate'],
            provider=kwargs['provider'],
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent') if request else None
        )
        
        return conversion.save()
    
    def _build_same_currency_response(self, amount, currency):
        """Construit la réponse pour une conversion de même devise"""
        return {
            'original_amount': float(amount),
            'converted_amount': float(amount),
            'gross_amount': float(amount),
            'net_amount': float(amount),
            'exchange_rate': 1.0,
            'from_currency': currency,
            'to_currency': currency,
            'fee_amount': 0.0,
            'fee_rate': 0.0,
            'provider': 'system',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _build_conversion_response(self, **kwargs):
        """Construit la réponse de conversion"""
        return {
            'conversion_id': kwargs['conversion_id'],
            'original_amount': float(kwargs['original_amount']),
            'gross_amount': float(kwargs['gross_amount']),
            'converted_amount': float(kwargs['converted_amount']),
            'net_amount': float(kwargs['converted_amount']),
            'exchange_rate': float(kwargs['exchange_rate']),
            'from_currency': kwargs['from_currency'],
            'to_currency': kwargs['to_currency'],
            'fee_amount': float(kwargs['fee_data']['fee_amount']),
            'fee_rate': float(kwargs['fee_data']['fee_rate']),
            'provider': kwargs['provider'],
            'timestamp': datetime.utcnow().isoformat()
        }
