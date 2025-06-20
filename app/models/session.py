# app/models/session.py
from datetime import datetime, timedelta
from app.extensions import db
from app.models.base import BaseModel


class Session(BaseModel):
    """Modèle de session utilisateur"""
    __tablename__ = 'sessions'
    
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    ip_address = db.Column(db.String(45))  # IPv6 compatible
    user_agent = db.Column(db.Text)
    device_type = db.Column(db.String(50))  # web, mobile, desktop
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user_id, session_token, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.session_token = session_token
        self.set_expiration()
    
    def set_expiration(self):
        """Définit la date d'expiration de la session"""
        from app.config.base import BaseConfig
        self.expires_at = datetime.utcnow() + BaseConfig.SESSION_TIMEOUT
    
    def is_expired(self):
        """Vérifie si la session est expirée"""
        return datetime.utcnow() > self.expires_at
    
    def refresh_activity(self):
        """Met à jour l'activité de la session"""
        self.last_activity = datetime.utcnow()
        db.session.commit()
    
    def deactivate(self):
        """Désactive la session"""
        self.is_active = False
        db.session.commit()
    
    @classmethod
    def find_active_session(cls, session_token):
        """Trouve une session active par token"""
        return cls.query.filter_by(
            session_token=session_token,
            is_active=True
        ).first()
    
    @classmethod
    def cleanup_expired_sessions(cls):
        """Nettoie les sessions expirées"""
        expired_sessions = cls.query.filter(
            cls.expires_at < datetime.utcnow()
        ).all()
        
        for session in expired_sessions:
            session.deactivate()
        
        return len(expired_sessions)
