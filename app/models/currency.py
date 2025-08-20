# app/models/currency.py
from app.extensions import db
from app.models.base import BaseModel


class Currency(BaseModel):
    """Modèle devise"""
    __tablename__ = 'currencies'
    
    code = db.Column(db.String(30), unique=True, nullable=False, index=True)  # USD, EUR, etc.
    name = db.Column(db.String(100), nullable=False)  # US Dollar, Euro, etc.
    symbol = db.Column(db.String(100), nullable=True) 
    symbol_native = db.Column(db.String(10))  # $, €, etc.
    decimal_places = db.Column(db.Integer, default=2)  # Nombre de décimales
    rounding = db.Column(db.Float, default=0.0)  # Rounding value
    name_plural = db.Column(db.String(100), default="")  # Nom pluriel
    is_active = db.Column(db.Boolean, default=True)
    is_crypto = db.Column(db.Boolean, default=False)
    countries_code = db.Column(db.String(200), default="")  # ISO country code


    def __init__(self, code, name, symbol_native=None, **kwargs):
        super().__init__(**kwargs)
        self.code = code.upper()
        self.name = name
        self.symbol_native = symbol_native

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
        popular_codes = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'BTC', 'ETH', 'XOF']
        return cls.query.filter(cls.code.in_(popular_codes), cls.is_active == True).all()
    
    def to_dict(self):
        """Convertit en dictionnaire"""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'symbol': self.symbol_native,
            'decimal_places': self.decimal_places,
            'is_crypto': self.is_crypto,
            'countries_code': self.countries_code
        }
