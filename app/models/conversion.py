# app/models/conversion.py
from decimal import Decimal
from app.extensions import db
from app.models.base import BaseModel


class Conversion(BaseModel):
    """Modèle historique des conversions"""
    __tablename__ = 'conversions'
    
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)  # Null pour utilisateurs anonymes
    from_currency = db.Column(db.String(3), nullable=False, index=True)
    to_currency = db.Column(db.String(3), nullable=False, index=True)
    original_amount = db.Column(db.Numeric(precision=20, scale=8), nullable=False)
    converted_amount = db.Column(db.Numeric(precision=20, scale=8), nullable=False)
    exchange_rate = db.Column(db.Numeric(precision=20, scale=8), nullable=False)
    fee_amount = db.Column(db.Numeric(precision=20, scale=8), default=0)
    fee_rate = db.Column(db.Numeric(precision=5, scale=4), default=0)  # 0.0100 = 1%
    provider = db.Column(db.String(50))
    ip_address = db.Column(db.String(45))  # Pour tracking anonyme
    user_agent = db.Column(db.Text)
    
    # Index pour optimiser les requêtes
    __table_args__ = (
        db.Index('idx_user_conversions', 'user_id', 'created_at'),
        db.Index('idx_currency_pair_conversions', 'from_currency', 'to_currency'),
        db.Index('idx_conversion_date', 'created_at'),
    )
    
    def __init__(self, from_currency, to_currency, original_amount, 
                 converted_amount, exchange_rate, **kwargs):
        super().__init__(**kwargs)
        self.from_currency = from_currency.upper()
        self.to_currency = to_currency.upper()
        self.original_amount = Decimal(str(original_amount))
        self.converted_amount = Decimal(str(converted_amount))
        self.exchange_rate = Decimal(str(exchange_rate))
        
        # Calcul automatique des frais si non fournis
        if 'fee_amount' in kwargs:
            self.fee_amount = Decimal(str(kwargs['fee_amount']))
        if 'fee_rate' in kwargs:
            self.fee_rate = Decimal(str(kwargs['fee_rate']))
    
    @property
    def net_amount(self):
        """Montant net après déduction des frais"""
        return self.converted_amount - self.fee_amount
    
    @classmethod
    def get_user_history(cls, user_id, limit=50):
        """Récupère l'historique des conversions d'un utilisateur"""
        return cls.query.filter_by(user_id=user_id)\
                       .order_by(cls.created_at.desc())\
                       .limit(limit).all()
    
    @classmethod
    def get_popular_pairs(cls, days=30):
        """Récupère les paires de devises les plus converties"""
        from datetime import datetime, timedelta
        from sqlalchemy import func
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        result = db.session.query(
            cls.from_currency,
            cls.to_currency,
            func.count().label('conversion_count'),
            func.sum(cls.original_amount).label('total_volume')
        ).filter(
            cls.created_at >= start_date
        ).group_by(
            cls.from_currency, 
            cls.to_currency
        ).order_by(
            func.count().desc()
        ).limit(10).all()
        
        return result
    
    @classmethod
    def get_volume_stats(cls, currency_code=None, days=30):
        """Statistiques de volume pour une devise"""
        from datetime import datetime, timedelta
        from sqlalchemy import func, or_
        
        start_date = datetime.utcnow() - timedelta(days=days)
        query = cls.query.filter(cls.created_at >= start_date)
        
        if currency_code:
            currency_code = currency_code.upper()
            query = query.filter(
                or_(cls.from_currency == currency_code, 
                    cls.to_currency == currency_code)
            )
        
        stats = query.with_entities(
            func.count().label('total_conversions'),
            func.sum(cls.original_amount).label('total_volume'),
            func.avg(cls.original_amount).label('avg_amount')
        ).first()
        
        return {
            'total_conversions': stats.total_conversions or 0,
            'total_volume': float(stats.total_volume or 0),
            'average_amount': float(stats.avg_amount or 0)
        }
    
    def to_dict(self):
        """Convertit en dictionnaire"""
        return {
            'id': self.id,
            'from_currency': self.from_currency,
            'to_currency': self.to_currency,
            'original_amount': float(self.original_amount),
            'converted_amount': float(self.converted_amount),
            'net_amount': float(self.net_amount),
            'exchange_rate': float(self.exchange_rate),
            'fee_amount': float(self.fee_amount),
            'fee_rate': float(self.fee_rate),
            'provider': self.provider,
            'timestamp': self.created_at.isoformat()
        }
