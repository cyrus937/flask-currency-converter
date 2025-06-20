# app/models/exchange_rate.py
from datetime import datetime, timedelta
from decimal import Decimal
from app.extensions import db
from app.models.base import BaseModel


class ExchangeRate(BaseModel):
    """Modèle taux de change"""
    __tablename__ = 'exchange_rates'
    
    from_currency = db.Column(db.String(3), nullable=False, index=True)
    to_currency = db.Column(db.String(3), nullable=False, index=True)
    rate = db.Column(db.Numeric(precision=20, scale=8), nullable=False)  # Précision élevée
    provider = db.Column(db.String(50), nullable=False)  # fixer, ecb, etc.
    is_active = db.Column(db.Boolean, default=True)
    
    # Index composé pour optimiser les requêtes
    __table_args__ = (
        db.Index('idx_currency_pair', 'from_currency', 'to_currency'),
        db.Index('idx_rate_timestamp', 'created_at'),
    )
    
    def __init__(self, from_currency, to_currency, rate, provider, **kwargs):
        super().__init__(**kwargs)
        self.from_currency = from_currency.upper()
        self.to_currency = to_currency.upper()
        self.rate = Decimal(str(rate))
        self.provider = provider
    
    def is_stale(self, minutes=10):
        """Vérifie si le taux est obsolète"""
        threshold = datetime.utcnow() - timedelta(minutes=minutes)
        return self.created_at < threshold
    
    @classmethod
    def get_latest_rate(cls, from_currency, to_currency):
        """Récupère le taux le plus récent pour une paire"""
        return cls.query.filter_by(
            from_currency=from_currency.upper(),
            to_currency=to_currency.upper(),
            is_active=True
        ).order_by(cls.created_at.desc()).first()
    
    @classmethod
    def get_historical_rates(cls, from_currency, to_currency, days=30):
        """Récupère l'historique des taux"""
        start_date = datetime.utcnow() - timedelta(days=days)
        return cls.query.filter(
            cls.from_currency == from_currency.upper(),
            cls.to_currency == to_currency.upper(),
            cls.created_at >= start_date,
            cls.is_active == True
        ).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def update_or_create(cls, from_currency, to_currency, rate, provider='system'):
        """Met à jour ou crée un nouveau taux"""
        exchange_rate = cls(
            from_currency=from_currency,
            to_currency=to_currency,
            rate=rate,
            provider=provider
        )
        return exchange_rate.save()
    
    @classmethod
    def cleanup_old_rates(cls, days=365):
        """Nettoie les anciens taux"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        old_rates = cls.query.filter(cls.created_at < cutoff_date).all()
        
        for rate in old_rates:
            rate.delete()
        
        return len(old_rates)
    
    def to_dict(self):
        """Convertit en dictionnaire"""
        return {
            'id': self.id,
            'from_currency': self.from_currency,
            'to_currency': self.to_currency,
            'rate': float(self.rate),
            'provider': self.provider,
            'timestamp': self.created_at.isoformat()
        }
