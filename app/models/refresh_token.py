# app/models/refresh_token.py
from datetime import datetime, timedelta
from app.extensions import db
from app.models.base import BaseModel
import secrets


class RefreshToken(BaseModel):
    """Modèle de refresh token"""
    __tablename__ = 'refresh_tokens'
    
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(36), db.ForeignKey('sessions.id'), nullable=False)
    token_hash = db.Column(db.String(255), unique=True, nullable=False, index=True)
    jti = db.Column(db.String(36), unique=True, nullable=False, index=True)  # JWT ID
    is_revoked = db.Column(db.Boolean, default=False, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    # Relations
    session = db.relationship('Session', backref='refresh_tokens')
    
    def __init__(self, user_id, session_id, jti, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.session_id = session_id
        self.jti = jti
        self.generate_token()
        self.set_expiration()
    
    def generate_token(self):
        """Génère un token sécurisé"""
        token = secrets.token_urlsafe(32)
        self.token_hash = token  # En production, hasher le token
    
    def set_expiration(self):
        """Définit la date d'expiration"""
        from app.config.base import BaseConfig
        self.expires_at = datetime.utcnow() + BaseConfig.JWT_REFRESH_TOKEN_EXPIRES
    
    def is_expired(self):
        """Vérifie si le token est expiré"""
        return datetime.utcnow() > self.expires_at
    
    def revoke(self):
        """Révoque le token"""
        self.is_revoked = True
        db.session.commit()
    
    def is_valid(self):
        """Vérifie si le token est valide"""
        return not self.is_revoked and not self.is_expired()
    
    @classmethod
    def find_by_jti(cls, jti):
        """Trouve un token par son JTI"""
        return cls.query.filter_by(jti=jti).first()
    
    @classmethod
    def cleanup_expired_tokens(cls):
        """Nettoie les tokens expirés"""
        expired_tokens = cls.query.filter(
            cls.expires_at < datetime.utcnow()
        ).all()
        
        for token in expired_tokens:
            token.delete()
        
        return len(expired_tokens)