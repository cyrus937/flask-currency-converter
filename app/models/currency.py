# app/models/currency.py
from app.extensions import db
from app.models.base import BaseModel


class Currency(BaseModel):
    """Modèle devise"""
    __tablename__ = 'currencies'
    
    code = db.Column(db.String(3), unique=True, nullable=False, index=True)  # USD, EUR, etc.
    name = db.Column(db.String(100), nullable=False)  # US Dollar, Euro, etc.
    symbol = db.Column(db.String(10))  # $, €, etc.
    decimal_places = db.Column(db.Integer, default=2)  # Nombre de décimales
    is_active = db.Column(db.Boolean, default=True)
    is_crypto = db.Column(db.Boolean, default=False)
    country_code = db.Column(db.String(2))  # ISO country code
    
    def __init__(self, code, name, symbol=None, **kwargs):
        super().__init__(**kwargs)
        self.code = code.upper()
        self.name = name
        self.symbol = symbol
    
    @classmethod
    def get_active_currencies(cls):
        """Retourne toutes les devises actives"""
        return cls.query.filter_by(is_active=True).all()
    
    @classmethod
    def find_by_code(cls, code):
        """Trouve une devise par son code"""
        return cls.query.filter_by(code=code.upper()).first()
    
    @classmethod
    def get_popular_currencies(cls):
        """Retourne les devises les plus populaires"""
        popular_codes = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'BTC', 'ETH']
        return cls.query.filter(cls.code.in_(popular_codes), cls.is_active == True).all()
    
    def to_dict(self):
        """Convertit en dictionnaire"""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'symbol': self.symbol,
            'decimal_places': self.decimal_places,
            'is_crypto': self.is_crypto,
            'country_code': self.country_code
        }
