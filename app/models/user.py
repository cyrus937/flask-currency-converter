# app/models/user.py
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import datetime
from app.extensions import db
from app.models.base import BaseModel


class User(BaseModel):
    """Modèle utilisateur"""
    __tablename__ = 'users'
    
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    is_premium = db.Column(db.Boolean, default=False, nullable=False)
    last_login = db.Column(db.DateTime)
    
    # Préférences utilisateur pour les devises
    preferred_currency = db.Column(db.String(3), default='USD')
    
    # Relations
    sessions = db.relationship('Session', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    refresh_tokens = db.relationship('RefreshToken', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    conversions = db.relationship('Conversion', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    favorite_currencies = db.relationship('UserFavoriteCurrency', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, email, password, first_name, last_name, **kwargs):
        super().__init__(**kwargs)
        self.email = email.lower().strip()
        self.first_name = first_name
        self.last_name = last_name
        self.set_password(password)
    
    def set_password(self, password):
        """Hash et définit le mot de passe"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Vérifie le mot de passe"""
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        """Retourne le nom complet"""
        return f"{self.first_name} {self.last_name}"
    
    def update_last_login(self):
        """Met à jour la date de dernière connexion"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def generate_tokens(self, session_id):
        """Génère les tokens JWT pour l'utilisateur"""
        additional_claims = {
            'session_id': session_id,
            'email': self.email,
            'is_premium': self.is_premium
        }
        
        access_token = create_access_token(
            identity=self.id,
            additional_claims=additional_claims
        )
        refresh_token = create_refresh_token(
            identity=self.id,
            additional_claims=additional_claims
        )
        
        return access_token, refresh_token
    
    def get_active_sessions_count(self):
        """Retourne le nombre de sessions actives"""
        return self.sessions.filter_by(is_active=True).count()
    
    def can_create_session(self):
        """Vérifie si l'utilisateur peut créer une nouvelle session"""
        from app.config.base import BaseConfig
        return self.get_active_sessions_count() < BaseConfig.MAX_SESSIONS_PER_USER
    
    def add_favorite_currency(self, currency_code):
        """Ajoute une devise aux favoris"""
        from app.models.user_favorite_currency import UserFavoriteCurrency
        
        existing = UserFavoriteCurrency.query.filter_by(
            user_id=self.id, 
            currency_code=currency_code
        ).first()
        
        if not existing:
            favorite = UserFavoriteCurrency(
                user_id=self.id,
                currency_code=currency_code
            )
            favorite.save()
    
    def remove_favorite_currency(self, currency_code):
        """Supprime une devise des favoris"""
        from app.models.user_favorite_currency import UserFavoriteCurrency
        
        favorite = UserFavoriteCurrency.query.filter_by(
            user_id=self.id,
            currency_code=currency_code
        ).first()
        
        if favorite:
            favorite.delete()
    
    def get_favorite_currencies(self):
        """Retourne les devises favorites"""
        return [fav.currency_code for fav in self.favorite_currencies]
    
    @classmethod
    def find_by_email(cls, email):
        """Trouve un utilisateur par email"""
        return cls.query.filter_by(email=email.lower().strip()).first()
    
    @classmethod
    def create_user(cls, email, password, first_name, last_name):
        """Crée un nouvel utilisateur"""
        if cls.find_by_email(email):
            raise ValueError("Un utilisateur avec cet email existe déjà")
        
        user = cls(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        return user.save()
    
    def to_dict(self, include_sensitive=False):
        """Convertit en dictionnaire (sans données sensibles par défaut)"""
        data = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'is_premium': self.is_premium,
            'preferred_currency': self.preferred_currency,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_sensitive:
            data.update({
                'favorite_currencies': self.get_favorite_currencies(),
                'active_sessions': self.get_active_sessions_count()
            })
        
        return data
